import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    BASE_URL = os.getenv("BASE_URL")
    REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", 10))

    ENDPOINTS = {
        "login": os.getenv("ENDPOINT_LOGIN"),
        "create_category": os.getenv("ENDPOINT_CREATE_CATEGORY"),
        "list_categories": os.getenv("ENDPOINT_LIST_CATEGORIES"),
        "update_category": os.getenv("ENDPOINT_UPDATE_CATEGORY"),
        "delete_category": os.getenv("ENDPOINT_DELETE_CATEGORY"),
    }

    ADMIN_EMAIL = os.getenv("ADMIN_EMAIL")
    ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")
    ADMIN_ROLE = os.getenv("ADMIN_ROLE")

    # Wrong credentials for negative test
    WRONG_EMAIL = os.getenv("WRONG_EMAIL")
    WRONG_PASSWORD = os.getenv("WRONG_PASSWORD")
    WRONG_ROLE = os.getenv("WRONG_ROLE")

    HEADERS = {}
