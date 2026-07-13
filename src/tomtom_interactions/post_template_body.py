from asyncio import sleep

from aiohttp import ClientSession

from constants import INODE_API_BASE
from tomtom_interactions.models import TemplateBody
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(5),
    wait=wait_exponential(multiplier=1, min=4, max=10)
)
async def post_template(auth_headers: dict, template: TemplateBody) -> dict:
    """
    Creates a new traffic stats report and returns the created report's JSON.
    Waits out 429 rate-limit responses using the API's retry_after_seconds.
    """
    create_endpoint = f"{INODE_API_BASE}/ts/"

    async with ClientSession(headers=auth_headers) as session:
        while True:
            async with session.post(
                create_endpoint, json=template.model_dump(by_alias=True, exclude_none=True)
            ) as res:
                json_response = await res.json()
                if res.status == 429:
                    wait_seconds = json_response.get("retry_after_seconds", 30) + 1
                    print(f"Rate limited, waiting {wait_seconds}s")
                    await sleep(wait_seconds)
                    continue
                if res.status not in (200, 201):
                    raise Exception(
                        f"Creating report '{template.name}' failed with status {res.status}: {json_response}"
                    )
                return json_response
