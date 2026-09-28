"""results_table.py: builds a results table from saved, judged transcripts.

Every number in this table comes from the saved JSON files, not from memory -
that's the rule the brief sets for the final report.

The agreement/pushback columns come from agreement_check.py (a plain word
count, no model), because the judge could not tell the failed run apart.

Run:  python results_table.py transcripts/debate_temp03.json transcripts/debate_temp07.json transcripts/debate_temp12.json transcripts/failure_identical.json
"""
import argparse
import json
import os

from agreement_check import AGREE_PHRASES, PUSHBACK_PHRASES, count_phrases


def load_row(path):
    with open(path) as f:
        data = json.load(f)

    # Use the file name as the run name, e.g. "debate_temp03"
    run_name = os.path.basename(path).replace(".json", "")

    judge_info = data.get("judge", {})

    # Count agreement and pushback phrases over every message in the run
    agree = 0
    pushback = 0
    for message in data["messages"]:
        agree += count_phrases(message["content"], AGREE_PHRASES)
        pushback += count_phrases(message["content"], PUSHBACK_PHRASES)

    return {
        "run": run_name,
        "temperature": data["agents"][0]["temperature"],
        "turns": data["budget"]["turns"],
        "tokens": data["budget"]["tokens"],
        "seconds": data["budget"]["seconds"],
        "stop_reason": data["budget"]["stop_reason"],
        "judge_score": judge_info.get("score", "-"),
        "success": judge_info.get("success", "-"),
        "agree": agree,
        "pushback": pushback,
    }


def print_table(rows):
    header = ("Run", "Temp", "Turns", "Tokens", "Seconds", "Stop reason",
              "Judge score", "Success", "Agree", "Pushback")
    print(" | ".join(header))
    print(" | ".join("-" * len(h) for h in header))
    for row in rows:
        print(" | ".join(str(v) for v in [
            row["run"], row["temperature"], row["turns"], row["tokens"],
            row["seconds"], row["stop_reason"], row["judge_score"],
            row["success"], row["agree"], row["pushback"],
        ]))


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("transcripts", nargs="+", help="paths to saved, judged transcript json files")
    args = p.parse_args()

    # Keep the rows in the order you typed the files, so the failed run can go last
    rows = [load_row(path) for path in args.transcripts]
    print_table(rows)
