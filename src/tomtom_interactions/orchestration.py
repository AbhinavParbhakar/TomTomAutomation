from tomtom_interactions.get_traffic_studies import (
    get_studies,
    get_study_metrics,
    get_route_response,
)
from tomtom_interactions.auth import get_auth_cookies
from tomtom_interactions.export_study import (
    download_export,
    trigger_export,
    wait_for_export,
)
from helpers.formatting import get_dataframe
from helpers.get_templates import generate_templates_bodies
from tomtom_interactions.post_template_body import post_template
from helpers.models import StudyMetrics
from tomtom_interactions.models import TemplateBody
import tqdm
from pathlib import Path
from asyncio import sleep


async def create_template_copies(
    project_name_filter: str, template_max_num: int, template_min_num: int
) -> None:
    seen_templates: set[str] = set()

    filter_names = [
        (f"{project_name_filter}{num} (2024-01-01-2024-01-24)", num)
        for num in range(template_min_num, template_max_num + 1)
    ]
    template_bodies: list[tuple[TemplateBody, int]] = list()

    cookies = await get_auth_cookies()
    studies_info = await get_studies(cookies)
    
    seen_studies: set[str] = set()

    print("Generating Template Bodies")
    for study_info in tqdm.tqdm(studies_info):
        seen_studies.update([study_info.name])
        for filter, city_num in filter_names:
            if filter in study_info.name and filter not in seen_templates:
                seen_templates.update([filter])
                route_response = await get_route_response(study_info, cookies)
                template_bodies.extend(
                    [
                        (template_body, route_response.id)
                        for template_body in generate_templates_bodies(
                            route_response, f"{project_name_filter}{city_num}"
                        )
                    ]
                )
    print("Creating template")
    
    x_csrf_token = ""
    for cookie in cookies:
        if cookie.key == "csrftoken":
            x_csrf_token = cookie.value
    for template_body, clone_id in tqdm.tqdm( template_bodies):
        if template_body.name not in seen_studies:
            print(f"Attempting to upload {template_body.name}")
            await post_template(cookies, template_body, clone_id, x_csrf_token)
            await sleep(2)


async def get_results(project_name_filter: list[str], save_name_path: str) -> None:
    result_metrics: list[StudyMetrics] = list()
    cookies = await get_auth_cookies()
    studies_info = await get_studies(cookies)
    save_path = Path(save_name_path)
    
    seen_studies: set[str] = set()

    for study_info in tqdm.tqdm(studies_info):
        for filter in project_name_filter:
            print(study_info.name)
            if filter in study_info.name and study_info.name not in seen_studies:
                seen_studies.update([study_info.name])
                study_metrics = await get_study_metrics(study_info, cookies)
                result_metrics.extend(study_metrics)

    df = get_dataframe(result_metrics)

    match save_path.suffix:
        case ".csv":
            df.to_csv(save_path, index=False)
        case ".xlsx":
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
