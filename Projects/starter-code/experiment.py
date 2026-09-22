"""experiment.py: WEEK 3 experiment - vary ONE parameter across >=3 runs,
judge each, and build a results table.

Parameter varied here: temperature (applied to both agents equally, so the
comparison is fair - only one thing changes between runs).

Usage:
    python experiment.py --config configs/debate.yaml --mock   # debug the plumbing, free
    python experiment.py --config configs/debate.yaml          # real numbers, real model

Each run is saved as its own transcript: transcripts/experiment_temp_<T>.json
"""
import argparse
import copy
import json

import yaml

from agents import Agent
from budget import Budget
from engine import DialogueEngine
from judge import judge
from llm_client import make_client

TEMPERATURES = [0.3, 0.7, 1.2]  # the one parameter we vary, everything else fixed


def run_one(cfg, temperature, client, judge_client):
    """Run the dialogue once at the given temperature, judge it, return a result row."""
    cfg = copy.deepcopy(cfg)
    for a in cfg["agents"]:
        a["temperature"] = temperature

    agents = [Agent(**a) for a in cfg["agents"]]
    budget = Budget(**cfg.get("budget", {}))
    engine = DialogueEngine(agents, client, budget)
    transcript = engine.run()

    out_path = f"transcripts/experiment_temp_{temperature}.json"
    engine.save(out_path, meta={"topic": cfg.get("topic"), "temperature": temperature})

    verdict = judge(transcript, client=judge_client)

    return {
        "temperature": temperature,
        "turns": budget.turns,
        "tokens": budget.tokens,
        "seconds": round(budget.elapsed, 2),
        "stop_reason": budget.stop_reason,
        "judge_score": verdict.get("score"),
        "judge_success": verdict.get("success"),
        "judge_winner": verdict.get("winner"),
        "transcript_file": out_path,
    }


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--config", required=True, help="base config, e.g. configs/debate.yaml")
    p.add_argument("--mock", action="store_true", help="use MockClient (free, for testing the plumbing)")
    args = p.parse_args()

    with open(args.config) as f:
        base_cfg = yaml.safe_load(f)

    results = []
    for t in TEMPERATURES:
        # Fresh client per run so mock's reply cycle restarts identically each time.
        client = make_client(mock=args.mock)
        judge_client = make_client(mock=args.mock)
        print(f"--- Running at temperature={t} ---")
        row = run_one(base_cfg, t, client, judge_client)
        results.append(row)
        print(row, "\n")

    # Results table.
    print("\n| Temperature | Turns | Tokens | Seconds | Stop reason | Judge score | Success | Winner |")
    print("|---|---|---|---|---|---|---|---|")
    for r in results:
        print(f"| {r['temperature']} | {r['turns']} | {r['tokens']} | {r['seconds']} | "
              f"{r['stop_reason']} | {r['judge_score']} | {r['judge_success']} | {r['judge_winner']} |")

    with open("transcripts/experiment_results.json", "w") as f:
        json.dump(results, f, indent=2)
    print("\nSaved transcripts/experiment_results.json")
