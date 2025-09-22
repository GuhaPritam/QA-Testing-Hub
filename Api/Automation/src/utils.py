import pytest
import requests
from config import Config

def safe_request(method, url, **kwargs):
    try:
        resp = requests.request(method, url, timeout=Config.REQUEST_TIMEOUT, **kwargs)
    except requests.exceptions.Timeout:
        pytest.fail(f"[ERROR] Timeout when calling {url}")
    except requests.exceptions.ConnectionError as e:
        pytest.fail(f"[ERROR] Connection error when calling {url}: {e}")
    except Exception as e:
        pytest.fail(f"[ERROR] Unexpected error when calling {url}: {e}")

    try:
        body = resp.json()
    except ValueError:
        body = resp.text

    return resp.status_code, body
