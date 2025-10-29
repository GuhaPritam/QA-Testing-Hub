from Api.Automation.Src.Config.config import Config
import requests


def build_url(endpoint_key="login"):
    """
    Default endpoint is 'login'. You can override by passing another key.
    """
    try:
        return Config.BASE_URL.rstrip("/") + Config.ENDPOINTS[endpoint_key]
    except KeyError:
        raise ValueError(f"Invalid endpoint_key: {endpoint_key}")


def get_login_payload(email=None, password=None, role=None):
    """Reusable login payload generator with optional overrides."""
    return {
        "email": email if email is not None else Config.ADMIN_EMAIL,
        "password": password if password is not None else Config.ADMIN_PASSWORD,
        "role": role if role is not None else Config.ADMIN_ROLE
    }


def api_request(method, endpoint_key="login", payload=None, headers=None, use_timeout=True):
    url = build_url(endpoint_key)
    hdrs = headers or Config.HEADERS
    timeout = Config.REQUEST_TIMEOUT if use_timeout else None
    return getattr(requests, method)(url, json=payload, headers=hdrs, timeout=timeout)


