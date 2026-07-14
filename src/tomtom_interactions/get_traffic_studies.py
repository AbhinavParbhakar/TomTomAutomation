from aiohttp import ClientSession

from constants import INODE_API_BASE
from helpers.models import StudyInfo, StudyMetrics
from tomtom_interactions.models import RouteResponse
from pydantic_core import ValidationError
import json
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(5),
    wait=wait_exponential(multiplier=1, min=4, max=10)
)
async def get_route_response(
    study_info: StudyInfo, auth_headers: dict
) -> RouteResponse:
    request_url = f"{INODE_API_BASE}/ts/{study_info.id}/"
    async with ClientSession(headers=auth_headers) as session:
        async with session.get(request_url) as response:
            json_response = await response.json()
            try:
                route_response = RouteResponse.model_validate(json_response)
                return route_response
            except ValidationError as e:
                print("\n================================")
                print(f"Status code: {response.status}")
                with open("errors.json",'a') as file:
                    file.write(f"\n{json.dumps(json_response, indent=4)}\n")
                print("================================\n")
                raise


async def get_study_metrics(
    study_info: StudyInfo, auth_headers: dict
) -> list[StudyMetrics]:
    study_metrics = []

    route_response = await get_route_response(study_info, auth_headers)

    project_name = route_response.name

    if route_response.sample_detail:
        summaries = route_response.sample_detail.summaries

        for summary in summaries:
            location_name = (
                summary.locationName.strip()
            )  # Assumes that the location name is in the format "ID Direction"
            location_name_splits = location_name.split(" ")

            miovision_id = ""
            direction_name = "None"
            if len(location_name_splits) == 2:
                direction_name = location_name_splits[1]

            miovision_id = location_name_splits[0]

            study_metrics.append(
                StudyMetrics(
                    project_name=project_name,
                    miovision_id=miovision_id,
                    direction_name=direction_name,
                    date_range_name=summary.dateRangeName,
                    average_sample_size=int(summary.averageSampleSize),
                )
            )
    else:
        print(f"{project_name} did not have sample_details")
    return study_metrics


async def accept_study(study_id: int, auth_headers: dict) -> None:
    """
    Confirms a study that is in NEED_CONFIRMATION so the platform proceeds
    to compute its results.
    """
    request_url = f"{INODE_API_BASE}/ts/{study_id}/accept/"
    async with ClientSession(headers=auth_headers) as session:
        async with session.get(request_url) as response:
            if response.status != 200:
                raise Exception(
                    f"Accepting study {study_id} failed with status "
                    f"{response.status}: {await response.text()}"
                )


async def get_studies(auth_headers: dict) -> list[StudyInfo]:
    studies_endpoint = f"{INODE_API_BASE}/ts/?no_pagination=true&ordering=-create_time"

    async with ClientSession(headers=auth_headers) as session:
        async with session.get(studies_endpoint) as response:
            json_res = await response.json()
            return [StudyInfo.model_validate(study) for study in json_res]
