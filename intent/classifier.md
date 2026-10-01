# Intent: classifier

## Goal
A command-line program that takes one customer-support message, asks an AI model to classify it, and prints JSON with three fields: `category` (billing, technical, sales, or unknown), `urgency`, and `reason` (one sentence). A separate eval runs five messages with known answers through it and prints PASS or FAIL for each.

## Who it is for
A support team triaging incoming messages, and me, comparing how two models handle a task that needs structured output. Today a person reads each message and decides where it goes.

## Constraints
- Python, standard library only. Must run on Python 3.9 or later.
- Run as `python3 classifier.py "the message"`. One message per run.
- Configuration comes only from environment variables: `CHAT_BASE_URL`, `CHAT_MODEL`, and `OPENROUTER_API_KEY`. No key or secret in the code or the repo.
- `category` is exactly one of billing, technical, sales, unknown. A message that is not a support request at all must be `unknown`.
- `urgency` is exactly one of low, medium, high. **High** means money was lost or the service is down. **Medium** means a feature is broken but there is a workaround. **Low** means a question or a request.
- A message that fits two categories: the model picks the main issue and explains why in `reason`.
- `reason` is one sentence.
- Models: `minimax/minimax-m3` (the class model) and `xiaomi/mimo-v2.6-flash`, switched by hand through `CHAT_MODEL`. Cheap models only.

## Not in scope
- Classifying more than one message per run, or reading messages from a file
- Categories beyond the four above
- Replying to the customer or routing the message anywhere
- Multi-turn conversation, automatic retries, or fallback between models
- Saving results, a GUI, or a web interface

## Success looks like
- A clear billing message, a clear technical message, and a clear sales message each get the right category.
- A message that is not a support request (for example, "What's your favorite movie?") gets `unknown`.
- A message that fits two categories passes if the model returns either of them.
- Urgency matches the rule above on all five eval cases.
- A model reply that is not JSON, is empty, or has a value outside the allowed set makes the program print a clear error, and the eval counts that case as a FAIL instead of crashing.
- The eval prints PASS or FAIL for each of the five cases and a summary line with the input and output tokens used.

## Open questions
- Where the token counts print so the JSON output stays clean is left to the spec.

**Approved by:** Lane Faison, 2026-10-01
