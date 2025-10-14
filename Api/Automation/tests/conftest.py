import pytest
from Api.Automation.Src.Utils.token_generate_utils import get_jwt_token

@pytest.fixture(scope="session")
def auth_token():
    """Generate token once per session and return it."""
    token = get_jwt_token()
    return token
