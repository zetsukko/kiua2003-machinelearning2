"""token_growth.py: prints how many tokens each turn used, from a saved transcript.

Every number comes from the saved file, so it is safe to quote in the report.
It shows the prompt growing every turn, because the whole conversation is
sent again each time (until truncation kicks in).

Run:  python token_growth.py transcripts/debate_temp07.json
"""
import argparse
import json


def main(path):
    with open(path) as f:
        data = json.load(f)

    print(f"File: {path}")
    print("Turn | Speaker | Prompt tokens | Reply tokens | Seconds")
    print("---- | ------- | ------------- | ------------ | -------")
    for m in data["messages"]:
        print(f"{m['turn_index']} | {m['speaker']} | {m['prompt_tokens']} | "
              f"{m['completion_tokens']} | {round(m['seconds'], 2)}")

    totals = data["totals"]
    print(f"Total: {totals['prompt_tokens']} prompt tokens, "
          f"{totals['completion_tokens']} reply tokens, {totals['seconds']} seconds")


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("transcript", help="path to a saved transcript json file")
    args = p.parse_args()
    main(args.transcript)