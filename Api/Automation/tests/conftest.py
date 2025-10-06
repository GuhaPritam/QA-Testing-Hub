import pytest
from Api.Automation.src.utils.token_generate_utils import get_jwt_token


@pytest.fixture(scope="session", autouse=True)
def authenticate():
    get_jwt_token()
    yield
