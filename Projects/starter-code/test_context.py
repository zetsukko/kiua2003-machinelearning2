"""test_context.py: proves that manage_context (truncate_context) keeps the
message list sent to the model bounded on a long-running conversation,
instead of growing every turn without limit.

Run:
    python test_context.py
"""
from agents import Agent
from budget import Budget
from engine import DialogueEngine, truncate_context, view_for
from llm_client import MockClient

MAX_MESSAGES = 10  # cap used for the "with management" run

agents = [
    Agent(name="SungJinFan", system_prompt="You argue IN FAVOUR. Be brief.",
          model="llama3.2:3b", temperature=0.7),
    Agent(name="TowerOfGodFan", system_prompt="You argue AGAINST. Be brief.",
          model="llama3.2:3b", temperature=0.7),
]


def sizes_over_time(engine, transcript, step=5):
    """Message-list length view_for would produce, sampled every `step` turns."""
    out = []
    for i in range(0, len(transcript), step):
        view = view_for(agents[i % 2], transcript[:i])
        view = engine.manage_context(view)
        out.append(len(view))
    return out


# --- Run 1: NO context management. Message list grows every turn. ---
budget_a = Budget(max_turns=30, max_tokens=1_000_000, max_seconds=1000)
engine_a = DialogueEngine(agents, MockClient(), budget_a)  # manage_context defaults to no-op
transcript_a = engine_a.run()
sizes_a = sizes_over_time(engine_a, transcript_a)

# --- Run 2: WITH context management. Message list caps at MAX_MESSAGES. ---
budget_b = Budget(max_turns=30, max_tokens=1_000_000, max_seconds=1000)
engine_b = DialogueEngine(
    agents, MockClient(), budget_b,
    manage_context=lambda m: truncate_context(m, max_messages=MAX_MESSAGES),
)
transcript_b = engine_b.run()
sizes_b = sizes_over_time(engine_b, transcript_b)

print(f"Message-list length over the run, sampled every 5 turns (30 turns total):")
print(f"  WITHOUT context management: {sizes_a}")
print(f"  WITH    context management: {sizes_b}  (capped at {MAX_MESSAGES})")
print()
if sizes_a[-1] > MAX_MESSAGES and sizes_b[-1] <= MAX_MESSAGES:
    print("Confirmed: without management the list keeps growing; "
          "with management it stays bounded.")
else:
    print("MISMATCH — check the values above.")
