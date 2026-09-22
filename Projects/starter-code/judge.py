import json
from llm_client import make_client

def judge(transcript, client=None, model="llama3.2:3b"):
    client = client or make_client()
    conversation = "\n".join(f"{e.speaker}: {e.content}" for e in transcript)
    messages = [
        {"role": "system", "content": "You are a judge. Read the dialogue and respond "
         "with JSON: {\"score\": 1-5, \"success\": true/false, \"reason\": \"...\"}"},
        {"role": "user", "content": conversation},
    ]
    reply = client.chat(model, messages, temperature=0)
    try:
        return json.loads(reply.text)
    except json.JSONDecodeError:
        return {"score": 0, "success": False, "reason": "invalid JSON from judge"}