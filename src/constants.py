from dotenv import load_dotenv
import os

load_dotenv()

USERNAME = str(os.getenv("TOMTOM_USERNAME"))
PASSWORD = str(os.getenv("TOMTOM_PASSWORD"))
STUDY_NAME_FORMATS = ["2025 AADT AAWDT","MioVision for test"]
MAX_STUDIES_PER_PAGE_TRAFFIC_ENDPOINT = 100000