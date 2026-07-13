from tomtom_interactions.get_traffic_studies import (
    get_studies,
    get_study_metrics,
    get_route_response,
)
from tomtom_interactions.auth import get_auth_headers
from tomtom_interactions.export_study import download_study_csv
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
    template_bodies: list[TemplateBody] = list()

    headers = get_auth_headers()
    studies_info = await get_studies(headers)

    seen_studies: set[str] = set()

    print("Generating Template Bodies")
    for study_info in tqdm.tqdm(studies_info):
        seen_studies.update([study_info.name])
        for filter, city_num in filter_names:
            if filter in study_info.name and filter not in seen_templates:
                seen_templates.update([filter])
                route_response = await get_route_response(study_info, headers)
                template_bodies.extend(
                    generate_templates_bodies(
                        route_response, f"{project_name_filter}{city_num}"
                    )
                )
    print("Creating template")

    for template_body in tqdm.tqdm(template_bodies):
        if template_body.name not in seen_studies:
            print(f"Attempting to upload {template_body.name}")
            await post_template(headers, template_body)
            await sleep(2)


async def get_results(project_name_filter: list[str], save_name_path: str) -> None:
    result_metrics: list[StudyMetrics] = list()
    headers = get_auth_headers()
    studies_info = await get_studies(headers)
    save_path = Path(save_name_path)

    seen_studies: set[str] = set()

    for study_info in tqdm.tqdm(studies_info):
        for filter in project_name_filter:
            if filter in study_info.name and study_info.name not in seen_studies:
                seen_studies.update([study_info.name])
                study_metrics = await get_study_metrics(study_info, headers)
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
    headers = get_auth_headers()
    studies_info = await get_studies(headers)

    matching_studies = [
        study_info
        for study_info in studies_info
        if any(filter.lower() in study_info.name.lower() for filter in project_name_filter)
    ]
    if not matching_studies:
        raise Exception(f"No studies matched filters: {project_name_filter}")

    downloaded_paths: list[Path] = list()
    for study_info in tqdm.tqdm(matching_studies):
        zip_path = await download_study_csv(study_info.id, headers, Path(save_dir))
        downloaded_paths.append(zip_path)

    return downloaded_paths
