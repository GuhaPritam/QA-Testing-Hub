import requests
from config import Config

def get_jwt_token():
    url = Config.BASE_URL.rstrip("/") + Config.ENDPOINTS["login"]
    payload = {
        "email": Config.ADMIN_EMAIL,
        "password": Config.ADMIN_PASSWORD,
        "role": Config.ADMIN_ROLE,
    }
    resp = requests.post(url, json=payload, timeout=Config.REQUEST_TIMEOUT)
    resp.raise_for_status()
    body = resp.json()

    token = (
        body.get("token") or
        body.get("access_token") or
        (body.get("data", {}).get("token", {}).get("access"))
    )

    if not token:
        raise ValueError(f"Login failed: token missing in response: {body}")

    Config.HEADERS = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    print("-- [ info ] --Token generated successfully and added to headers.")
    return token
