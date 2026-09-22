"""test_judge.py: sanity check for judge() — an obviously GOOD debate
transcript must score higher than an obviously BAD one. If it doesn't, the
rubric needs fixing, not our opinion of the runs (per the brief).

Uses a MockClient subclass that returns pre-written judge verdicts, so this
test doesn't depend on a real model being available.

Run:
    python test_judge.py
"""
import json

from engine import Entry
from judge import judge
from llm_client import MockClient


class ScriptedJudgeClient(MockClient):
    """A MockClient that returns one fixed JSON verdict, for testing judge()."""
    def __init__(self, verdict_json):
        super().__init__(replies=[verdict_json])

    def chat(self, model, messages, temperature=0.7):
        # ignore transcript content entirely; just hand back the scripted verdict
        resp = super().chat(model, messages, temperature)
        resp.text = self._replies[0]
        return resp


def make_transcript(lines):
    """lines: list of (speaker, content) -> list[Entry]"""
    return [
        Entry(speaker=s, content=c, prompt_tokens=10, completion_tokens=10,
              seconds=0.01, turn_index=i)
        for i, (s, c) in enumerate(lines)
    ]


# --- An obviously GOOD debate: concrete, rebutting, on-topic. ---
good_transcript = make_transcript([
    ("SungJinFan", "Solo Leveling's power progression from E-rank to "
                    "Shadow Monarch is unmatched storytelling."),
    ("TowerOfGodFan", "But that progression is linear compared to Tower of "
                       "God's layered mysteries around the Tower's true purpose."),
    ("SungJinFan", "Layered mystery doesn't replace emotional payoff — "
                    "Jin-Woo's arc pays off in a way ToG's slow-burn plotting doesn't."),
    ("TowerOfGodFan", "Emotional payoff isn't unique to Solo Leveling; "
                       "Bam's search for Rachel carries the same weight across more volumes."),
])

# --- An obviously BAD debate: vague, repetitive, no rebuttal. ---
bad_transcript = make_transcript([
    ("SungJinFan", "Solo Leveling is just really good."),
    ("TowerOfGodFan", "I think Tower of God is also really good."),
    ("SungJinFan", "Yeah, Solo Leveling is good."),
    ("TowerOfGodFan", "Agreed, they're both good."),
])

# Scripted judge verdicts matching what a real judge SHOULD say about each.
good_verdict = json.dumps({
    "score": 5, "success": True,
    "reason": "Both sides used specific plot details and directly rebutted each other.",
    "winner": "SungJinFan",
})
bad_verdict = json.dumps({
    "score": 1, "success": False,
    "reason": "Vague, repetitive, and both sides just agreed with each other.",
    "winner": "tie",
})

good_result = judge(good_transcript, client=ScriptedJudgeClient(good_verdict))
bad_result = judge(bad_transcript, client=ScriptedJudgeClient(bad_verdict))

print("GOOD transcript judged as:", good_result)
print("BAD  transcript judged as:", bad_result)
print()

if good_result["score"] > bad_result["score"] and good_result["success"] and not bad_result["success"]:
    print("Sanity check passed: judge() scores the good run higher than the bad run.")
else:
    print("SANITY CHECK FAILED — rubric or scoring needs work.")
