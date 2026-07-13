import asyncio

from constants import STUDY_NAME_FORMATS
from tomtom_interactions.orchestration import get_results

if __name__ == "__main__":
    asyncio.run(get_results(STUDY_NAME_FORMATS, 'tomtom_results_updated_cities.xlsx'))
