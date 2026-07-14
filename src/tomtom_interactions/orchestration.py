from tomtom_interactions.get_traffic_studies import (
    accept_study,
    get_studies,
    get_study_metrics,
    get_route_response,
)
from constants import EXPORT_SELECTION
from tomtom_interactions.auth import get_auth_headers
from tomtom_interactions.export_study import download_segment_csv, download_study_csv
from helpers.formatting import get_dataframe
from helpers.get_templates import generate_templates_bodies
from tomtom_interactions.post_template_body import post_template
from helpers.models import StudyMetrics
from tomtom_interactions.models import TemplateBody
import tqdm
from pathlib import Path
from asyncio import sleep


async def create_template_copies(template_source_names: list[str]) -> None:
    """
    For each named source study, creates copies covering TEMPLATE_START_DATE
    to TEMPLATE_END_DATE in DAYS_PER_PROJECT-day chunks. Copies whose names
    already exist on the platform are skipped, so re-running is safe.
    """
    template_bodies: list[TemplateBody] = list()

    headers = get_auth_headers()
    studies_info = await get_studies(headers)

    seen_studies: set[str] = {study_info.name for study_info in studies_info}

    print("Generating Template Bodies")
    for source_name in template_source_names:
        source_study = next(
            (study_info for study_info in studies_info if study_info.name == source_name),
            None,
        )
        if source_study is None:
            print(f"No study named {source_name!r} found on the account - skipping")
            continue
        route_response = await get_route_response(source_study, headers)
        template_bodies.extend(generate_templates_bodies(route_response, source_name))

    print("Creating templates")
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

    # confirm any studies waiting on the sample-size preview so the platform
    # computes their results; they become downloadable on a later run
    pending_studies = [s for s in matching_studies if s.job_state == "NEED_CONFIRMATION"]
    for study_info in pending_studies:
        print(f"Accepting {study_info.name}")
        await accept_study(study_info.id, headers)
        await sleep(1)

    ready_studies = [s for s in matching_studies if s.job_state == "RESULTS_READY"]
    skipped = len(matching_studies) - len(ready_studies)
    if skipped:
        print(f"Skipping {skipped} matching studies that are not RESULTS_READY yet")

    downloaded_paths: list[Path] = list()
    for study_info in tqdm.tqdm(ready_studies):
        if EXPORT_SELECTION == "segment":
            # segment exports exceed the v1 endpoint's row cap; use the async
            # export flow, which needs @ids from the study's detail response
            detail = await get_route_response(study_info, headers)
            zip_path = await download_segment_csv(
                study_info.id,
                time_set_id=detail.time_sets[0]["@id"],
                date_range_id=detail.date_range[0]["@id"],
                auth_headers=headers,
                save_dir=Path(save_dir),
            )
        else:
            zip_path = await download_study_csv(
                study_info.id, headers, Path(save_dir), selection=EXPORT_SELECTION
            )
        downloaded_paths.append(zip_path)

    return downloaded_paths
