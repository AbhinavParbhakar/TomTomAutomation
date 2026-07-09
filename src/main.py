import asyncio

from constants import (
    STUDY_NAME_FORMATS,
    TEMPLATE_END_NUM,
    TEMPLATE_FILTER_PREFIX,
    TEMPLATE_START_NUM,
)
from tomtom_interactions.orchestration import create_template_copies, get_results

if __name__ == "__main__":
    asyncio.run(get_results(STUDY_NAME_FORMATS, 'tomtom_results_updated_cities.xlsx'))
    # asyncio.run(
    #     create_template_copies(
    #         TEMPLATE_FILTER_PREFIX, TEMPLATE_END_NUM, TEMPLATE_START_NUM
    #     )
    # )
