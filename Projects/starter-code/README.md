# AgentCom: manhwa debate

Two agents debate whether "Solo Leveling is the greatest manhwa of all
time." One argues for it (SungJinFan), one argues against it
(TowerOfGodFan). A separate judge agent scores the finished debate.

## Setup

```
pip install -r requirements.txt
```

You also need [Ollama](https://ollama.com) installed, with the model
pulled:

```
ollama pull llama3.2:3b
```

Don't have Ollama, or working offline? Add `--mock` to any command below
and it uses canned replies instead of a real model. Good for checking
things run without waiting on real model calls.

## Run the main scenario

```
python run.py --config configs/debate.yaml
```

This runs the debate for 8 turns, prints it, and saves it to
`transcripts/manhwa_debate.json`.

## Judge a transcript

```
python run_judge.py transcripts/manhwa_debate.json
```

Scores the debate (1-5), says whether it counts as a success, gives a
reason, and picks a winner. Saves that verdict back into the same JSON
file. Add `--mock` to test this without a real model call.

## Run the experiment (varies temperature)

```
python experiment.py --config configs/debate.yaml
```

Runs the same debate 3 times at temperature 0.3, 0.7, and 1.2, judges each
one, and prints a results table. Saves each run as its own file in
`transcripts/`.

## See a deliberate failure

```
python run.py --config configs/failure_sycophancy.yaml
python run_judge.py transcripts/failure_sycophancy.json
```

Both agents get the same neutral prompt instead of opposing ones. This
reliably makes them agree with each other instead of debating, a failure
mode called sycophancy. See the report for what this showed.

## Build the final results table

```
python build_results_table.py
```

Reads every saved transcript in `transcripts/` and prints one table, so
every number is pulled from a real file, not memory.

## Run the tests

```
python test_engine.py      # checks view_for and the main loop
python test_budgets.py     # checks all three budget limits can stop a run
python test_context.py     # checks long runs get truncated correctly
python test_judge.py       # checks the judge scores a good run higher than a bad one
```

## What's in here

- `agents.py`, `budget.py`, `llm_client.py`, `engine.py` - the core engine
  (agent data, the three-limit safety guard, the model client, the
  orchestration loop and role-mapping).
- `judge.py` - scores a finished transcript against a rubric. Separate
  model call, not part of the debate itself.
- `run.py` - runs a single debate from a config file.
- `run_judge.py` - judges a saved transcript and saves the verdict back
  into it.
- `experiment.py` - runs the temperature experiment (3 runs, one
  parameter varied).
- `build_results_table.py` - builds the final results table from saved
  transcripts.
- `configs/debate.yaml` - the manhwa debate config (personas, topic,
  budget).
- `configs/failure_sycophancy.yaml` - the deliberate-failure config
  (identical prompts, no opposing roles).
- `transcripts/` - every saved run, including judge verdicts. This is the
  evidence behind the report.
- `week1_design_doc.md` - scenario, personas, and the goal-reached
  definition, written in Week 1.
- `week3_notes.md` - notes on context management, the judge, and the
  temperature experiment, written in Week 3.

## The one rule

No `while` loop that calls a model exists without a `Budget` controlling
it. All three limits (turns, tokens, seconds) are always active. Checked
directly in `test_budgets.py`.
