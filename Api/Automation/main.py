import pytest
import requests
from config import Config


# ---------- Common Request Handler ----------
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


# ---------- Fixtures ----------
@pytest.fixture(scope="module")
def category_id():
    """Create a fresh category before tests, cleanup after"""
    # Pre-cleanup
    delete_if_exists("Automation Test Category")

    # Create
    url = Config.BASE_URL + Config.ENDPOINTS["create_category"]
    payload = {"name": "Automation Test Category", "description": "Created by pytest"}
    status, body = safe_request("post", url, headers=Config.HEADERS, json=payload)

    assert status in (200, 201), f"Create failed: {status} {body}"

    cid = None
    if isinstance(body, dict):
        for key in ("id", "_id", "category_id"):
            if key in body:
                cid = body[key]
                break
        if not cid and "data" in body and isinstance(body["data"], dict):
            cid = body["data"].get("id") or body["data"].get("_id")

    assert cid, f"No category id found in response: {body}"

    yield cid

    # Cleanup
    del_url = Config.BASE_URL + Config.ENDPOINTS["delete_category"].format(id=cid)
    safe_request("delete", del_url, headers=Config.HEADERS)


def delete_if_exists(category_name):
    """Delete category if already exists"""
    url = Config.BASE_URL + Config.ENDPOINTS["list_categories"]
    status, body = safe_request("post", url, headers=Config.HEADERS)

    if status == 200 and "data" in body and "categories" in body["data"]:
        for cat in body["data"]["categories"]:
            if cat.get("name") == category_name:
                del_url = Config.BASE_URL + Config.ENDPOINTS["delete_category"].format(id=cat["id"])
                safe_request("delete", del_url, headers=Config.HEADERS)
                break


# ---------- Test Cases (method-wise) ----------
def test_post_create_category(category_id):
    """POST: Create Category (via fixture)"""
    assert category_id is not None


def test_get_list_categories():
    """GET/POST: List Categories"""
    url = Config.BASE_URL + Config.ENDPOINTS["list_categories"]
    status, body = safe_request("post", url, headers=Config.HEADERS)
    assert status == 200
    assert "data" in body


def test_put_update_category(category_id):
    """PUT: Update Category"""
    url = Config.BASE_URL + Config.ENDPOINTS["update_category"].format(id=category_id)
    payload = {"name": "Updated Automation Category", "description": "Updated by pytest"}
    status, body = safe_request("put", url, headers=Config.HEADERS, json=payload)
    assert status in (200, 201)
    assert isinstance(body, dict)


def test_delete_category(category_id):
    """DELETE: Delete Category"""
    url = Config.BASE_URL + Config.ENDPOINTS["delete_category"].format(id=category_id)
    status, body = safe_request("delete", url, headers=Config.HEADERS)
    assert status in (200, 204)
