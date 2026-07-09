from aiohttp import ClientSession, CookieJar

from constants import MAX_STUDIES_PER_PAGE_TRAFFIC_ENDPOINT
from helpers.models import StudiesResponse, StudyInfo, StudyMetrics
from tomtom_interactions.models import RouteResponse
from pydantic_core import ValidationError
import json
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(5),
    wait=wait_exponential(multiplier=1, min=4, max=10)
)
async def get_route_response(
    study_info: StudyInfo, auth_cookies: CookieJar
) -> RouteResponse:
    request_url = f"https://inode.app/api/road_analytics/traffic_stats/{study_info.id}/"
    async with ClientSession(cookie_jar=auth_cookies) as session:
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
    study_info: StudyInfo, auth_cookies: CookieJar
) -> list[StudyMetrics]:
    study_metrics = []

    route_response = await get_route_response(study_info, auth_cookies)

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


async def get_studies(jar: CookieJar) -> list[StudyInfo]:
    studies_endpoint = f"https://inode.app/api/road_analytics/traffic_stats/?page=1&page_size={MAX_STUDIES_PER_PAGE_TRAFFIC_ENDPOINT}&ordering=-create_time&is_draft=false&is_archive=false&is_deleted=false&job_state=NEW,SCHEDULED,MAP_MATCHING,MAP_MATCHED,READING_GEOBASE,CALCULATIONS,NEED_CONFIRMATION,PROCESSING_RESULTS,RESULTS_READY,DONE,ERROR,REJECTED,CANCELLED,EXPIRED"

    async with ClientSession(cookie_jar=jar) as session:
        async with session.get(studies_endpoint) as response:
            json_res = await response.json()
            study_response = StudiesResponse.model_validate(json_res)
            return study_response.results
