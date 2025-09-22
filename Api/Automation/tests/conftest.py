import pytest
from Api.Automation.src.token_generate import get_jwt_token


@pytest.fixture(scope="session", autouse=True)
def authenticate():
    get_jwt_token()
    yield
