"""
HTTP Request Helper
-----------------
Makes API requests with error handling and response parsing.

Example:
    status, data = safe_request("post", "http://api/login",
                              headers={"Content-Type": "application/json"},
                              json={"email": "test@mail.com"})
"""

import pytest
import requests
from Api.Automation.Src.Config.config import Config

def safe_request(method, url, **kwargs):
    """Send HTTP request with error handling & return status, data."""
    try:
        resp = requests.request(method, url, timeout=Config.REQUEST_TIMEOUT, **kwargs)
        return resp.status_code, resp.json() if resp.text else resp.text
    except requests.exceptions.Timeout:
        pytest.fail(f"Timeout: {url}")
    except requests.exceptions.ConnectionError as e:
        pytest.fail(f"Connection failed: {url} - {e}")
    except ValueError:  # JSON parsing failed
        return resp.status_code, resp.text
    except Exception as e:
        pytest.fail(f"Request error: {url} - {e}")
