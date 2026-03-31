from aiohttp import ClientSession, CookieJar

from constants import MAX_STUDIES_PER_PAGE_TRAFFIC_ENDPOINT
from helpers.models import StudiesResponse, StudyInfo, StudyMetrics
from tomtom_interactions.models import RouteResponse
from pydantic_core import ValidationError


async def get_study_metrics(
    study_info: StudyInfo, auth_cookies: CookieJar
) -> list[StudyMetrics]:
    study_metrics = []
    request_url = f"https://inode.app/api/road_analytics/traffic_stats/{study_info.id}/"

    async with ClientSession(cookie_jar=auth_cookies) as session:
        async with session.get(request_url) as response:
            json_response = await response.json()
            try:
                route_response = RouteResponse.model_validate(json_response)

                project_name = route_response.name
                summaries = route_response.sample_detail.summaries

                for summary in summaries:
                    location_name = (
                        summary.locationName.strip()
                    )  # Assumes that the location name is in the format "ID Direction"
                    location_name_splits = location_name.split(" ")

                    if len(location_name_splits) != 2:
                        raise Exception(
                            "locationName did not follow the expected 'ID Direction' format for study {study_info.id}, location name: {location_name}"
                        )

                    miovision_id = int(location_name_splits[0])
                    direction_name = location_name_splits[1]

                    study_metrics.append(
                        StudyMetrics(
                            project_name=project_name,
                            miovision_id=miovision_id,
                            direction_name=direction_name,
                            date_range_name=summary.dateRangeName,
                            average_sample_size=int(summary.averageSampleSize),
                        )
                    )
            except ValidationError:
                print("\n================================")
                print(f"Status code: {response.status}")
                print(json_response)
                print("================================\n")
                raise
    return study_metrics


async def get_studies(jar: CookieJar) -> list[StudyInfo]:
    studies_endpoint = f"https://inode.app/api/road_analytics/traffic_stats/?page=1&page_size={MAX_STUDIES_PER_PAGE_TRAFFIC_ENDPOINT}&ordering=-create_time&is_draft=false&is_archive=false&is_deleted=false&job_state=NEW,SCHEDULED,MAP_MATCHING,MAP_MATCHED,READING_GEOBASE,CALCULATIONS,NEED_CONFIRMATION,PROCESSING_RESULTS,RESULTS_READY,DONE,ERROR,REJECTED,CANCELLED,EXPIRED"

    async with ClientSession(cookie_jar=jar) as session:
        async with session.get(studies_endpoint) as response:
            json_res = await response.json()
            study_response = StudiesResponse.model_validate(json_res)
            return study_response.results
