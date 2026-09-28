from judge import judge
from llm_client import make_client

# Specific, on-topic, and each side responds directly to the other's point.
GOOD_TRANSCRIPT = [
    {"speaker": "SungJinFan",
     "content": "Solo Leveling's power system directly ties Jin-Woo's shadow army to his "
                "emotional arc - System notifications like 'Rank Up' mirror his growth from "
                "E-rank to Monarch, which is a concrete storytelling choice."},
    {"speaker": "TowerOfGodFan",
     "content": "That's specific, but Tower of God's Position system ties power directly to "
                "social standing within the Tower - the difference is ToG layers in the "
                "Guardians and Workshops as competing factions, adding political complexity "
                "Solo Leveling never attempts."},
    {"speaker": "SungJinFan",
     "content": "Political complexity is exactly why casual readers drop ToG - Solo Leveling "
                "keeps its cast small so every named character has a clear stake, which is "
                "why the Jeju Island arc lands emotionally."},
    {"speaker": "TowerOfGodFan",
     "content": "A small cast limits stakes long-term though - once Jin-Woo becomes the "
                "strongest there's no tension left, whereas Bam's group keeps evolving with "
                "new rivals even after Bam gains power."},
]

# Vague, repetitive, nobody engages with the other side's point.
BAD_TRANSCRIPT = [
    {"speaker": "SungJinFan", "content": "Solo Leveling is just better, it's really good."},
    {"speaker": "TowerOfGodFan", "content": "No, Tower of God is better, I like it more."},
    {"speaker": "SungJinFan", "content": "Well I still think Solo Leveling is better."},
    {"speaker": "TowerOfGodFan", "content": "Yeah I disagree, Tower of God wins."},
]


def main():
    client = make_client(mock=False)  # the judge needs the real model to actually reason

    good_result = judge(GOOD_TRANSCRIPT, client)
    bad_result = judge(BAD_TRANSCRIPT, client)

    print("Good transcript judged:", good_result)
    print("Bad transcript judged:", bad_result)

    assert good_result["score"] > bad_result["score"], \
        "Expected the specific, on-topic debate to score higher than the vague one - " \
        "if this fails, the rubric in judge.py needs work"

    print("\njudge sanity check: OK (good debate scored higher than bad debate)")


if __name__ == "__main__":
    main()
