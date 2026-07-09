from dotenv import load_dotenv
import os
import arrow
from datetime import datetime

load_dotenv()

USERNAME = str(os.getenv("TOMTOM_USERNAME"))
PASSWORD = str(os.getenv("TOMTOM_PASSWORD"))
STUDY_NAME_FORMATS = ["Updated"]
MAX_STUDIES_PER_PAGE_TRAFFIC_ENDPOINT = 100000
DATE_RANGE_MODEL_ARROW_TIME_FORMAT = "YYYY-MM-DD"
TEMPLATE_START_NUM = 1
TEMPLATE_END_NUM = 2
TEMPLATE_FILTER_PREFIX = "MioVision for Whole City-"

TEMPLATE_START_DATE = arrow.get(datetime(year=2025, month=10, day=1))
TEMPLATE_END_DATE = arrow.get(datetime(year=2026, month=3, day=31))
DAYS_PER_PROJECT = 24