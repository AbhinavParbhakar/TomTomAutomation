from tomtom_interactions.get_traffic_studies import get_studies, get_study_metrics
from tomtom_interactions.auth import get_auth_cookies
from tomtom_interactions.export_study import (
    download_export,
    trigger_export,
    wait_for_export,
)
from helpers.formatting import get_dataframe
from helpers.models import StudyMetrics
import tqdm
from pathlib import Path



async def get_results(project_name_filter: list[str], save_name_path: str) -> None:
    result_metrics: list[StudyMetrics] = list()
    cookies = await get_auth_cookies()
    studies_info = await get_studies(cookies)
    save_path = Path(save_name_path)

    for study_info in tqdm.tqdm(studies_info):
        for filter in project_name_filter:
            if filter in study_info.name:
                study_metrics = await get_study_metrics(study_info, cookies)
                result_metrics.extend(study_metrics)
    
    df =  get_dataframe(result_metrics)
    
    match save_path.suffix:
        case '.csv':
            df.to_csv(save_path, index=False)
        case '.xlsx':
            df.to_excel(save_path, index=False)
        case _:
            raise Exception("save_name_path must end in one of: {'.csv', '.xlsx'}")


async def export_study_csvs(project_name_filter: list[str], save_dir: str) -> list[Path]:
    """
    Exports the csv report of every study whose name contains one of the
    filters (case-insensitive), saving the downloaded files under save_dir.
    """
    cookies = await get_auth_cookies()
    studies_info = await get_studies(cookies)

    matching_studies = [
        study_info
        for study_info in studies_info
        if any(filter.lower() in study_info.name.lower() for filter in project_name_filter)
    ]
    if not matching_studies:
        raise Exception(f"No studies matched filters: {project_name_filter}")

    downloaded_paths: list[Path] = list()
    for study_info in tqdm.tqdm(matching_studies):
        task_id = await trigger_export(study_info.id, cookies)
        file_name = await wait_for_export(study_info.id, task_id, cookies)
        zip_path = await download_export(
            study_info.id, task_id, file_name, cookies, Path(save_dir)
        )
        downloaded_paths.append(zip_path)

    return downloaded_paths
