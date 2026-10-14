import json
from pathlib import Path
from jsonschema import Draft202012Validator

SCHEMA = json.loads((Path(__file__).parent / "schema.json").read_text(encoding="utf-8"))
schema_validator = Draft202012Validator(SCHEMA)


def strip_fence(text):
    # Models sometimes wrap JSON in ```json ... ``` even when told not to.
    text = text.strip()
    if text.startswith("```"):
        lines = text.split("\n")
        lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        text = "\n".join(lines)
    return text


def validate(raw_text, retrieved_ids):
    """Returns (ok, errors, parsed). Never raises: the caller feeds errors back on retry."""
    try:
        parsed = json.loads(strip_fence(raw_text))
    except json.JSONDecodeError as e:
        return False, [f"Output is not valid JSON: {e}"], None

    errors = []

    # 1. Shape and field rules (schema.json)
    for err in schema_validator.iter_errors(parsed):
        where = ".".join(str(p) for p in err.absolute_path) or "(root)"
        errors.append(f"Schema: {where}: {err.message}")

    # 2. Cited chunks must be ones the model was actually shown
    if isinstance(parsed, dict) and isinstance(parsed.get("citations"), list):
        for cid in parsed["citations"]:
            if cid not in retrieved_ids:
                errors.append(f"Citation {cid} was not in the retrieved chunks")

    return len(errors) == 0, errors, parsed
