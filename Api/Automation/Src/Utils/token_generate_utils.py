"""
Gets authentication token and sets up headers for API requests.
Required before making any protected API calls.

Basic usage:
    token = get_jwt_token()  # This will set up Config.HEADERS automatically
"""

import requests
from Api.Automation.Src.Config.config import Config

def get_jwt_token():
    """Get JWT token and configure request headers."""
    # Build login URL from base URL and endpoint
    url = Config.BASE_URL.rstrip("/") + Config.ENDPOINTS["login"]

    # Prepare login credentials from config
    payload = {
        "email": Config.ADMIN_EMAIL,
        "password": Config.ADMIN_PASSWORD,
        "role": Config.ADMIN_ROLE,
    }

    # Make login request
    resp = requests.post(url, json=payload, timeout=Config.REQUEST_TIMEOUT)
    resp.raise_for_status()  # Raises exception for 4XX/5XX status codes
    body = resp.json()

    # Extract token from different possible response formats
    token = (
        body.get("token") or                                  # Format: {"token": "xyz"}
        body.get("access_token") or                          # Format: {"access_token": "xyz"}
        (body.get("data", {}).get("token", {}).get("access")) # Format: {"data":{"token":{"access":"xyz"}}}
    )

    # Ensure token was found
    if not token:
        raise ValueError(f"Login failed: token missing in response: {body}")

    # Set up headers for future API requests
    Config.HEADERS = {
        "Authorization": f"Bearer {token}",  # Add token as Bearer token
        "Content-Type": "application/json"   # Set JSON content type
    }
    print("-- [ info ] --Token generated successfully and added to headers.")
    return token
