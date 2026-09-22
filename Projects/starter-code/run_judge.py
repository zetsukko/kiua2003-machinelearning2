"""run_judge.py: load a saved transcript JSON and judge it for real
(against Ollama by default, or --mock to test the plumbing offline).

Usage:
    python run_judge.py transcripts/manhwa_debate.json
    python run_judge.py transcripts/manhwa_debate.json --mock
"""
import argparse
import json

from engine import Entry
from judge import judge
from llm_client import make_client


def load_transcript(path):
    with open(path) as f:
        data = json.load(f)
    return [Entry(**m) for m in data["messages"]]


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("path", help="path to a saved transcript JSON, e.g. transcripts/manhwa_debate.json")
    p.add_argument("--mock", action="store_true", help="use MockClient instead of a real model")
    args = p.parse_args()

    transcript = load_transcript(args.path)
    print(f"Loaded {len(transcript)} messages from {args.path}\n")
    for e in transcript:
        print(f"{e.speaker}: {e.content}\n")

    client = make_client(mock=args.mock)
    verdict = judge(transcript, client=client)

    print("--- Judge verdict ---")
    print(json.dumps(verdict, indent=2))
