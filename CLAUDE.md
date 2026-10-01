# Project conventions

<!-- The agent reads this at the start of every session. Keep it short and current.
     Graded: does it reflect how the team actually works? -->

## What this repository is
The Week 3 lab for CPSC 415: a command-line program that classifies one customer-support message into JSON (category, urgency, reason) through a model on OpenRouter, plus an eval that runs five known cases against two models. The design is in [`spec.md`](spec.md); the intent is in [`intent/classifier.md`](intent/classifier.md).

## Commands
```
# build: none (Python, no packages)
# test:  python3 eval.py
# run:   python3 classifier.py "the support message"
# lint:  none
```

## Conventions
- Language: Python, standard library only; code must run on Python 3.9 or later.
- Default model: `minimax/minimax-m3` through OpenRouter. Comparison model: `xiaomi/mimo-v2.6-flash`. Configuration comes only from the environment: `CHAT_BASE_URL`, `CHAT_MODEL`, `OPENROUTER_API_KEY`. No key or secret in code or in the repo.
- File naming: lowercase snake_case (`classifier.py`, `eval.py`, `cases.json`).
- Eval cases live in `cases.json`; run results and the model comparison go in `CHECKS.md`.

## Working rules

For an introductory lab, follow its explicitly assigned stages; the full chain below applies to major projects. Week 1 uses its own minimal repository.

- This is the Week 3 introductory lab. Stages assigned: intent and spec.
  No plan.md, no branches or pull requests. Commit to main.
- Standard library only, except that Java may add one JSON library jar.
- Commits are authored by Lane Faison. Never add Co-Authored-By or any AI attribution trailer to a commit message.
- Write or update `intent/` and `spec.md` before code. Get `plan.md` approved before implementing.
- One feature per branch and pull request. Never push to `main` directly.
- Never commit `.env` or `.claude/settings.local.json`.

## Common mistakes
Things the agent got wrong before and must not repeat. Add to this list as they happen.
