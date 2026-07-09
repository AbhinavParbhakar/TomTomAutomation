from typing import List, Optional

from pydantic import BaseModel

from helpers.models import DateRange


class LatLng(BaseModel):
    latitude: float
    longitude: float


class Geometry(BaseModel):
    type: str
    coordinates: List[List[float]]  # [longitude, latitude]


class NetworkItem(BaseModel):
    start: LatLng
    end: LatLng
    via: List  # empty list in sample, unknown structure
    name: str
    geometry: Geometry


class TimeGroup(BaseModel):
    days: List[str]
    times: List[str]


class TimeSet(BaseModel):
    name: str
    timeGroups: List[TimeGroup]


class Summary(BaseModel):
    timeSetName: str
    distanceUnit: str
    locationName: str
    dateRangeName: str
    networkLength: float
    averageSampleSize: float
    coveredNetworkLength: float


class SampleDetail(BaseModel):
    summaries: List[Summary]



class LineStringGeometry(BaseModel):
    type: str
    coordinates: List[list[float]]
    
class NetworkItemV2(BaseModel):
    name: str
    start: LatLng
    end: LatLng
    via: List[LatLng] = []
    geometry: LineStringGeometry


class NetworkModelV2(BaseModel):
    network: list[NetworkItemV2]

class DrawControlGeometry(BaseModel):
    type: str
    coordinates: List[List[float]]


class NetworkItemV1(BaseModel):
    name: str
    start: LatLng
    end: LatLng
    via: List[LatLng] = []

    geometry: LineStringGeometry

    featureId: int
    editing: bool

    originalGeometry: List[List[float]]
    originalDrawControlGeometry: DrawControlGeometry

    timezone: str

class NetworkModelV1(BaseModel):
    network: List[NetworkItemV1]

class RouteResponse(BaseModel):
    id: int
    name: str
    type: str

    network: list[NetworkItemV2]

    user_preference: Optional[dict]
    max_sample_size: Optional[int]

    date_range: list
    time_sets: list

    map_version: str
    map_type: str
    is_time_sets_advanced: bool
    timezone: str

    frcs: List[str]
    accept_mode: str
    probe_source: str
    full_traversal: bool

    job_id: int
    job_state: str
    job_result: Optional[list]

    covered_meters: float | None

    sample_detail: SampleDetail | None = None

    labels: List[str]

    distance_unit: str

    is_archive: bool
    is_volume_estimation: bool
    volume_estimation_id: Optional[int]

    current_progress: int
    volume_estimation_model_id: Optional[int]

    create_time: int
    edit_time: int

    collision_data: Optional[dict]

    is_draft: bool
    key: Optional[str]
    is_deleted: bool





class TemplateBody(BaseModel):
    name: str
    type: str = "ROUTE"
    distance_unit: str = "KILOMETERS"
    network: list[NetworkItemV1]
    date_range: list[DateRange]
    probe_source: str
    frcs: list[str]
    time_sets: list = [
        {"name": "Whole Day", "time_group": {"from": "00:00", "to": "24:00"}}
    ]
    timezone: str
    map_version: str
    map_type: str
    full_traversal: bool = False
    is_time_sets_advanced: bool = False
