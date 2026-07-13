from typing import Optional

from pydantic import BaseModel, Field

class StudyInfo(BaseModel):
    id: int
    name: str
    type: str
    job_state: Optional[str]
    create_time: int
    create_time_iso: str
    labels: list

class StudyMetrics(BaseModel):
    project_name: str
    direction_name: str
    miovision_id: str
    date_range_name: str
    average_sample_size: int

class DateRange(BaseModel):
    name: str
    from_: str = Field(alias="from")
    to: str
    days: list[int]
    eligible_days: list[int]
    exclusions: list = []
