import asyncio
import zipfile
from pathlib import Path

from aiohttp import ClientSession, CookieJar

# Query parameters for the export endpoint. time_set, date_range, and route_id
# are study-specific selections; the rest control the report contents.
DEFAULT_EXPORT_PARAMS = {
    "time_set": "2",
    "date_range": "1",
    "mode": "congestion",
    "percentile": "90",
    "percentages": "5",
    "value": "average",
    "sample_size_threshold": "0",
    "frcs": "0",
    "street_names": "all",
    "selection": "route",
    "route_id": "1",
    "export_type": "csv",
    "apply_offset": "true",
}


async def trigger_export(
    study_id: int, auth_cookies: CookieJar, export_params: dict | None = None
) -> str:
    """
    Starts a server-side export job for the study and returns its task_id.
    """
    params = {**DEFAULT_EXPORT_PARAMS, **(export_params or {})}
    request_url = f"https://inode.app/api/road_analytics/traffic_stats/{study_id}/export/"

    async with ClientSession(cookie_jar=auth_cookies) as session:
        async with session.get(request_url, params=params) as response:
            json_response = await response.json()

    task_id = json_response.get("task_id")
    if not task_id:
        raise Exception(
            f"Export trigger for study {study_id} returned no task_id: {json_response}"
        )
    return task_id


async def wait_for_export(
    study_id: int,
    task_id: str,
    auth_cookies: CookieJar,
    poll_interval_seconds: float = 2.0,
    timeout_seconds: float = 300.0,
) -> str:
    """
    Polls the export status endpoint until the job succeeds, then returns the
    export's file name.
    """
    request_url = (
        f"https://inode.app/api/road_analytics/traffic_stats/{study_id}/check_export_status/"
    )
    elapsed = 0.0

    async with ClientSession(cookie_jar=auth_cookies) as session:
        while True:
            async with session.get(request_url, params={"task_id": task_id}) as response:
                json_response = await response.json()

            status = json_response.get("status")
            if status == "SUCCESS":
                return json_response["file_name"]
            if status != "PENDING":
                raise Exception(
                    f"Export for study {study_id} ended with status {status}: {json_response}"
                )

            if elapsed >= timeout_seconds:
                raise TimeoutError(
                    f"Export for study {study_id} still {status} after {timeout_seconds}s"
                )
            await asyncio.sleep(poll_interval_seconds)
            elapsed += poll_interval_seconds


async def download_export(
    study_id: int,
    task_id: str,
    file_name: str,
    auth_cookies: CookieJar,
    save_dir: Path,
) -> Path:
    """
    Downloads the finished export (a zip containing the csv), saves it under
    save_dir, extracts its contents next to it, and returns the zip's path.
    """
    request_url = (
        f"https://inode.app/api/road_analytics/traffic_stats/{study_id}/export_download/"
    )
    save_dir.mkdir(parents=True, exist_ok=True)
    zip_path = save_dir / file_name

    async with ClientSession(cookie_jar=auth_cookies) as session:
        async with session.get(request_url, params={"task_id": task_id}) as response:
            if response.status != 200:
                raise Exception(
                    f"Download for study {study_id} failed with status {response.status}"
                )
            zip_path.write_bytes(await response.read())

    if zipfile.is_zipfile(zip_path):
        with zipfile.ZipFile(zip_path) as archive:
            archive.extractall(save_dir)

    return zip_path
