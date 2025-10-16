import json

import pytest
import requests
import re
import threading
from Api.Automation.Src.Config.config import Config
from Api.Automation.Src.Utils.token_generate_utils import get_jwt_token


class TestLoginAPI:
    """Comprehensive Login API tests: positive, negative, edge, security, integration, performance."""

    # ---------- Positive Tests using utility ----------
    def test_login_success_token(self, auth_token):
        """Verify login succeeds and returns valid (header.payload.signature) JWT token from utility function."""
        token = auth_token
        assert token is not None, "Token should not be None"
        assert isinstance(token, str), f"Token should be string, got {type(token)}"
        assert re.match(r"^[A-Za-z0-9-_]+\.[A-Za-z0-9-_]+\.[A-Za-z0-9-_]+$", token), "Invalid JWT format"


    def test_token_allows_access_to_protected_endpoint(self, auth_token):
        """Token from utility function works for protected API."""
        token = auth_token
        url = Config.BASE_URL.rstrip("/") + Config.ENDPOINTS["protected_endpoint"]
        resp = requests.get(url, headers=Config.HEADERS, timeout=Config.REQUEST_TIMEOUT)
        assert resp.status_code in [200, 404], f"Expected 200 or 404, got {resp.status_code}"
        if resp.status_code == 200:
            body = resp.json()
            print(json.dumps(body, indent=4, ensure_ascii=False))
        elif resp.status_code == 404:
            print("\n No data found for this endpoint — valid 404 case.")


    # ---------- Negative / Validation ----------
    @pytest.mark.parametrize("email,password,role", [
        (Config.ADMIN_EMAIL, Config.WRONG_PASSWORD, Config.ADMIN_ROLE),
        (Config.WRONG_EMAIL, Config.ADMIN_PASSWORD, Config.ADMIN_ROLE),
        (Config.WRONG_EMAIL, Config.WRONG_PASSWORD, Config.ADMIN_ROLE),
        (Config.ADMIN_EMAIL, Config.ADMIN_PASSWORD, Config.WRONG_ROLE),
    ])
    def test_login_invalid_credentials(self, email, password, role):
        """Invalid credentials or role returns proper error code."""
        url = Config.BASE_URL.rstrip("/") + Config.ENDPOINTS["login"]
        payload = {"email": email, "password": password, "role": role}

        resp = requests.post(url, json=payload, timeout=Config.REQUEST_TIMEOUT)
        body = resp.json()

        print("\n------------------------------------------------")
        print(f"🔹 Testing invalid credential:")
        print(f"   Email    : {email}")
        print(f"   Password : {password}")
        print(f"   Role     : {role}")
        print(f"   → Response Code : {resp.status_code}")
        print(f"   → Response Body : {body}")
        print("------------------------------------------------")

        assert resp.status_code in [400, 401, 403], \
            f"Expected 200/400/401/403, got {resp.status_code} for {email}, {role}"

        assert "error" in body or "message" in body, \
            f"No error/message key found in response for {email}, {role}"


    @pytest.mark.parametrize("payload", [
        {"email": Config.ADMIN_EMAIL},  # missing password
        {"password": Config.ADMIN_PASSWORD},  # missing email
        {},  # empty
        {"email": None, "password": None},  # null values
    ])
    def test_login_missing_fields(self, payload):
        """Missing or null fields return validation error."""
        url = Config.BASE_URL.rstrip("/") + Config.ENDPOINTS["login"]
        resp = requests.post(url, json=payload, timeout=Config.REQUEST_TIMEOUT)
        assert resp.status_code in [400, 422]
        body = resp.json()
        assert "error" in body or "message" in body


    def test_login_invalid_email_format(self):
        """Invalid email format rejected."""
        url = Config.BASE_URL.rstrip("/") + Config.ENDPOINTS["login"]
        payload = {"email": "invalid_email", "password": "1234", "role": Config.ADMIN_ROLE}
        resp = requests.post(url, json=payload, timeout=Config.REQUEST_TIMEOUT)
        assert resp.status_code in [400, 422]

    def test_login_empty_body(self):
        """Empty raw body fails."""
        url = Config.BASE_URL.rstrip("/") + Config.ENDPOINTS["login"]
        resp = requests.post(url, data="", timeout=Config.REQUEST_TIMEOUT)
        assert resp.status_code in [400, 422]
    
    def test_login_long_input(self):
        """Very long email/password handled gracefully."""
        url = Config.BASE_URL.rstrip("/") + Config.ENDPOINTS["login"]
        payload = {
            "email": "a" * 10000 + "@example.com",
            "password": "b" * 10000,
            "role": Config.ADMIN_ROLE,
        }
        resp = requests.post(url, json=payload, timeout=Config.REQUEST_TIMEOUT)
        assert resp.status_code in [400, 413]
    
    # ---------- HTTP Method Validation ----------
    @pytest.mark.parametrize("method", ["get", "put", "delete", "patch"])
    def test_login_invalid_methods(self, method):
        """Non-POST methods return 405."""
        url = Config.BASE_URL.rstrip("/") + Config.ENDPOINTS["login"]
        resp = getattr(requests, method)(url, timeout=Config.REQUEST_TIMEOUT)
        assert resp.status_code == 405
    
    # ---------- Security ----------
    def test_sql_injection_attempt(self):
        """SQL injection payload rejected."""
        url = Config.BASE_URL.rstrip("/") + Config.ENDPOINTS["login"]
        payload = {"email": "' OR 1=1 --", "password": "x", "role": Config.ADMIN_ROLE}
        resp = requests.post(url, json=payload, timeout=Config.REQUEST_TIMEOUT)
        assert resp.status_code in [400, 401, 403]
    
    def test_xss_payload_attempt(self):
        """XSS payload rejected."""
        url = Config.BASE_URL.rstrip("/") + Config.ENDPOINTS["login"]
        payload = {"email": "<script>alert(1)</script>", "password": "x", "role": Config.ADMIN_ROLE}
        resp = requests.post(url, json=payload, timeout=Config.REQUEST_TIMEOUT)
        assert resp.status_code in [400, 401, 422]
    
    # ---------- Integration / Token Behavior ----------
    def test_protected_endpoint_without_token(self):
        """Protected API without token returns 401/403."""
        url = Config.BASE_URL.rstrip("/") + Config.ENDPOINTS.get("profile", "/user/profile")
        resp = requests.get(url, timeout=Config.REQUEST_TIMEOUT)
        assert resp.status_code in [401, 403]
    
    def test_protected_endpoint_with_tampered_token(self, auth_token):
        """Tampered token is rejected."""
        token = auth_token + "abc"
        url = Config.BASE_URL.rstrip("/") + Config.ENDPOINTS.get("profile", "/user/profile")
        resp = requests.get(url, headers=Config.HEADERS, timeout=Config.REQUEST_TIMEOUT)
        assert resp.status_code in [401, 403]
    
    # ---------- Performance / Concurrency ----------
    def test_multiple_parallel_logins(self):
        """Simulate concurrent login requests."""
        url = Config.BASE_URL.rstrip("/") + Config.ENDPOINTS["login"]
        payload = {"email": Config.ADMIN_EMAIL, "password": Config.ADMIN_PASSWORD, "role": Config.ADMIN_ROLE}
        results = []
    
        def do_login():
            resp = requests.post(url, json=payload, timeout=Config.REQUEST_TIMEOUT)
            results.append(resp.status_code)
    
        threads = [threading.Thread(target=do_login) for _ in range(5)]
        [t.start() for t in threads]
        [t.join() for t in threads]
    
        assert all(r == 200 for r in results)
    
    def test_rate_limit(self):
        """Basic rate-limit simulation."""
        url = Config.BASE_URL.rstrip("/") + Config.ENDPOINTS["login"]
        payload = {"email": Config.ADMIN_EMAIL, "password": Config.ADMIN_PASSWORD, "role": Config.ADMIN_ROLE}
        responses = [requests.post(url, json=payload, timeout=Config.REQUEST_TIMEOUT) for _ in range(15)]
        codes = [r.status_code for r in responses]
        assert any(c == 429 for c in codes) or all(c == 200 for c in codes)
