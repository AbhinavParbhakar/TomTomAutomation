import asyncio
import zipfile
from pathlib import Path

from aiohttp import ClientSession

from constants import INODE_API_BASE

INTERNAL_API_BASE = "https://inode.app/api/road_analytics"


async def download_study_csv(
    study_id: int,
    auth_headers: dict,
    save_dir: Path,
    selection: str = "route",
) -> Path:
    """
    Downloads the study's csv results (a zip), saves it under save_dir,
    extracts its contents next to it, and returns the zip's path.

    selection is "route" for route-level rows or "segment" for segment-level.
    """
    request_url = f"{INODE_API_BASE}/ts/{study_id}/results/"
    params = {"export_format": "csv", "selection": selection}

    async with ClientSession(headers=auth_headers) as session:
        async with session.get(request_url, params=params) as response:
            if response.status != 200:
                raise Exception(
                    f"Results download for study {study_id} failed with status "
                    f"{response.status}: {await response.text()}"
                )
            file_name = (
                response.content_disposition.filename
                if response.content_disposition and response.content_disposition.filename
                else f"study_{study_id}_results.zip"
            )
            content = await response.read()

    save_dir.mkdir(parents=True, exist_ok=True)
    zip_path = save_dir / file_name
    zip_path.write_bytes(content)

    if zipfile.is_zipfile(zip_path):
        with zipfile.ZipFile(zip_path) as archive:
            archive.extractall(save_dir)

    return zip_path


async def download_segment_csv(
    study_id: int,
    time_set_id: int,
    date_range_id: int,
    auth_headers: dict,
    save_dir: Path,
    poll_interval_seconds: float = 3.0,
    timeout_seconds: float = 600.0,
) -> Path:
    """
    Downloads the segment-level csv via the platform's async export flow
    (trigger /export/, poll /check_export_status/, fetch /export_download/).

    The v1 results endpoint caps downloads at 20,000 rows, which segment-level
    reports exceed, so this uses the internal export the dashboard itself
    relies on. time_set_id and date_range_id must be valid @ids from the
    study's detail response (the export still contains all time sets and date
    ranges regardless).
    """
    export_params = {
        "time_set": str(time_set_id),
        "date_range": str(date_range_id),
        "mode": "congestion",
        "percentile": "90",
        "percentages": "5",
        "value": "average",
        "sample_size_threshold": "0",
        "frcs": "0",
        "street_names": "all",
        "selection": "segment",
        "export_type": "csv",
        "apply_offset": "true",
    }
    base_url = f"{INTERNAL_API_BASE}/traffic_stats/{study_id}"

    async with ClientSession(headers=auth_headers) as session:
        async with session.get(f"{base_url}/export/", params=export_params) as response:
            trigger_json = await response.json()
        task_id = trigger_json.get("task_id")
        if not task_id:
            raise Exception(
                f"Export trigger for study {study_id} returned no task_id: {trigger_json}"
            )

        elapsed = 0.0
        while True:
            async with session.get(
                f"{base_url}/check_export_status/", params={"task_id": task_id}
            ) as response:
                status_json = await response.json()

            status = status_json.get("status")
            if status == "SUCCESS":
                file_name = status_json["file_name"]
                break
            if status != "PENDING":
                raise Exception(
                    f"Export for study {study_id} ended with status {status}: {status_json}"
                )
            if elapsed >= timeout_seconds:
                raise TimeoutError(
                    f"Export for study {study_id} still PENDING after {timeout_seconds}s"
                )
            await asyncio.sleep(poll_interval_seconds)
            elapsed += poll_interval_seconds

        async with session.get(
            f"{base_url}/export_download/", params={"task_id": task_id}
        ) as response:
            if response.status != 200:
                raise Exception(
                    f"Download for study {study_id} failed with status {response.status}"
                )
            content = await response.read()

    save_dir.mkdir(parents=True, exist_ok=True)
    zip_path = save_dir / file_name
    zip_path.write_bytes(content)

    if not zipfile.is_zipfile(zip_path):
        raise Exception(f"Export download for study {study_id} is not a valid zip")
    with zipfile.ZipFile(zip_path) as archive:
        archive.extractall(save_dir)

    return zip_path
