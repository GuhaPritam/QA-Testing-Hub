import pytest
from Api.Automation.Src_ff.Utils.token_generate_utils import get_jwt_token

# session-level storage
SESSION_TOKEN = None

@pytest.fixture(scope="session", autouse=True)
def authenticate():
    global SESSION_TOKEN
    SESSION_TOKEN = get_jwt_token()  # auto-run, store token
    yield

@pytest.fixture(scope="session")
def auth_token():
    return SESSION_TOKEN  # reuse same token
