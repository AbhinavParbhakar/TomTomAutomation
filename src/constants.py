from dotenv import load_dotenv
import os
import arrow
from datetime import datetime

load_dotenv()

API_TOKEN = str(os.getenv("TOMTOM_API_TOKEN"))
INODE_API_BASE = "https://inode.app/api/v1/flow"

STUDY_NAME_FORMATS = ["Updated"]
EXPORT_STUDY_NAME_FILTERS = ["Whitemud Dr", "Calgary Trail", "23 Ave"]
DATE_RANGE_MODEL_ARROW_TIME_FORMAT = "YYYY-MM-DD"
TEMPLATE_START_NUM = 1
TEMPLATE_END_NUM = 2
TEMPLATE_FILTER_PREFIX = "MioVision for Whole City-"

TEMPLATE_START_DATE = arrow.get(datetime(year=2025, month=10, day=1))
TEMPLATE_END_DATE = arrow.get(datetime(year=2026, month=3, day=31))
DAYS_PER_PROJECT = 24
