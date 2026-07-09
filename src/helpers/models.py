from pydantic import BaseModel, Field

class StudyInfo(BaseModel):
    id: int
    name: str
    type: str
    current_progress: int
    job_state: str
    create_time: int
    labels: list

class StudiesResponse(BaseModel):
    count: int
    page_size: int
    results: list[StudyInfo]

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