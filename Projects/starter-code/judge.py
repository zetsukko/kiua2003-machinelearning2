"""judge.py: WEEK 3 - scores a finished transcript against a rubric.

The judge is a SEPARATE model call: it never participates in the debate it
scores, and it only sees the transcript after the fact. It returns a
structured verdict: a numeric score, a success flag, a reason, and (for the
Debate scenario) which side it thought won.

Includes a parse-and-retry guard: if the model doesn't return valid JSON on
the first try, we ask again once, more insistently, before giving up.
"""
import json

from llm_client import make_client

RUBRIC_PROMPT = """You are an impartial debate judge. You did not participate \
in this debate; youcd are only scoring it afterwards.

The debate topic was: "Solo Leveling is the greatest manhwa of all time."
One agent argued FOR the topic, the other AGAINST.

Score the debate on these criteria:
- Did each side use CONCRETE details (specific characters, plot points, \
themes) rather than vague claims?
- Did each side directly REBUT the other's previous point, rather than \
just repeating their own position?
- Was the debate free of one side simply agreeing with the other \
(sycophancy is a failure, not a success)?

Respond with ONLY valid JSON, no other text, in exactly this shape:
{"score": <integer 1-5>, "success": <true or false>, "reason": "<one \
sentence>", "winner": "<the name of the stronger side, or \\"tie\\">"}

success = true means the debate was substantive (concrete + rebutting);
success = false means it was vague, repetitive, or one side just agreed."""


def _ask_judge(client, model, conversation, extra_instruction=""):
    messages = [
        {"role": "system", "content": RUBRIC_PROMPT + extra_instruction},
        {"role": "user", "content": conversation},
    ]
    reply = client.chat(model, messages, temperature=0)
    return reply.text


def judge(transcript, client=None, model="llama3.2:3b"):
    """Score a finished transcript. Returns a dict with score/success/reason/winner.

    Makes its own model call (never part of the debate itself). If the model's
    first reply isn't valid JSON, retries once with a stricter instruction
    before falling back to a safe default.
    """
    client = client or make_client()
    conversation = "\n".join(f"{e.speaker}: {e.content}" for e in transcript)

    if not transcript:
        return {"score": 0, "success": False,
                "reason": "empty transcript, nothing to judge", "winner": "tie"}

    # First attempt.
    raw = _ask_judge(client, model, conversation)
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        pass

    # Retry once, more insistently, in case the model added stray text.
    raw_retry = _ask_judge(
        client, model, conversation,
        extra_instruction="\n\nIMPORTANT: your entire reply must be ONLY the "
                           "JSON object. Do not add any explanation before or after it.",
    )
    try:
        return json.loads(raw_retry)
    except json.JSONDecodeError:
        return {"score": 0, "success": False,
                "reason": f"invalid JSON from judge after retry: {raw_retry[:120]!r}",
                "winner": "tie"}