import pytest
from Api.Automation.Src_ff.Config.config import Config
from Api.Automation.Src_ff.Utils.request_utils import safe_request

class TestCategoryCRUD:

    @pytest.fixture(scope="class")
    def category_id(self):
        # Pre-cleanup
        self.delete_if_exists("Automation Test Category")

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

    def delete_if_exists(self, category_name):
        url = Config.BASE_URL + Config.ENDPOINTS["list_categories"]
        status, body = safe_request("post", url, headers=Config.HEADERS)

        if status == 200 and "data" in body and "categories" in body["data"]:
            for cat in body["data"]["categories"]:
                if cat.get("name") == category_name:
                    del_url = Config.BASE_URL + Config.ENDPOINTS["delete_category"].format(id=cat["id"])
                    safe_request("delete", del_url, headers=Config.HEADERS)
                    break

    def test_post_create_category(self, category_id):
        assert category_id is not None

    def test_get_list_categories(self):
        url = Config.BASE_URL + Config.ENDPOINTS["list_categories"]
        status, body = safe_request("post", url, headers=Config.HEADERS)
        assert status == 200
        assert "data" in body

    def test_put_update_category(self, category_id):
        url = Config.BASE_URL + Config.ENDPOINTS["update_category"].format(id=category_id)
        payload = {"name": "Updated Automation Category", "description": "Updated by pytest"}
        status, body = safe_request("put", url, headers=Config.HEADERS, json=payload)
        assert status in (200, 201)
        assert isinstance(body, dict)

    def test_delete_category(self, category_id):
        url = Config.BASE_URL + Config.ENDPOINTS["delete_category"].format(id=category_id)
        status, body = safe_request("delete", url, headers=Config.HEADERS)
        assert status in (200, 204)
