from tomtom_interactions.get_traffic_studies import get_studies, get_study_metrics
from tomtom_interactions.auth import get_auth_cookies
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
