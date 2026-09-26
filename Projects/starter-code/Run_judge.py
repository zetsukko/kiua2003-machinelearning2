import argparse
import json

from judge import judge
from llm_client import make_client


def main(path, mock):
    with open(path) as f:
        data = json.load(f)

    client = make_client(mock=mock)
    verdict = judge(data["messages"], client)

    # This is the structured field the loop reads back afterwards: the
    # verdict gets saved into the same transcript file, not just printed.
    data["judge"] = verdict

    with open(path, "w") as f:
        json.dump(data, f, indent=2)

    print("Judge verdict:", verdict)
    print(f"Saved back into {path}")


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("transcript", help="path to a saved transcript json file")
    p.add_argument("--mock", action="store_true", help="use the free offline MockClient")
    args = p.parse_args()
    main(args.transcript, mock=args.mock)