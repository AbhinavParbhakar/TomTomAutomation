import asyncio
from tomtom_interactions.orchestration import get_results
from constants import STUDY_NAME_FORMATS

if __name__ == "__main__":
    asyncio.run(get_results(STUDY_NAME_FORMATS, 'tomtom_results.xlsx'))