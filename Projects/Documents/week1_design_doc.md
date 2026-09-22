# Design doc — AgentCom (KIUA2003 / KIUA2005-1)

## Scenario: Socratic tutor
I picked this here because it has a clean, checkable success condition (the student
says the target idea in their own words), and it fits from my ML
coursework: the tutor teaching the concept of **overfitting** without
saying the word.

## Personas

**Tutor (Agent A)**
```
You are a patient Socratic tutor teaching the concept of OVERFITTING in machine learning.
Never say the word 'overfitting' yourself, and never explain the answer directly.
Ask one guiding question at a time, and react to what the student just said.
Be brief: 2-3 sentences max.
```

**Student (Agent B)**
```
You are a student learning about machine learning models. You do not yet understand
why a model can do great on training data but poorly on new data. Answer the tutor's
questions honestly, thinking out loud, in your own words.
Be brief: 2-3 sentences max.
```

## Goal reached — measurable definition
The student states the target idea in their own words, before the tutor has
used the word "overfitting" themselves.

**Week 1 detection (deliberately rough):** substring check — does "overfit"
appear anywhere in a Student message? This is a placeholder. As the brief
warns, it fires too early: the student could pick up and repeat the word
without actually understanding the idea behind it. Week 3's judge agent
replaces this with something that checks for understanding, not vocabulary.

## What I noticed in the first run
(fill this in right after running `ping_pong.py --mock` and then the real
model — what surprised you, what broke, whether the student converged
quickly or needed a lot of nudging. This is the raw material for the Week 4
report, so write it down now while it's fresh.)