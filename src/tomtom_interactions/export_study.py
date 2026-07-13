import zipfile
from pathlib import Path

from aiohttp import ClientSession

from constants import INODE_API_BASE


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
