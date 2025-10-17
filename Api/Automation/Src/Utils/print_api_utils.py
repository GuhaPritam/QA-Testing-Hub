def print_api_response(test_name, payload, resp):
    """Reusable print function for API test debug info."""
    try:
        body = resp.json()
    except Exception:
        body = resp.text  # fallback if not JSON

    print("\n------------------------------------------------")
    print(f"🔹 {test_name}")
    print(f"   Payload : {payload}")
    print(f"   → Response Code : {resp.status_code}")
    print(f"   → Response Body : {body}")
    print("------------------------------------------------")
    return body
