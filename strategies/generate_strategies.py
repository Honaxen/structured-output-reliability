"""
Three strategies for getting a model to produce JSON conforming to a
schema, from loosest to most constrained:

  1. plain       -- task prompt + a one-line "respond as JSON" instruction.
                     No schema shown, no examples.
  2. few_shot     -- task prompt + the schema shown explicitly + one
                     worked example of correctly formatted output.
  3. native_json  -- Ollama's format="json" parameter, which constrains
                     decoding at the token level (the model literally
                     cannot emit a token that would break JSON syntax).
                     This guarantees syntactic validity but NOT schema
                     conformance -- valid JSON can still have the wrong
                     fields or types, which is exactly why this project
                     tests both validation stages separately.

Keeping these as three clearly separate functions (not parameterized
variations of one function) makes it easy to compare their prompts
side by side and makes each strategy's assumptions explicit rather than
buried in conditional logic.

Usage:
    from generate_strategies import generate_plain, generate_few_shot, generate_native_json
    raw_output = generate_plain(model, task_prompt)
"""

import json
import urllib.request

OLLAMA_URL = "http://localhost:11434/api/generate"

# A fixed, schema-independent example used for the few-shot strategy.
# Deliberately unrelated to any schema in schemas/schema_dataset.py --
# the point is showing the model *the shape of a well-formed answer*,
# not giving it something to pattern-match against the actual task.
FEW_SHOT_EXAMPLE = """Example task: Describe a book titled 'The Old Lighthouse' by author Mara Voss, published in 2019.
Example schema: {"title": "string", "author": "string", "year": "integer"}
Example correct output: {"title": "The Old Lighthouse", "author": "Mara Voss", "year": 2019}"""


def _call_ollama(model: str, prompt: str, format_json: bool = False, timeout: int = 60) -> str:
    payload = {"model": model, "prompt": prompt, "stream": False}
    if format_json:
        payload["format"] = "json"

    request = urllib.request.Request(
        OLLAMA_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        body = json.loads(response.read().decode("utf-8"))
        return body.get("response", "").strip()


def generate_plain(model: str, task_prompt: str) -> str:
    """Weakest strategy: just asks for JSON, shows nothing about structure."""
    prompt = f"{task_prompt}\n\nRespond with the information as JSON."
    return _call_ollama(model, prompt)


def generate_few_shot(model: str, task_prompt: str, schema: dict) -> str:
    """Stronger strategy: shows the actual schema and one worked example
    of correctly formatted (but unrelated) output."""
    prompt = (
        f"{FEW_SHOT_EXAMPLE}\n\n"
        f"Now do the same for this task.\n"
        f"Task: {task_prompt}\n"
        f"Required schema: {json.dumps(schema)}\n"
        f"Respond with ONLY the JSON object matching this schema, no other text."
    )
    return _call_ollama(model, prompt)


def generate_native_json(model: str, task_prompt: str, schema: dict) -> str:
    """
    Strongest syntactic guarantee: Ollama's format="json" constrains
    token-level decoding so the output is guaranteed to be syntactically
    valid JSON. Still includes the schema in the prompt text, since
    format="json" alone only guarantees valid JSON *syntax* -- it does
    not know or enforce which fields are required or their types.
    """
    prompt = (
        f"Task: {task_prompt}\n"
        f"Required schema: {json.dumps(schema)}\n"
        f"Respond with the JSON object matching this schema."
    )
    return _call_ollama(model, prompt, format_json=True)


STRATEGIES = {
    "plain": lambda model, entry: generate_plain(model, entry["task_prompt"]),
    "few_shot": lambda model, entry: generate_few_shot(model, entry["task_prompt"], entry["schema"]),
    "native_json": lambda model, entry: generate_native_json(model, entry["task_prompt"], entry["schema"]),
}
