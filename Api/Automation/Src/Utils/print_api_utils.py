"""
API Response Debug Utility
-------------------------
Purpose: Print formatted API request/response details for:
- Test debugging & troubleshooting
- Response validation
- API behavior monitoring

Usage:
    print_api_response("Test Name", payload, response)

Output format:
    Test Name
    Payload sent
    Response status (if applicable)
    Response body (formatted JSON)
"""

import json

def print_api_response(test_name, payload, resp):
    """Reusable print function for API test debug info."""
    print("\n------------------------------------------------")
    print(f"🔹 {test_name}")
    print(f"   Payload : {payload}")

    # Handle Response object, dict, or string gracefully
    if hasattr(resp, "status_code"):  # requests.Response
        try:
            body = resp.json()
        except Exception:
            body = getattr(resp, "text", str(resp))
        print(f"   → Response Code : {resp.status_code}")
        print(f"   → Response Body : {json.dumps(body, indent=2)}")
    elif isinstance(resp, dict):
        print(f"   → Response Body : {json.dumps(resp, indent=2)}")
        body = resp
    else:
        print(f"   → Response Body : {resp}")
        body = resp

    print("------------------------------------------------")
    return body
