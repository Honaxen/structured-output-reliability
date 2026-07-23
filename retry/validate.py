"""
Validates model output against a JSON schema in two stages: first,
whether the output is even parseable JSON at all; second, whether that
JSON conforms to the schema. Both failure modes are common and distinct
-- a model can produce syntactically broken JSON (missing a closing
brace, trailing comma) or produce perfectly valid JSON that's simply
missing required fields or has the wrong types.

Returns a structured result with a specific, human-readable error
message on failure -- that message is what retry/retry_loop.py feeds
back to the model as correction feedback, so the error needs to be
precise enough to actually be fixable, not just "invalid".

Usage:
    from validate import validate_output
    result = validate_output(raw_text, schema)
    if not result["valid"]:
        print(result["error"])
"""

import json
import re

from jsonschema import validate as jsonschema_validate
from jsonschema import ValidationError


def extract_json_block(raw_text: str) -> str | None:
    """
    Extracts the first {...} block from raw text, tolerating surrounding
    prose ("Here's the JSON: {...}"). Returns None if no brace-delimited
    block is found at all -- a different failure mode than "found a block
    but it doesn't parse", and worth distinguishing in the error message.
    """
    match = re.search(r"\{.*\}", raw_text, re.DOTALL)
    return match.group(0) if match else None


def validate_output(raw_text: str, schema: dict) -> dict:
    """
    Returns:
        {"valid": True, "parsed": <dict>}
        or
        {"valid": False, "error": "<specific, actionable message>", "stage": "extraction" | "parsing" | "schema"}
    """
    json_block = extract_json_block(raw_text)
    if json_block is None:
        return {
            "valid": False,
            "stage": "extraction",
            "error": "No JSON object (content wrapped in { }) was found in the response at all. "
                     "The response must contain a JSON object.",
        }

    try:
        parsed = json.loads(json_block)
    except json.JSONDecodeError as e:
        return {
            "valid": False,
            "stage": "parsing",
            "error": f"The extracted content is not valid JSON syntax: {str(e)}. "
                     f"Check for issues like missing commas, unquoted keys, or trailing commas.",
        }

    try:
        jsonschema_validate(instance=parsed, schema=schema)
    except ValidationError as e:
        # e.json_path (or e.path for older jsonschema versions) pinpoints
        # exactly which field failed -- passing that through, not just
        # "schema validation failed", is what makes the retry feedback
        # specific enough for the model to actually fix.
        path = ".".join(str(p) for p in e.absolute_path) or "(root)"
        return {
            "valid": False,
            "stage": "schema",
            "error": f"JSON is syntactically valid but does not conform to the required schema. "
                     f"Problem at '{path}': {e.message}",
        }

    return {"valid": True, "parsed": parsed}
