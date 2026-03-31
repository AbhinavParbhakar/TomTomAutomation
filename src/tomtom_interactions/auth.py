from aiohttp import ClientSession, CookieJar

from constants import PASSWORD, USERNAME


def get_requests_body() -> dict:
    return {
        "username": USERNAME,
        "password": PASSWORD,
        "rememberMe": "",
        "check_tfa": True,
    }


def get_request_headers() -> dict:
    return {
        "Content-Type": "multipart/form-data; boundary=----WebKitFormBoundary2skZZqYo5Vg766cn",
        "content-length": "466",
    }


async def get_auth_cookies() -> CookieJar:
    """
    Returns authenticated cookies
    """
    auth_link = "https://inode.app/api/login/"
    body = get_requests_body()
    jar = CookieJar()

    async with ClientSession(cookie_jar=jar) as session:
        async with session.post(url=auth_link, data=body) as response:
            await response.json()
    return jar
