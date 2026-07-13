from typing import List, Optional

from pydantic import BaseModel

from helpers.models import DateRange


class LatLng(BaseModel):
    latitude: float
    longitude: float


class LineStringGeometry(BaseModel):
    type: str
    coordinates: List[List[float]]  # [longitude, latitude]


class NetworkItem(BaseModel):
    name: str
    start: LatLng
    end: LatLng
    via: List[LatLng] = []
    geometry: LineStringGeometry
    # absent in detail responses; set when the item is used in a POST body
    timezone: Optional[str] = None


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


class RouteResponse(BaseModel):
    """
    Detail response of GET /api/v1/flow/ts/{id}/ (DetailTrafficStatsReport).
    """

    id: int
    name: str
    type: str

    network: list[NetworkItem]

    user_preference: Optional[dict]
    max_sample_size: Optional[int]

    date_range: list
    time_sets: list

    map_version: str
    is_time_sets_advanced: bool
    timezone: str

    frcs: List[str]
    probe_source: str
    full_traversal: bool

    job_state: Optional[str]
    job_result: Optional[list]

    covered_meters: float | None

    sample_detail: SampleDetail | None = None

    messages: list | str = []  # the API returns "" when there are no messages
    labels: List[str]

    distance_unit: str

    volume_estimation_model_id: Optional[int]

    create_time: int
    create_time_iso: str
    edit_time: int
    edit_time_iso: str

    is_draft: bool
    is_archive: bool


class TimeGroupAdvanced(BaseModel):
    days: str  # day abbreviation, e.g. "MON"
    times: list[str]  # time ranges as "HH:MM-HH:MM"


class TimeSetAdvanced(BaseModel):
    name: str
    time_groups: list[TimeGroupAdvanced]


class TemplateBody(BaseModel):
    """
    Request body of POST /api/v1/flow/ts/ for a ROUTE report.
    """

    name: str
    type: str = "ROUTE"
    distance_unit: str = "KILOMETERS"
    network: list[NetworkItem]
    date_range: list[DateRange]
    probe_source: str
    frcs: list[str]
    time_sets: list = [
        {"name": "Whole Day", "time_group": {"from": "00:00", "to": "24:00"}}
    ]
    timezone: str
    map_version: str
    full_traversal: bool = False
    is_time_sets_advanced: bool = False
    # NOTE: never send is_draft — the v1 endpoint 500s on its draft code path
