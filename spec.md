# Spec

<!-- The agent writes this from the approved intent. You validate it against the intent.
     If the spec and the intent disagree, the intent wins until you change the intent. -->

## Intent
[`intent/classifier.md`](intent/classifier.md)

## Components
One component: the classifier, plus the eval runner that checks it.

### classifier
- **What it does:** Takes one support message from the command line, sends it to a chat model through OpenRouter with a fixed system message that defines the categories and the urgency rule, pulls the JSON object out of the reply, checks it, and prints it.
- **Language:** Python 3.9+, standard library only. **Why:** Java was the alternative. It has no JSON parser in its standard library, so it would need a hand-written parser or an extra jar; Python's `json` module needs nothing. Last week's `chat.py` is already Python and its request code carries over.
- **Model:** `minimax/minimax-m3` (default, the class model) compared against `xiaomi/mimo-v2.6-flash`. **Why:** both are cheap models, so the comparison is about whether a model follows a strict output format, not raw capability. MiniMax is $0.23 in / $0.96 out per million tokens and spends output tokens on hidden reasoning (Week 2: 142 output tokens for one sentence). MiMo is $0.07 in / $0.28 out. The eval will show whether the cheaper model sorts as well.
- **Interfaces:**
  - Run: `python3 classifier.py "the message"`
  - Environment: `CHAT_BASE_URL`, `CHAT_MODEL`, `OPENROUTER_API_KEY`
  - Request: one system message, one user message, `temperature` 0, `max_tokens` 1000 (room for hidden reasoning)
  - Urgency values: `low`, `medium`, `high` for support requests (rule from the intent); `irrelevant` only when the category is `unknown`.
  - Output on success: the JSON object alone on standard output, e.g. `{"category": "billing", "urgency": "high", "reason": "The customer was charged twice."}`, then a usage line on standard error: `model: <model> | input tokens: <n> | output tokens: <n>`. Keeping the usage line separate means standard output is always clean JSON.
  - Exit code: 0 on success, 1 on any model or reply failure, 2 on missing input or configuration.
- **Dependencies:** `urllib.request`, `json`, `os`, `sys`. No packages.

### eval
- **What it does:** Reads the five cases from `cases.json`, runs `classifier.py` once per case as a separate process, compares the result with the expected answer, and prints PASS or FAIL per case and one summary line.
- **Interfaces:**
  - Run: `python3 eval.py` (same environment variables)
  - `cases.json`: a list of cases, each with `id`, `message`, `categories` (list of accepted categories: one entry, or two for the ambiguous case), and `urgency`.
  - Output: one line per case, `PASS <id>` or `FAIL <id>: <what was expected> / <what came back>`, then `Summary: <passed>/5 passed | model: <model> | input tokens: <total> | output tokens: <total>`.
- **Dependencies:** `json`, `subprocess`, `sys`, `re`.

## Behavior
The five eval cases. Cases 1 to 4 check both `category` and `urgency`; case 5 checks `category` only.

1. A clear billing message (charged twice) returns `billing`, urgency `high` (money was lost).
2. A clear technical message (a feature broken, with a workaround) returns `technical`, urgency `medium`.
3. A clear sales message (a question about plans or pricing) returns `sales`, urgency `low`.
4. A message that fits both billing and technical (the app crashed during checkout and the customer may have been charged) returns `billing` or `technical`, urgency `high`.
5. A message that is not a support request at all returns `unknown`. Urgency is not checked; the system message asks for `irrelevant`.

## Failure handling
- **Reply wrapped in formatting:** leading and trailing whitespace and Markdown code fences (a line of three backticks, with or without `json` after them) are removed before parsing. Any other words before or after the JSON object make the reply a failure (next bullet).
- **Reply is not JSON:** prints `error: reply is not JSON` and the first 200 characters of the reply to standard error; exit 1.
- **Field missing, or a value outside the allowed set** (category not one of the four, urgency not low/medium/high, urgency `irrelevant` on a category other than `unknown`, reason empty): prints `error: invalid <field>: <value>`; exit 1. Values are lowercased and trimmed before checking, so `"Billing "` is accepted as `billing`.
- **Empty reply:** prints `error: empty reply (finish_reason: <reason>)`; exit 1. A `length` finish reason means hidden reasoning used up `max_tokens`.
- **Missing key, URL, model, or message:** prints which one is missing; exit 2.
- **HTTP error or no response within 60 seconds:** prints the status code or `timeout`; exit 1.
- **In the eval:** any non-zero exit counts as a FAIL for that case, with the error shown on its line. The eval never stops early and always prints the summary.

## Cost estimate
Per classification: about 400 input tokens (system message plus message) and about 300 output tokens on MiniMax, including hidden reasoning, based on Week 2's 201 in / 142 out for a shorter prompt.
- MiniMax: about $0.0004 per call, $0.002 per five-case eval run.
- MiMo: about $0.0001 per call, $0.0006 per eval run.
- A semester of use at 40 eval runs per model: about $0.10 total. Week 2's logged cost ($0.000196 for 201 in / 142 out) matches these prices.

## Out of scope
From the intent: more than one message per run, reading messages from a file, categories beyond the four, replying to or routing the customer, multi-turn conversation, retries or fallback between models, saving results, a GUI or web interface.
From the design: OpenRouter's `response_format` JSON-schema option, because not every model honors it; the eval must not depend on it.
