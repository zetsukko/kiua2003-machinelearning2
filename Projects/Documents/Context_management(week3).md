Context management (Week 3)


The problem: every turn, the code sends the whole conversation so far back
into the model. This means that the prompt keeps growing longer as the
debate runs. I can see this in transcripts/debate_temp07.json, where
prompt_tokens goes from 94 on turn 0 up to 792 on turn 7.
If a debate ran long enough, it would eventually overflow the model's
context window entirely.

I fixed this with truncation: I keep the system prompt (always needed so that
the agent knows its role), plus only the most recent 20 messages, and drop
anything older. I picked truncation over summarizing the old messages because
summarizing would mean an extra model call every time I compress: more tokens,
more time, more complexity. The debate agents mainly respond to whatever the
other one just said, so I don't think I lose much by cutting off older messages.

I have tested this with the Test_context.py, simulation a 30-turn conversation. 
Without truncation, the message list kept on growing the whole time: 2, 6, 11, 21, 30 messages at turns 0/5/10/20/29.
With truncate_context wired in (window of 20), it capped at 21 messages and stayed flat once the conversation got long enough: 2, 6, 11, 21, 21.
The console also printed a log line each time it actually trimmed something (e.g. "trimmed 9 old message(s), keeping last 20"),
so I could confirm it was actively cutting messages, not just doing nothing. 

One tradeoff: with only a 20-message window, an agent in a very long debate
would eventually "forget" the earliest arguments. My real debates only ran 8
turns, so they never reached the 20-message window. I proved the truncation
works with test_context.py on a 30-turn conversation instead.