# Week 3 Notes

## Keeping the conversation from growing forever (context management)

The problem: every turn, the code sends the WHOLE conversation so far to the
model again. So after 30 turns the message list is huge. Real models can
only "see" so much at once (their context window), so eventually this would
break or the model would just forget the start of the conversation.

The fix I used: `truncate_context()`. It's already in `engine.py`. It just
keeps the system prompt plus the last 20 messages (I tested it with 10 to
make the numbers clearer) and throws away everything older than that.

Why I picked this over the other option (summarizing the old messages into
a shorter version instead of deleting them): truncating is way simpler, and
it doesn't cost extra model calls. Summarizing would keep more info but you'd
have to call the model an extra time just to make the summary, which costs
more tokens and time. Since my agents mostly respond to the last thing the
other one said, not stuff from way earlier, I don't think I'm losing much
by just cutting old messages off.

I proved it works with `test_context.py`, ran a 30-turn conversation with
and without the fix. Without it, the message list kept growing every turn
(2, 6, 11, 16, 21, 26...). With it, it capped out at 10 and just stayed
there. So it does what it's supposed to.

## The judge

`judge.py` reads a finished debate and scores it. It's a totally separate
model call, it's not one of the two debaters, it just reads the transcript
after the fact and gives an opinion. It sends the model a rubric that says:
did both sides use actual specific stuff (character names, plot points)
instead of being vague, and did they actually respond to each other instead
of just repeating themselves.

It gives back JSON with a score (1-5), whether it counts as a "success",
a one-sentence reason, and who it thinks won.

One thing I had to add: sometimes the model doesn't send back valid JSON
(like it adds extra words before/after the JSON). So if the first try fails
to parse, the code asks again one more time, more strictly ("ONLY send the
JSON, nothing else"). If that also fails, it just returns a safe default
instead of crashing.

I checked this actually works two ways:
1. Made a fake "obviously good" debate (specific, on-topic, rebutting) and a
   fake "obviously bad" one (vague, repetitive, "yeah I agree"). The judge
   gave the good one a higher score than the bad one, like it should.
2. Ran it for real on my actual manhwa debate transcript. It gave a 4/5,
   said "success", and called it a tie, and reading the actual transcript
   myself, that's a fair call. Both sides brought up real character/plot
   stuff the whole way through and neither one backed down.

Also: the judge's "winner" wasn't actually being used anywhere before, just
printed and forgotten. I changed `run_judge.py` so now it actually saves
the judge's verdict (score, success, reason, winner) back into the
transcript's JSON file. So now it's a real piece of data that gets kept,
not just text that shows up in the terminal and disappears.

## The experiment

The one thing I changed: temperature (how random/creative the model's
replies are). I ran the same manhwa debate 3 times, at temperature 0.3,
0.7, and 1.2, everything else (personas, topic, turn limit) stayed exactly
the same.

Results:

| Temperature | Turns | Tokens | Seconds | Stop reason | Judge score | Success | Winner |
|---|---|---|---|---|---|---|---|
| 0.3 | 8 | 4456 | 35.87 | max_turns | 4 | True | tie |
| 0.7 | 8 | 3820 | 32.44 | max_turns | 4 | True | tie |
| 1.2 | 8 | 4260 | 34.74 | max_turns | 4 | True | tie |

**The judge score, success, and winner were exactly the same at all three
temperatures.** So by the numbers, temperature didn't matter here. That's a
real result, not a fail, the assignment brief actually says it's fine (and
more honest) to report "no difference" instead of making up a pattern that
isn't really there.

BUT, I actually read all three transcripts, not just the numbers, and
there IS a difference you can see, the judge's simple 1-5 score just didn't
catch it:

- At 0.3, both sides stuck tightly to the topic and just went back and
  forth disagreeing the whole time. Felt the most "debate-like."
- At 0.7, it started drifting a little. One reply brought up other manhwa
  (Black God, Noblesse) that weren't even part of the topic.
- At 1.2, two things got worse: the very first line had a random
  "(The stage is set, let's debate!)" that shouldn't be there, the model
  broke character for a second. Also both sides started saying stuff like
  "that's a fair point, but..." more often, which is a step toward just
  agreeing with each other (the thing the course calls "sycophancy," one
  of the actual failure types we're supposed to watch for).

So my conclusion: temperature didn't change the judge's score in my
experiment, but it did change HOW the debate played out, calmer and more
on-topic at low temperature, a bit looser and more prone to small mistakes
at high temperature. This also shows the judge's score is kind of blunt,
it can miss things that are obviously different if you actually read the
text.

One more thing I noticed, not related to temperature: at every single
temperature, the model made up fake Tower of God character names that
aren't real (like "Han Jisoo," "Chakho," "Park Yeon-jin," "Hansong and
Shai"). That's the model just hallucinating details it doesn't actually
know, and it happened no matter what temperature I used. Keeping this as an
example for the Week 4 failure-analysis part, since hallucination is one of
the failure types we're supposed to find and explain.
