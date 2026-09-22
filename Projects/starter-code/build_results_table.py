"""build_results_table.py: scans transcripts/*.json and builds one results
table from the saved data - not from memory. Run this AFTER you've run all
your experiment configs and judged them with run_judge.py.

Usage:
    python build_results_table.py
"""
import glob
import json
import os

rows = []
for path in sorted(glob.glob("transcripts/*.json")):
    with open(path) as f:
        data = json.load(f)

    # Skip files that aren't a single saved transcript (e.g. experiment.py's
    # own summary file, or this script's own output on a re-run).
    if not isinstance(data, dict) or "messages" not in data:
        continue

    meta = data.get("meta", {})
    budget = data.get("budget", {})
    judge = data.get("judge", {})  # only present if run_judge.py was run on this file

    rows.append({
        "file": os.path.basename(path),
        "topic": meta.get("topic", meta.get("config", "?")),
        "temperature": meta.get("temperature", "-"),
        "turns": budget.get("turns", "-"),
        "tokens": budget.get("tokens", "-"),
        "seconds": budget.get("seconds", "-"),
        "stop_reason": budget.get("stop_reason", "-"),
        "judge_score": judge.get("score", "not judged"),
        "judge_success": judge.get("success", "not judged"),
        "winner": judge.get("winner", "not judged"),
    })

print(f"Found {len(rows)} transcripts in transcripts/\n")
print("| File | Temp | Turns | Tokens | Seconds | Stop reason | Score | Success | Winner |")
print("|---|---|---|---|---|---|---|---|---|")
for r in rows:
    print(f"| {r['file']} | {r['temperature']} | {r['turns']} | {r['tokens']} | "
          f"{r['seconds']} | {r['stop_reason']} | {r['judge_score']} | "
          f"{r['judge_success']} | {r['winner']} |")

with open("transcripts/final_results_table.json", "w") as f:
    json.dump(rows, f, indent=2)
print("\nSaved transcripts/final_results_table.json")
