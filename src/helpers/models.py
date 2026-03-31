from pydantic import BaseModel

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
    miovision_id: int
    date_range_name: str
    average_sample_size: int