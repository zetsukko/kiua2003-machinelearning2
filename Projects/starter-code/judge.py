import json

JUDGE_PROMPT = """You are an impartial judge scoring a debate transcript.

Score the debate from 1 to 5 based on:
- Did both sides use specific, concrete details (names, examples, real points)
  instead of vague claims?
- Did each side respond directly to what the other side just said, instead
  of just repeating their own point?
- Do the two sides actually disagree and push back on each other? If both
  sides mostly agree, praise each other, or repeat the same ideas with more
  enthusiasm, score 2 or lower, even if the writing sounds detailed.

A debate that stays vague or repetitive should score low (1-2).
A debate where both sides bring up specific details and directly rebut each
other should score high (4-5).

Reply with ONLY a JSON object, nothing else, in exactly this shape:
{"score": <1-5>, "success": <true or false>, "reason": "<one sentence>", "winner": "<name or 'tie'>"}

success should be true if the score is 3 or higher.
"""

RETRY_PROMPT = """Your last reply could not be parsed as JSON.
Reply again with ONLY the JSON object, nothing else. No explanation, no
markdown formatting, just the raw JSON."""


def render_transcript(messages):
    # messages is a list of dicts, each with a "speaker" and "content" key -
    # this matches both a live engine transcript (after asdict) and a saved
    # transcripts/*.json file's "messages" list.
    lines = []
    for m in messages:
        lines.append(f"{m['speaker']}: {m['content']}")
    return "\n".join(lines)


def parse_judge_reply(text):
    # The model sometimes wraps the JSON in extra words or markdown fences.
    # Find the outermost { ... } and try to parse just that part.
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1:
        return None
    try:
        return json.loads(text[start:end + 1])
    except json.JSONDecodeError:
        return None


def judge(messages, client, model="llama3.2:3b"):
    conversation = render_transcript(messages)
    chat_messages = [
        {"role": "system", "content": JUDGE_PROMPT},
        {"role": "user", "content": f"Transcript:\n{conversation}"},
    ]

    reply = client.chat(model, chat_messages, temperature=0)
    result = parse_judge_reply(reply.text)

    if result is None:
        # Parse-and-retry guard: ask once more, more strictly, before giving up.
        chat_messages.append({"role": "assistant", "content": reply.text})
        chat_messages.append({"role": "user", "content": RETRY_PROMPT})
        retry_reply = client.chat(model, chat_messages, temperature=0)
        result = parse_judge_reply(retry_reply.text)

    if result is None:
        # Still failed after retrying - return a safe default instead of crashing.
        return {"score": 0, "success": False,
                "reason": "judge reply could not be parsed as JSON", "winner": "unknown"}

    return result
