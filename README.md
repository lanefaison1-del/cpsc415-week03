# Support-message classifier with a five-case eval

CPSC 415, Week 3. A command-line program that takes one customer-support message, asks a model to classify it, and prints JSON with `category` (billing, technical, sales, or unknown), `urgency` (low, medium, high, or irrelevant for non-support messages), and a one-sentence `reason`. An eval runs five messages with known answers and compares two models.

The intent is in [`intent/classifier.md`](intent/classifier.md) and the design in [`spec.md`](spec.md).

## How to run

Python 3.9 or later, standard library only. Set three environment variables:

```bash
export CHAT_BASE_URL=https://openrouter.ai/api/v1
export CHAT_MODEL=minimax/minimax-m3          # or xiaomi/mimo-v2.6-flash
export OPENROUTER_API_KEY=<your key>
```

Classify one message:

```bash
python3 classifier.py "I was charged twice this month."
```

Output is the JSON object on standard output and a usage line (model, input tokens, output tokens) on standard error. Exit code 0 on success, 1 when the model's reply is unusable, 2 when a setting or the message is missing.

Run the eval:

```bash
python3 eval.py
```

It prints PASS or FAIL for each case in `cases.json` and a summary line with the score and total tokens.

## The five cases

| # | Message | Expected | What it is there to catch |
|---|---|---|---|
| 1 | "I was charged twice for my subscription this month. Please refund the extra charge." | billing, high | A clear billing case where money was lost |
| 2 | "The Export to PDF button does nothing when I click it. I can still print the page to PDF from my browser, but please fix the button." | technical, medium | Whether the model applies the rule that a workaround makes it medium |
| 3 | "We're thinking about upgrading our team from the Basic plan to Pro. What extra features would we get?" | sales, low | A clear sales question; "plan" should not pull it into billing |
| 4 | "Your app crashed while I was checking out, and now there's a charge on my card but no order confirmation." | billing or technical, high | The ambiguous case: either category passes; urgency is high because money left the customer's card |
| 5 | "Can you recommend a good pizza place near campus?" | unknown (urgency not checked) | A deceptive non-support message: it is phrased as a request, and "recommend" could pull a model toward sales |

## Two-model comparison

From [`CHECKS.md`](CHECKS.md), all runs on Oct 1, 2026:

| Model | Cases passed | Failed case and how | Tokens in | Tokens out |
|---|---|---|---|---|
| `minimax/minimax-m3` | 5/5 | None | 1,653 | 457 |
| `xiaomi/mimo-v2.6-flash` | 4/5 | `not_support`: the reply was cut off mid-word (`{"category": "unknown", "urgency": "relev`), so it was not valid JSON and counted as a FAIL | 860 | 366 |
| Local model | Not run | No local model installed | | |

MiniMax passed all five cases; MiMo passed four, failing the deceptive case because its reply was cut off mid-word, although three re-sends of that message all came back `unknown` / `irrelevant`. MiMo counted about half as many input tokens and its run cost about a quarter as much ($0.0002 against $0.0008 at listed prices).

## One correction I made to the spec

The draft spec pulled the JSON out of any surrounding text. Kousen's setup notes say text around the answer should count as a failed case, so I tightened it: formatting marks like code fences are allowed, but any extra words make the case fail. That rule is what caught MiMo's cut-off reply on the pizza case.

## One line of code I can explain

In `classifier.py`, inside `parse_reply`:

```python
result = json.loads(cleaned)
```

Just before this line, the program removes any code-fence marks from the AI's reply. This line then tries to turn what's left into structured data. If anything else is in the text, like an extra sentence or a cut-off word, it fails, and the program reports "reply is not JSON." This is where my "formatting okay, no extra language" rule actually lives.

## Files

- `classifier.py`: the classifier
- `eval.py`: the eval runner
- `cases.json`: the five cases
- `CHECKS.md`: run results and the case-or-model call on each failure
- `DECISIONS.md`: my decisions at each review point
- `intent/classifier.md`, `spec.md`: the approved intent and spec
