import json
import time

import pytest
import requests
import re
import threading
import traceback
from Api.Automation.Src.Config.config import Config
from jsonschema import validate, ValidationError
from Api.Automation.Src.Utils.print_api_utils import print_api_response
from Api.Automation.Src.Utils.schema_validation_utils import validate_response_schema
from concurrent.futures import ThreadPoolExecutor, as_completed


class TestLoginAPI:
    """Comprehensive Login API tests: positive, negative, edge, security, integration, performance."""

    # ---------- Positive Tests using utility ----------
    def test_login_success_token(self, auth_token):
        """Verify login succeeds and returns valid (header.payload.signature) JWT token from utility function."""
        try:
            token = auth_token
            assert token is not None, "Token should not be None"
            assert isinstance(token, str), f"Token should be string, got {type(token)}"
            assert re.match(r"^[A-Za-z0-9-_]+\.[A-Za-z0-9-_]+\.[A-Za-z0-9-_]+$", token), "Invalid JWT format"
        except Exception as e:
            pytest.fail(f"Unexpected error in test_login_success_token: {e}\n{traceback.format_exc()}")

    def test_token_allows_access_to_protected_endpoint(self, auth_token):
        """Token from utility function works for protected API."""
        try:
            token = auth_token
            url = Config.BASE_URL.rstrip("/") + Config.ENDPOINTS["protected_endpoint"]
            resp = requests.get(url, headers=Config.HEADERS, timeout=Config.REQUEST_TIMEOUT)
            assert resp.status_code in [200, 404], f"Expected 200 or 404, got {resp.status_code}"
            if resp.status_code == 200:
                body = resp.json()
                print(json.dumps(body, indent=4, ensure_ascii=False))
            elif resp.status_code == 404:
                print("\n No data found for this endpoint — valid 404 case.")
        except Exception as e:
            pytest.fail(
                f"Unexpected error in test_token_allows_access_to_protected_endpoint: {e}\n{traceback.format_exc()}")

    # ---------- Negative / Validation ----------
    @pytest.mark.parametrize("email,password,role", [
        (Config.ADMIN_EMAIL, Config.WRONG_PASSWORD, Config.ADMIN_ROLE),
        (Config.WRONG_EMAIL, Config.ADMIN_PASSWORD, Config.ADMIN_ROLE),
        (Config.WRONG_EMAIL, Config.WRONG_PASSWORD, Config.ADMIN_ROLE),
        (Config.ADMIN_EMAIL, Config.ADMIN_PASSWORD, Config.WRONG_ROLE),
    ])
    def test_login_invalid_credentials(self, email, password, role):
        """Invalid credentials or role returns proper error code."""
        try:
            url = Config.BASE_URL.rstrip("/") + Config.ENDPOINTS["login"]
            payload = {"email": email, "password": password, "role": role}

            resp = requests.post(url, json=payload, timeout=Config.REQUEST_TIMEOUT)
            body = print_api_response("Testing invalid credentials", payload, resp)

            assert resp.status_code in [400], \
                f"Expected 400/401/403, got {resp.status_code} for {email}, {role}"

            assert "error" in body or "message" in body, \
                f"No error/message key found in response for {email}, {role}"
        except Exception as e:
            pytest.fail(
                f"Unexpected error in test_login_invalid_credentials ({email}, {role}): {e}\n{traceback.format_exc()}")

    @pytest.mark.parametrize("payload", [
        {"email": Config.ADMIN_EMAIL},  # missing password
        {"password": Config.ADMIN_PASSWORD},  # missing email
        {},  # empty
        {"email": None, "password": None},  # null values
    ])
    def test_login_missing_fields(self, payload):
        """Missing or null fields return validation error."""
        try:
            url = Config.BASE_URL.rstrip("/") + Config.ENDPOINTS["login"]
            resp = requests.post(url, json=payload, timeout=Config.REQUEST_TIMEOUT)
            body = print_api_response("Testing missing/null fields", payload, resp)

            assert resp.status_code in [400, 422], f"Expected 400/422, got {resp.status_code} for payload={payload}"
            assert "error" in body or "message" in body, f"No error/message key found in response for payload={payload}"
        except Exception as e:
            pytest.fail(
                f"Unexpected error in test_login_missing_fields (payload={payload}): {e}\n{traceback.format_exc()}")

    def test_login_invalid_email_format(self):
        """Invalid email format rejected."""
        try:
            url = Config.BASE_URL.rstrip("/") + Config.ENDPOINTS["login"]
            payload = {"email": "invalid_email", "password": "1234", "role": Config.ADMIN_ROLE}

            resp = requests.post(url, json=payload, timeout=Config.REQUEST_TIMEOUT)
            body = print_api_response("Testing invalid email format", payload, resp)

            assert resp.status_code in [400, 422], \
                f"Expected 400/422, got {resp.status_code} for payload={payload}"
            assert "error" in body or "message" in body, \
                f"No error/message key found in response for payload={payload}"
        except Exception as e:
            pytest.fail(f"Unexpected error in test_login_invalid_email_format: {e}\n{traceback.format_exc()}")

    def test_login_empty_body(self):
        """Empty raw body fails."""
        try:
            url = Config.BASE_URL.rstrip("/") + Config.ENDPOINTS["login"]
            payload = {}
            resp = requests.post(url, data="", timeout=Config.REQUEST_TIMEOUT)
            body = print_api_response("Testing empty body", payload, resp)

            # Assertions
            assert resp.status_code in [400, 422], \
                f"Expected 400/422, got {resp.status_code} for payload={payload}"
            assert "error" in body or "message" in body, \
                f"No error/message key found in response for payload={payload}"
        except Exception as e:
            pytest.fail(f"Unexpected error in test_login_empty_body: {e}\n{traceback.format_exc()}")

    def test_login_long_input(self):
        """Very long email/password handled gracefully."""
        try:
            url = Config.BASE_URL.rstrip("/") + Config.ENDPOINTS["login"]
            payload = {
                "email": "a" * 10000 + "@example.com",
                "password": "b" * 10000,
                "role": Config.ADMIN_ROLE,
            }
            resp = requests.post(url, json=payload, timeout=Config.REQUEST_TIMEOUT)
            body = print_api_response("Testing very long input", payload, resp)

            # Assertions
            assert resp.status_code in [400, 413], \
                f"Expected 400/413, got {resp.status_code} for payload={payload}"
            assert "error" in body or "message" in body, \
                f"No error/message key found in response for payload={payload}"
        except Exception as e:
            pytest.fail(f"Unexpected error in test_login_long_input: {e}\n{traceback.format_exc()}")

    # ---------- HTTP Method Validation ----------
    @pytest.mark.parametrize("method", ["get", "put", "delete", "patch"])
    def test_login_invalid_methods(self, method):
        """Non-POST methods return 405."""
        try:
            url = Config.BASE_URL.rstrip("/") + Config.ENDPOINTS["login"]
            resp = getattr(requests, method)(url, timeout=Config.REQUEST_TIMEOUT)
            payload = {"method": method}
            body = print_api_response(f"Testing invalid HTTP method: {method.upper()}", payload, resp)

            # Assertions
            assert resp.status_code in [404, 405], \
                f"Expected 405 or 404, got {resp.status_code} for method={method}"
            if isinstance(body, dict):
                assert "error" in body or "message" in body, \
                    f"No error/message key found in response for method={method}"
        except Exception as e:
            pytest.fail(
                f"Unexpected error in test_login_invalid_methods (method={method}): {e}\n{traceback.format_exc()}")

    # ---------- Performance / Concurrency ----------
    def test_parallel_logins_auto_timeout(self, num_users=50):
        """
        Simulate multiple parallel logins without manually setting a timeout.
        The function measures time taken for each request and total execution.
        """
        try:
            url = Config.BASE_URL.rstrip("/") + Config.ENDPOINTS["login"]

            payload = {
                "email": Config.ADMIN_EMAIL,
                "password": Config.ADMIN_PASSWORD,
                "role": Config.ADMIN_ROLE
            }

            results = []

            def do_login(index):
                start = time.time()
                try:
                    resp = requests.post(url, json=payload)
                    duration = time.time() - start
                    return index, resp.status_code, duration
                except requests.RequestException as e:
                    duration = time.time() - start
                    return index, f"Error: {e}", duration
                except Exception as e:
                    duration = time.time() - start
                    return index, f"Error: {e}", duration

            start_all = time.time()
            with ThreadPoolExecutor(max_workers=num_users) as executor:
                futures = [executor.submit(do_login, i) for i in range(num_users)]
                for future in as_completed(futures):
                    try:
                        idx, status, duration = future.result()
                        results.append((idx, status, duration))
                        print(f"Login {idx}: {status} (Time taken: {duration:.2f} sec)")
                    except Exception as e:
                        # capture any worker exception
                        pytest.fail(
                            f"Worker raised exception in test_parallel_logins_auto_timeout: {e}\n{traceback.format_exc()}")

            total_time = time.time() - start_all
            print(f"\nTotal time for {num_users} users: {total_time:.2f} sec")
        except Exception as e:
            pytest.fail(f"Unexpected error in test_parallel_logins_auto_timeout: {e}\n{traceback.format_exc()}")

    def test_login_response_schema(self):
        """Validate login endpoint response schema."""
        try:
            url = Config.BASE_URL.rstrip("/") + Config.ENDPOINTS["login"]
            payload = {
                "email": Config.ADMIN_EMAIL,
                "password": Config.ADMIN_PASSWORD,
                "role": Config.ADMIN_ROLE
            }

            resp = requests.post(url, json=payload, timeout=Config.REQUEST_TIMEOUT)
            body = print_api_response("Login Schema Validation", payload, resp)

            assert resp.status_code in [200, 201], f"Expected 200/201, got {resp.status_code}"
            validate_response_schema(body, Config.LOGIN_SCHEMA, "Login Response")

        except Exception as e:
            pytest.fail(f"Login schema validation failed: {e}")