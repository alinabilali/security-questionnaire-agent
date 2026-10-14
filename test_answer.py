import json
import os
import tempfile
from answer import answer_question, build_user_message

CHUNKS = [
    {"id": "BR-1.1", "doc": "backup-dr", "title": "Backup schedule", "text": "Daily incremental, weekly full."},
    {"id": "DP-2.1", "doc": "data-protection", "title": "Customer data after contract end", "text": "30 days."},
]
USAGE = {"input_tokens": 1000, "output_tokens": 100}

GOOD = json.dumps({"answer": "Daily incremental, weekly full.", "citations": ["BR-1.1"],
                   "confidence": "high", "answerable": True, "conflict": False})
BAD_CITATION = json.dumps({"answer": "x", "citations": ["ZZ-9.9"], "confidence": "high",
                           "answerable": True, "conflict": False})
SILENT = json.dumps({"answer": "", "citations": [], "confidence": "low",
                     "answerable": False, "conflict": False})


def scripted(replies):
    """A fake model that returns the given replies in order and records what it was sent."""
    sent = []
    def fake(system, user):
        sent.append(user)
        return replies[len(sent) - 1], USAGE
    return fake, sent


def run(name, replies, expect_route, expect_attempts):
    fake, sent = scripted(replies)
    trace = os.path.join(tempfile.mkdtemp(), "t.jsonl")
    out = answer_question("How often are backups performed?", CHUNKS, model_fn=fake, trace_path=trace)
    lines = open(trace).read().strip().split("\n")
    assert out["route"] == expect_route, (name, out)
    assert out["attempts"] == expect_attempts, (name, out)
    assert len(lines) == expect_attempts, (name, "trace lines", len(lines))
    print(f"PASS  {name}: route={out['route']!r} attempts={out['attempts']} cost=${out['cost_usd']:.6f}")
    return sent


run("good answer is drafted", [GOOD], "draft", 1)
run("docs silent is escalated", [SILENT], "needs human review", 1)

sent = run("bad then good: retry succeeds", [BAD_CITATION, GOOD], "draft", 2)
assert "ZZ-9.9" in sent[1], "retry message should include the validator error"
print("PASS  retry message carries the error back to the model")

run("bad twice: escalated after one retry", [BAD_CITATION, "not json"], "needs human review", 2)

msg = build_user_message("Q?", CHUNKS)
assert '<chunk id="BR-1.1"' in msg and "<question>" in msg
print("PASS  prompt wraps chunks and question in tags")

print("all answer tests passed")
