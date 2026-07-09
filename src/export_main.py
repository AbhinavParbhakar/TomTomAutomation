import asyncio
from tomtom_interactions.orchestration import export_study_csvs
from constants import EXPORT_STUDY_NAME_FILTERS

if __name__ == "__main__":
    asyncio.run(export_study_csvs(EXPORT_STUDY_NAME_FILTERS, 'exports'))
