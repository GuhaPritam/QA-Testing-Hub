import pytest
import uuid
import json
import requests
import traceback
from Api.Automation.Src.Config.config import Config
from Api.Automation.Src.Utils.request_utils import safe_request
from Api.Automation.Src.Utils.print_api_utils import print_api_response
from jsonschema import validate, ValidationError


def _extract_id(body):
    """Return a candidate id from a response body or None."""
    try:
        if not isinstance(body, dict):
            return None
        for key in ("id", "_id", "category_id"):
            if key in body and body[key]:
                return body[key]
        data = body.get("data")
        if isinstance(data, dict):
            for key in ("id", "_id", "category_id"):
                if key in data and data[key]:
                    return data[key]
        if isinstance(data, list) and data:
            first = data[0]
            if isinstance(first, dict):
                for key in ("id", "_id", "category_id"):
                    if key in first and first[key]:
                        return first[key]
        return None
    except Exception as e:
        print(f"Error extracting ID: {e}")
        return None


class TestCategoryCRUD:

    @pytest.fixture(scope="class")
    def category_id(self):
        """Create unique category before tests, delete after tests."""
        cid = None
        base = None
        try:
            category_name = f"Automation Test Category {uuid.uuid4().hex[:8]}"
            category_description = "Created by Automation Test Suite"

            base = Config.BASE_URL.rstrip("/")
            create_url = base + Config.ENDPOINTS["create_category"]
            payload = {"name": category_name, "description": category_description}

            # CREATE
            status, body = safe_request("post", create_url, headers=Config.HEADERS, json=payload)
            print_api_response("Create Category Fixture", payload, body)
            assert status in (200, 201), f"Create failed: status={status}, body={body}"

            # extract id (response may wrap the object under "data")
            cid = _extract_id(body)
            assert cid, f"No category id found in creation response: {body}"

            # validate response values inside "data" if present
            data = body.get("data") if isinstance(body, dict) else {}
            assert data.get("name") == category_name, f"Unexpected name in response: {data}"
            assert data.get("description") == category_description, f"Unexpected description in response: {data}"

            yield cid  # provide category id to tests

        except Exception as e:
            print(f"Error in category creation: {e}")
            yield None

        finally:
            # CLEANUP
            try:
                if cid and base:
                    del_url = base + Config.ENDPOINTS["delete_category"].format(id=cid)
                    d_status, d_body = safe_request("delete", del_url, headers=Config.HEADERS)
                    if d_status not in (200, 204):
                        print(f"Warning: cleanup delete returned {d_status}, body={d_body}")
            except Exception as e:
                print(f"Warning: cleanup delete raised exception: {e}")

    # ---------------- CRUD TESTS ---------------- #

    def test_post_create_category(self, category_id):
        """Verify category creation returns valid id."""
        try:
            assert category_id is not None, "category_id fixture did not yield an id"
        except Exception as e:
            pytest.fail(f"Category creation test failed: {e}")


    def test_get_list_categories(self, category_id):
        """Verify created category exists in list."""
        try:
            base = Config.BASE_URL.rstrip("/")
            list_url = base + Config.ENDPOINTS["list_categories"]
            status, body = safe_request("post", list_url, headers=Config.HEADERS)
            print_api_response("List Categories Test", None, body)
            assert status == 200, f"List categories failed: status={status}, body={body}"
            assert "data" in body, f"Unexpected list response shape: {body}"

            # ensure our category exists in the list
            data = body.get("data")
            categories = data.get("categories") if isinstance(data, dict) else data
            assert any(cat.get("id") == category_id for cat in categories if isinstance(cat, dict)), \
                "Created category not found in list"
        except Exception as e:
            pytest.fail(f"List categories test failed: {e}")


    def test_put_update_category(self, category_id):
        """Verify category update API updates name/description correctly."""
        try:
            base = Config.BASE_URL.rstrip("/")
            update_url = base + Config.ENDPOINTS["update_category"].format(id=category_id)
            updated_name = "Updated Automation Category"
            updated_desc = "Updated by pytest"
            payload = {"name": updated_name, "description": updated_desc}

            status, body = safe_request("put", update_url, headers=Config.HEADERS, json=payload)
            print_api_response("Update Category Test", payload, body)
            assert status in (200, 201), f"Update failed: status={status}, body={body}"
            assert isinstance(body, dict), f"Unexpected update response: {body}"

            # response payload places the updated object under "data"
            data = body.get("data") if isinstance(body, dict) else None
            assert data and isinstance(data, dict), f"No 'data' object in response: {body}"
            assert data.get("name") == updated_name
            assert data.get("description") == updated_desc
        except Exception as e:
            pytest.fail(f"Update category test failed: {e}")


    def test_delete_category(self, category_id):
        """Verify category delete API removes the category."""
        try:
            base = Config.BASE_URL.rstrip("/")
            del_url = base + Config.ENDPOINTS["delete_category"].format(id=category_id)
            status, body = safe_request("delete", del_url, headers=Config.HEADERS)
            print_api_response("Delete Category Test", None, body)

            # confirm deletion by checking list
            list_url = base + Config.ENDPOINTS["list_categories"]
            l_status, l_body = safe_request("post", list_url, headers=Config.HEADERS)
            print_api_response("Verify Deletion - List Categories", None, l_body)
            if l_status == 200 and "data" in l_body:
                data = l_body.get("data")
                categories = data.get("categories") if isinstance(data, dict) else data
                assert all(cat.get("id") != category_id for cat in categories if isinstance(cat, dict)), \
                    "Deleted category still found in list"
        except Exception as e:
            pytest.fail(f"Delete category test failed: {e}")


    # add schema validation test similar to test_login_response_schema
    def test_category_response_schema(self, category_id):
        """
        Validate category list response schema by validating the first category item
        against Config.CATEGORY_SCHEMA (keeps style similar to test_login_response_schema).
        """
        try:
            base = Config.BASE_URL.rstrip("/")
            list_url = base + Config.ENDPOINTS["list_categories"]

            resp = requests.post(list_url, headers=Config.HEADERS, timeout=Config.REQUEST_TIMEOUT)
            body = print_api_response("Schema validation for category list response", None, resp)

            # fallback to JSON parsing if utility returned None
            try:
                if body is None:
                    body = resp.json()
            except Exception:
                try:
                    body = json.loads(resp.text)
                except Exception:
                    body = resp.text

            assert resp.status_code == 200, f"Expected 200 on list categories, got {resp.status_code}"

            # extract first category item
            data = body.get("data") if isinstance(body, dict) else {}
            categories = data.get("categories") if isinstance(data, dict) else data
            assert isinstance(categories, list) and categories, f"No categories array in response: {body}"
            first = categories[0]

            try:
                validate(instance=first, schema=Config.CATEGORY_SCHEMA)
                print("Category item schema validation passed")
            except ValidationError as ve:
                pytest.fail(f"Category schema validation failed: {ve}\nItem: {json.dumps(first, indent=2, ensure_ascii=False)}")
        except Exception as e:
            pytest.fail(f"Unexpected error in test_category_response_schema: {e}\n{traceback.format_exc()}")
