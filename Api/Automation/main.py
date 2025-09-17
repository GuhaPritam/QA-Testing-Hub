import requests
import sys
import time
from config import Config


def safe_request(method, url, **kwargs):
    try:
        resp = requests.request(method, url, timeout=Config.REQUEST_TIMEOUT, **kwargs)
    except requests.exceptions.Timeout:
        print(f"[ERROR] Timeout when calling {url}")
        return None
    except requests.exceptions.ConnectionError as e:
        print(f"[ERROR] Connection error when calling {url}: {e}")
        return None
    except Exception as e:
        print(f"[ERROR] Unexpected error when calling {url}: {e}")
        return None

    try:
        body = resp.json()
    except ValueError:
        body = resp.text

    return resp.status_code, body


def test_create_category():
    url = Config.BASE_URL + Config.ENDPOINTS["create_category"]
    payload = {"name": "Automation Test Category", "description": "Created by automation script"}
    print(f"\n[STEP] Create category -> POST {url}")
    result = safe_request("post", url, headers=Config.HEADERS, json=payload)
    if not result:
        return None
    status, body = result
    print("Status:", status)
    print("Body:", body)

    if isinstance(body, dict):
        for k in ("id", "_id", "data", "category_id"):
            if k in body:
                if k == "data" and isinstance(body[k], dict):
                    for sub in ("id", "_id"):
                        if sub in body[k]:
                            return body[k][sub]
                else:
                    return body[k]
        if "data" in body and isinstance(body["data"], dict):
            for sub in ("id", "_id"):
                if sub in body["data"]:
                    return body["data"][sub]
    print("[WARN] Couldn't find created resource id in response.")
    return None


def test_list_categories():
    url = Config.BASE_URL + Config.ENDPOINTS["list_categories"]
    print(f"\n[STEP] List categories -> POST {url}")
    result = safe_request("post", url, headers=Config.HEADERS)
    if not result:
        return
    status, body = result
    print("Status:", status)
    print("Body:", body)


def test_update_category(category_id):
    url = Config.BASE_URL + Config.ENDPOINTS["update_category"].format(id=category_id)
    payload = {"name": "Updated Automation Category", "description": "Updated by automation script"}
    print(f"\n[STEP] Update category -> PUT {url}")
    result = safe_request("put", url, headers=Config.HEADERS, json=payload)
    if not result:
        return
    status, body = result
    print("Status:", status)
    print("Body:", body)


def test_delete_category(category_id):
    url = Config.BASE_URL + Config.ENDPOINTS["delete_category"].format(id=category_id)
    print(f"\n[STEP] Delete category -> DELETE {url}")
    result = safe_request("delete", url, headers=Config.HEADERS)
    if not result:
        return
    status, body = result
    print("Status:", status)
    print("Body:", body)


def delete_if_exists(category_name="Automation Test Category"):
    url = Config.BASE_URL + Config.ENDPOINTS["list_categories"]
    result = safe_request("post", url, headers=Config.HEADERS)
    if not result:
        return
    status, body = result

    if status == 200 and "data" in body and "categories" in body["data"]:
        for cat in body["data"]["categories"]:
            if cat["name"] == category_name:
                print(f"[INFO] Found existing category '{category_name}' with id={cat['id']}. Deleting it...")
                test_delete_category(cat["id"])
                break



if __name__ == "__main__":
    if not Config.BASE_URL or not Config.ADMIN_TOKEN:
        print("Please set BASE_URL and ADMIN_TOKEN in your .env file. Exiting.")
        sys.exit(1)

    print("Starting automation tests against:", Config.BASE_URL)

    delete_if_exists("Automation Test Category")

    created_id = test_create_category()
    time.sleep(0.5)

    test_list_categories()
    time.sleep(0.5)

    if created_id:
        test_update_category(created_id)
        time.sleep(0.5)
        test_delete_category(created_id)
    else:
        print("\n[SKIP] No created resource id — skipping update & delete steps.")

