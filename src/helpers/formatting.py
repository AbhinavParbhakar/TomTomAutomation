import pandas as pd

from helpers.models import StudyMetrics
from tomtom_interactions.models import (
    DrawControlGeometry,
    NetworkItemV1,
    NetworkItemV2,
)


def get_dataframe(metrics: list[StudyMetrics]) -> pd.DataFrame:
    data = [study_metric.model_dump() for study_metric in metrics]

    df = pd.DataFrame(data=data)
    df = df.groupby(
        ["project_name", "miovision_id", "date_range_name"], as_index=False
    ).aggregate({"average_sample_size": "sum"})

    return df


def convert_v2_to_v1(v2: list[NetworkItemV2], timezone: str) -> list[NetworkItemV1]:
    v1_items = []

    for idx, item in enumerate(v2):
        coords = item.geometry.coordinates

        v1_item = NetworkItemV1(
            name=item.name,
            start=item.start,
            end=item.end,
            via=item.via,
            geometry=item.geometry,
            featureId=idx,  # inferred pattern
            editing=False,  # constant assumption
            originalGeometry=coords,  # direct copy
            originalDrawControlGeometry=DrawControlGeometry(
                type=item.geometry.type, coordinates=coords
            ),
            timezone=timezone,  # external constant
        )

        v1_items.append(v1_item)

    return v1_items
