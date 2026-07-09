from aiohttp import ClientSession, CookieJar
from tomtom_interactions.models import TemplateBody
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(5),
    wait=wait_exponential(multiplier=1, min=4, max=10)
)
async def post_template(cookies: CookieJar, template: TemplateBody, clone_id: int, x_csrf: str) -> None:
    create_endpoint = "https://inode.app/api/road_analytics/traffic_stats/"
    headers = {
        "Referer": f"https://inode.app/dashboard/road-analytics/traffic-stats/clone?id={clone_id}",
        "Origin": "https://inode.app",
        "X-Csrftoken": x_csrf
    }

    async with ClientSession(cookie_jar=cookies) as session:
        async with session.post(
            create_endpoint, json=template.model_dump(by_alias=True), headers=headers
        ) as res:
            if res.status != 201 and res.status != 200:
                print(await res.json())
