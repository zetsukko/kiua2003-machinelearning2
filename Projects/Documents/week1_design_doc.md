# Week 1 Design Doc

## Scenario

Category: **Debate**

Two manhwa fans arguing about which series is the GOAT.

- **SungJinFan** — die-hard Solo Leveling stan. All about the art, the power
  progression, and Jin-Woo's whole arc.
- **TowerOfGodFan** — Tower of God devotee. Thinks Solo Leveling is
  overrated and argues ToG wins on worldbuilding and mystery.

Topic: "Solo Leveling is the greatest manhwa of all time."

## The two personas (full system prompts)

**SungJinFan:**
```
You argue IN FAVOUR of the topic. Be brief: 2 sentences max.
```

**TowerOfGodFan:**
```
You argue AGAINST the topic. Be brief: 2 sentences max.
```

(Note: right now these are the generic Pro/Con prompts from `ping_pong.py`
with just the agent names swapped to match the manhwa scenario — I haven't
written manhwa-specific system prompts yet. That's the next thing to fix,
see "Next steps" below.)

## What "goal reached" means

Since this is a **Debate** scenario, the goal isn't for the two agents to
agree — debates don't need to converge. Following the pattern from the
Project Brief (a 3rd judge agent picks a winner after N rounds), I'm
defining goal-reached like this:

- The debate runs for a fixed number of rounds (currently capped by
  `Budget(max_turns=...)`, e.g. 8 turns).
- **Goal reached = a judge agent reads the full transcript and declares
  which side made the stronger case**, based on: did they use concrete
  details (character names, plot points, actual arguments) rather than
  vague claims, and did they respond directly to the other side's points
  instead of just repeating themselves.
- I haven't built the judge yet — that's a Week 2/3 thing (`goal_reached`
  is literally a parameter `DialogueEngine` already supports, I just need
  to write the judging function). For now, "goal reached" is defined but
  not yet automatically tested — the current runs stop purely on
  `max_turns`, not on goal completion.

## First try: mock mode

```
python ping_pong.py --mock
```

8 turns, ~634-814 tokens, basically instant, stopped because it hit
max_turns.

The loop itself worked fine — turns alternated, budget tracked everything,
stopped when it was supposed to. But the actual replies were kind of
random and had nothing to do with manhwa ("I think we should weigh the
costs before anything else"?). Turns out MockClient just cycles through 6
hardcoded lines no matter what you feed it — it doesn't even look at the
system prompt or topic. Makes sense though, it's just there to test that
the plumbing works without needing a real model.

## Second try: real model (Ollama, llama3.2:3b)

```
python ping_pong.py
```

8 turns, 3018 tokens, 44.2 seconds, stopped on max_turns again.

This time it was actually good. SungJinFan kept hammering that Solo
Leveling's bleakness is intentional and "authentic," ToG fan kept saying
Solo Leveling's themes are one-note compared to ToG's layered
worldbuilding. Neither one backed down — they argued the whole 8 turns and
never agreed on anything, which honestly tracks for this kind of fan
debate lol. (Funny enough the mock run randomly ended on "Agreed, I think
that's our common ground" — which obviously wasn't a real agreement, just
a coincidence from the canned replies.)

Quick comparison:

| | Mock | Real |
|---|---|---|
| Tokens | ~634-814 | 3018 |
| Time | instant | 44.2s |
| Actually on-topic | no | yes |
| Ended in agreement | yes (coincidence) | no |

Basically: mock mode is great for checking your loop doesn't break, but
you don't get real content out of it. Real model = way more tokens and
time, but you actually get a debate that makes sense.

## Thing I noticed about ping_pong.py

The way it builds the prompt is kind of janky — it dumps the ENTIRE
conversation so far into one big "user" message every single turn, for
both agents:

```python
messages = [
    {"role": "system", "content": f"{speaker.system_prompt}\n..."},
    {"role": "user", "content": f"Conversation so far:\n{render(transcript)}\n\n..."},
]
```

So neither agent actually knows which lines were theirs and which were the
other person's — it's all just one wall of text. Also this means the
prompt keeps growing every turn since you're resending the whole history,
which is going to be a problem eventually if the conversation runs long.

Guessing this is exactly what engine.py's view_for() is supposed to fix in
Week 2 — giving each agent its own lines as "assistant" and the other
agent's lines as "user" so it actually knows who's who. Week 3 sounds like
it'll deal with the growing-prompt problem.

## Next steps

- Write manhwa-specific system prompts for SungJinFan and TowerOfGodFan
  instead of reusing the generic Pro/Con text from ping_pong.py.
- Build the judge function for goal_reached once I'm in Week 2's
  DialogueEngine.
