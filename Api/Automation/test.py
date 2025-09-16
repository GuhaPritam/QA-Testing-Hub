"""
automation_test.py

Usage:
  1. Set BASE_URL to your API base (e.g. "http://localhost:3000" or "https://api.example.com")
  2. Run: python automation_test.py
"""

import requests
import sys
import time

# ====== CONFIGURE THESE ======
BASE_URL = "https://vd-api.weavers-web.com"
ADMIN_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6IjFmODkxOTU4LTYyOTUtNGQ5ZC05MTNiLTIzNzg3MjNhNmViNCIsInRva2VuVHlwZSI6ImFjY2VzcyIsImlhdCI6MTc1ODAxOTE5NywiZXhwIjoxNzU4MDI5OTk3fQ.o_b1gIsHb75ZsFm3nw83x_gWVRBOxC5c3DHHiLHqFdY"
# ==============================

HEADERS = {
    "Authorization": f"Bearer {ADMIN_TOKEN}",
    "Content-Type": "application/json"
}

ENDPOINTS = {
    "create_category": "/v1/admin/business/category",
    "list_categories": "/v1/admin/business/category/list",
    "update_category": "/v1/admin/business/category/{id}",
    "delete_category": "/v1/admin/business/category/{id}",
}

REQUEST_TIMEOUT = 10  # seconds


def safe_request(method, url, **kwargs):
    """Helper that performs request and handles connection/timeouts."""
    try:
        resp = requests.request(method, url, timeout=REQUEST_TIMEOUT, **kwargs)
    except requests.exceptions.Timeout:
        print(f"[ERROR] Timeout when calling {url}")
        return None
    except requests.exceptions.ConnectionError as e:
        print(f"[ERROR] Connection error when calling {url}: {e}")
        return None
    except Exception as e:
        print(f"[ERROR] Unexpected error when calling {url}: {e}")
        return None

    # try parsing json, but fallback to text
    try:
        body = resp.json()
    except ValueError:
        body = resp.text

    return resp.status_code, body


def test_create_category():
    url = BASE_URL + ENDPOINTS["create_category"]
    payload = {"name": "Automation Test Category", "description": "Created by automation script"}
    print(f"\n[STEP] Create category -> POST {url}")
    result = safe_request("post", url, headers=HEADERS, json=payload)
    if not result:
        return None
    status, body = result
    print("Status:", status)
    print("Body:", body)
    # try common id keys
    if isinstance(body, dict):
        for k in ("id", "_id", "data", "category_id"):
            if k in body:
                # if id nested inside data
                if k == "data" and isinstance(body[k], dict):
                    for sub in ("id", "_id"):
                        if sub in body[k]:
                            return body[k][sub]
                else:
                    return body[k]
        # sometimes response shape is { "data": { "id": ... } }
        if "data" in body and isinstance(body["data"], dict):
            for sub in ("id", "_id"):
                if sub in body["data"]:
                    return body["data"][sub]
    # cannot find id
    print("[WARN] Couldn't find created resource id in response. You may need to provide a valid id manually.")
    return None


def test_list_categories():
    url = BASE_URL + ENDPOINTS["list_categories"]
    print(f"\n[STEP] List categories -> POST {url}")
    result = safe_request("post", url, headers=HEADERS)
    if not result:
        return
    status, body = result
    print("Status:", status)
    print("Body:", body)


def test_update_category(category_id):
    url = BASE_URL + ENDPOINTS["update_category"].format(id=category_id)
    payload = {"name": "Updated Automation Category", "description": "Updated by automation script"}
    print(f"\n[STEP] Update category -> PUT {url}")
    result = safe_request("put", url, headers=HEADERS, json=payload)
    if not result:
        return
    status, body = result
    print("Status:", status)
    print("Body:", body)


def test_delete_category(category_id):
    url = BASE_URL + ENDPOINTS["delete_category"].format(id=category_id)
    print(f"\n[STEP] Delete category -> DELETE {url}")
    result = safe_request("delete", url, headers=HEADERS)
    if not result:
        return
    status, body = result
    print("Status:", status)
    print("Body:", body)


if __name__ == "__main__":
    # quick sanity check for BASE_URL
    if "your-api.com" in BASE_URL or BASE_URL.strip() == "":
        print("Please set BASE_URL to your real API host (not the placeholder). Exiting.")
        sys.exit(1)

    print("Starting automation tests against:", BASE_URL)
    # 1. Create
    created_id = test_create_category()
    # small sleep in case server needs it
    time.sleep(0.5)

    # 2. List
    test_list_categories()
    time.sleep(0.5)

    # 3. Update & Delete (only if we have id)
    if created_id:
        test_update_category(created_id)
        time.sleep(0.5)
        test_delete_category(created_id)
    else:
        print("\n[SKIP] No created resource id — skipping update & delete steps.")
