import pytest
import requests
from ..src.config import Config
from ..src.token_generate import get_jwt_token

class TestLogin:

    def test_login_success(self):
        token = get_jwt_token()
        assert token is not None
        assert isinstance(token, str)

    def test_login_failure(self):
        url = Config.BASE_URL + Config.ENDPOINTS["login"]
        wrong_payload = {
            "email": "wronguser@yopmail.com",
            "password": "wrongpass",
            "role": "ADMIN",
        }
        with pytest.raises(requests.exceptions.HTTPError):
            resp = requests.post(url, json=wrong_payload, timeout=Config.REQUEST_TIMEOUT)
            resp.raise_for_status()
