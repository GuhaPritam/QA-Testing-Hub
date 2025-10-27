"""
Validates API responses against schemas.

Example:
    validate_response_schema(
        response.json(),    # API response
        Config.SCHEMA,      # Schema to validate against
        "Login"             # Schema name
    )
"""

import json
import pytest
from jsonschema import validate, ValidationError
from Api.Automation.Src.Utils.print_api_utils import print_api_response

def validate_response_schema(body, schema, schema_name="Response"):
    try:
        # Handle response object if passed
        if hasattr(body, 'json'):
            try:
                body = body.json()
            except Exception:
                body = body.text

        # Ensure we have valid JSON
        if isinstance(body, str):
            try:
                body = json.loads(body)
            except Exception as e:
                pytest.fail(f"Invalid JSON response: {e}\nBody: {body}")

        # Perform schema validation
        validate(instance=body, schema=schema)
        print(f"{schema_name} schema validation passed")
        return True

    except ValidationError as ve:
        print_api_response(f"{schema_name} Schema Validation Failed", None, body)
        pytest.fail(f"{schema_name} schema validation failed: {ve}")
    except Exception as e:
        pytest.fail(f"Unexpected error validating {schema_name}: {e}")