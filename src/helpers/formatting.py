import pandas as pd

from helpers.models import StudyMetrics


def get_dataframe(metrics: list[StudyMetrics]) -> pd.DataFrame:
    data = [study_metric.model_dump() for study_metric in metrics]

    df = pd.DataFrame(data=data)
    
    df = df.groupby(['project_name','miovision_id','date_range_name'], as_index=False).aggregate(
        {
            'average_sample_size' : 'sum'
        }
    )
    
    return df
