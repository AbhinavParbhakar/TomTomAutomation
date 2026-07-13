import asyncio

from constants import TEMPLATE_SOURCE_STUDY_NAMES
from tomtom_interactions.orchestration import create_template_copies

# NOTE: running this creates real studies on the platform (one per
# DAYS_PER_PROJECT-day chunk between TEMPLATE_START_DATE and TEMPLATE_END_DATE,
# for every source study). Already-existing names are skipped.
if __name__ == "__main__":
    asyncio.run(create_template_copies(TEMPLATE_SOURCE_STUDY_NAMES))
