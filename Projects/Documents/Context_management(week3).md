Context management (Week 3)


The problem: every turn, the code is sending the whole conversations so far back into the model.
This means that the prompt keeps on growing longer and the debate is running - I can see this in the debate.json where 
prompt_tokens goes on from 73 on turn 0 up to 495 by turn7.
If ab debate is running long enough it would eventually overflow the model's context window entirely.

I fixed with truncation: Keeping the system prompt (always needed so that the agent knows it role), 
plus only the most recent 20 messages, and drop anything that is older.
I picked truncation over summarizing the old messages because summarizing would mean and extra model call every time you compress
more tokens, more time, more complexity and since the debate agents mainly respond to whatever the other one just said,
i dont think much about cutting off stuff from much earlier in the conversation.

I have tested this with the Test_context.py, simulation a 30-turn conversation. 
Without truncation, the message list kept on growing the whole time: 2, 6, 11, 21, 30 messages at turns 0/5/10/20/29.
With truncate_context wired in (window of 20), it capped at 21 messages and stayed flat once the conversation got long enough: 2, 6, 11, 21, 21.
The console also printed a log line each time it actually trimmed something (e.g. "trimmed 9 old message(s), keeping last 20"),
so I could confirm it was actively cutting messages, not just doing nothing. 

One tradeoff worth noting: with only a 20-message window, an agent in a very long debate would eventually "forget" the earliest arguments made.
For an 8-turn debate like mine that's not really an issue, but it's the honest cost of this approach.