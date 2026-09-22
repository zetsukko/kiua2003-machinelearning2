"""test_budgets.py: demonstrates that each of the three Budget limits
(max_turns, max_tokens, max_seconds) can independently stop a run, and that
stop_reason correctly names which one fired.

Run:
    python test_budgets.py
"""
import time

from agents import Agent
from budget import Budget
from engine import DialogueEngine
from llm_client import MockClient


def make_agents():
    return [
        Agent(name="SungJinFan",
              system_prompt="You argue IN FAVOUR. Be brief.",
              model="llama3.2:3b", temperature=0.7),
        Agent(name="TowerOfGodFan",
              system_prompt="You argue AGAINST. Be brief.",
              model="llama3.2:3b", temperature=0.7),
    ]


def run_with(budget, label):
    engine = DialogueEngine(make_agents(), MockClient(), budget)
    transcript = engine.run()
    print(f"{label}: stop_reason={budget.stop_reason!r}, "
          f"turns={budget.turns}, tokens={budget.tokens}, "
          f"seconds={budget.elapsed:.4f}")
    return budget.stop_reason


results = {}

# 1. max_turns should fire first: tight turn cap, everything else loose.
results["max_turns"] = run_with(
    Budget(max_turns=2, max_tokens=100_000, max_seconds=1000),
    "Test 1 (expect max_turns)",
)

# 2. max_tokens should fire first: tight token cap, everything else loose.
#    MockClient counts prompt tokens as word-count of the messages sent, so a
#    small cap like 20 will be exceeded within the first couple of turns,
#    well before 100 turns or 1000 seconds could ever be reached.
results["max_tokens"] = run_with(
    Budget(max_turns=100, max_tokens=20, max_seconds=1000),
    "Test 2 (expect max_tokens)",
)

# 3. max_seconds should fire first: near-zero time budget, everything else
#    loose. MockClient replies are instant (~0.01s reported), but Budget's
#    wall-clock check uses real elapsed time, so a tiny max_seconds still
#    gets exceeded after the very first turn.
results["max_seconds"] = run_with(
    Budget(max_turns=100, max_tokens=100_000, max_seconds=0.0001),
    "Test 3 (expect max_seconds)",
)

print()
expected = {"max_turns": "max_turns", "max_tokens": "max_tokens", "max_seconds": "max_seconds"}
if all(results[k] == expected[k] for k in expected):
    print("All three budgets independently stopped the run for the correct reason.")
else:
    print("MISMATCH — check the tuning above:", results)
