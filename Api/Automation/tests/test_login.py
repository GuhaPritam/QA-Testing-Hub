import pytest
import requests
from Api.Automation.Src.Config.config import Config
from Api.Automation.Src.Utils.token_generate_utils import get_jwt_token

class TestLogin:

    def test_login_success(self):
        token = get_jwt_token()
        assert token is not None
        assert isinstance(token, str)

    def test_login_failure(self):
        url = Config.BASE_URL + Config.ENDPOINTS["login"]
        wrong_payload = {
            "email": Config.WRONG_EMAIL,
            "password": Config.WRONG_PASSWORD,
            "role": Config.WRONG_ROLE,
        }
        with pytest.raises(requests.exceptions.HTTPError):
            resp = requests.post(url, json=wrong_payload, timeout=Config.REQUEST_TIMEOUT)
            resp.raise_for_status()
