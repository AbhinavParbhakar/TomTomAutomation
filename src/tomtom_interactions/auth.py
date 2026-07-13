from constants import API_TOKEN


def get_auth_headers() -> dict:
    """
    Returns the Authorization header expected by every iNode API endpoint.
    The token comes from Settings > My Profile > API Access in the dashboard.
    """
    return {"Authorization": f"Token {API_TOKEN}"}
