import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    BASE_URL = os.getenv("BASE_URL")
    ADMIN_TOKEN = os.getenv("ADMIN_TOKEN")
    REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", 10))

    ENDPOINTS = {
        "create_category": os.getenv("ENDPOINT_CREATE_CATEGORY"),
        "list_categories": os.getenv("ENDPOINT_LIST_CATEGORIES"),
        "update_category": os.getenv("ENDPOINT_UPDATE_CATEGORY"),
        "delete_category": os.getenv("ENDPOINT_DELETE_CATEGORY"),
    }

    HEADERS = {
        "Authorization": f"Bearer {ADMIN_TOKEN}",
        "Content-Type": "application/json"
    }
