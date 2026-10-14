import json
from validator import validate

RETRIEVED = ["BR-1.1", "DP-2.1", "BR-3.1"]


def check(name, raw, expect_ok):
    ok, errors, _ = validate(raw, RETRIEVED)
    status = "PASS" if ok == expect_ok else "FAIL"
    print(f"{status}  {name}")
    for e in errors:
        print("        ", e)
    assert ok == expect_ok, name


good = {"answer": "Daily incremental, weekly full.", "citations": ["BR-1.1"],
        "confidence": "high", "answerable": True, "conflict": False}
silent = {"answer": "", "citations": [], "confidence": "low",
          "answerable": False, "conflict": False}
conflict = {"answer": "DP-2.1 says 30 days, BR-3.1 says 90 days.",
            "citations": ["DP-2.1", "BR-3.1"], "confidence": "medium",
            "answerable": False, "conflict": True}

check("good answer (case 2)", json.dumps(good), True)
check("docs silent (cases 10-12)", json.dumps(silent), True)
check("conflict (case 13)", json.dumps(conflict), True)
check("fenced JSON is accepted", "```json\n" + json.dumps(good) + "\n```", True)

check("not JSON", "Sure! Here is the answer.", False)
check("silent but answer given", json.dumps({**silent, "answer": "No, we are not certified."}), False)
check("answerable but no citation", json.dumps({**good, "citations": []}), False)
check("conflict with one citation", json.dumps({**conflict, "citations": ["DP-2.1"]}), False)
check("citation not retrieved", json.dumps({**good, "citations": ["ZZ-9.9"]}), False)
check("bad confidence value", json.dumps({**good, "confidence": "certain"}), False)
check("missing field", json.dumps({k: v for k, v in good.items() if k != "conflict"}), False)

print("all validator tests passed")
