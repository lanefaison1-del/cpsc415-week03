# Checks: classifier eval, two models

Each run is `python3 eval.py` with `CHAT_BASE_URL=https://openrouter.ai/api/v1`, changing only `CHAT_MODEL`. Same five cases from `cases.json` both times. All runs on Oct 1, 2026.

## Comparison

| Model | Cases passed | Failed case and how | Tokens in | Tokens out |
|---|---|---|---|---|
| `minimax/minimax-m3` (2:42 PM) | 5/5 | None | 1,653 | 457 |
| `xiaomi/mimo-v2.6-flash` (2:44 PM) | 4/5 | `not_support`: the reply was cut off mid-word (`{"category": "unknown", "urgency": "relev`), so it was not valid JSON and counted as a FAIL | 860 | 366 |
| Local model | Not run | No local model installed | | |

Cost at OpenRouter's listed prices: about $0.0008 for the MiniMax run and $0.0002 for the MiMo run.

## The MiMo failure: case or model?

**Model error.** The expected answer (`unknown`) is not a judgment call: a request for a pizza recommendation is not billing, technical, or sales. MiMo's broken reply had started the right answer. Sent the same message three more times outside the eval, MiMo returned `unknown` / `irrelevant` with a sensible reason each time, once wrapped in code fences, which the spec allows. The classification was right; the reply it delivered once was unusable. The program did not record why that reply ended, so the cause of the cut-off (model or the server that ran it) is not confirmed.

## Notes

- Both models handled the deceptive case: "recommend" did not pull either of them into `sales` when the reply arrived complete.
- Both gave `high` urgency on the crash-plus-charge case and accepted the urgency rule as written in the system message.
- MiMo counted about half as many input tokens as MiniMax for the same requests; each provider tokenizes differently.
- MiniMax used about 90 output tokens per answer, well under the spec's estimate of 300, so a run cost less than half of what the spec estimated.
- Temperature 0 did not make MiMo's output identical between runs: the reason text and the use of code fences varied.
