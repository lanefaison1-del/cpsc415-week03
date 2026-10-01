# Decisions log

My decisions at each review point, recorded as I gave them. Source material for the README and the final write-up.

## 1. Intent review (Oct 1, 2026)

**Options I was given:**
- A. What makes high vs. low urgency? A1: high = money lost or service down; medium = feature broken with a workaround; low = a question or request. A2: leave it to the AI.
- B. A message fitting two categories. B1: the AI picks the main issue and explains why; the test accepts either category. B2: the test requires one specific category.
- C. Check urgency on every message? C1: only where clear-cut. C2: all five.
- D. Garbled AI answer. D1: the program prints a clear error and the test counts it as a FAIL.

**My response, verbatim:**
> This is the fix: High means money was lost or the service is down. Medium means a feature is broken but there's a workaround. Low means a question or request., and then The AI picks the main issue and explains why. The test accepts either category., and then Check it on all five. The program prints a clear error and the test counts it as a failure

**Result:** A1, B1, C2, D1. The urgency definition was my correction to the intent; the draft named the three levels but never defined them. Committed as "Approve intent for the classifier".

## 2. Spec review (Oct 1, 2026)

**Options I was given:**
- 1. The AI wraps its answer in extra text. 1A: strict, any extra text fails. 1B: allow formatting marks (code fences), fail anything else. 1C: dig the JSON out of whatever surrounds it (the draft). Kousen's setup notes say text around the answer should count as a failed case.
- 2. The AI answers "Billing" instead of "billing". 2A: accept it. 2B: count it as a FAIL.
- 3. Urgency for the off-topic message. 3A: low. 3B: don't check it on that case.

**My response, verbatim:**
> extra formatting okay but no actual extra language, capitalization slip is fine, if it isn't a suppport request the urgency shouldnt be checked and there should be responded as Irellevant

**Result:** 1B, 2A, and a new rule for 3: a non-support message gets urgency `irrelevant`, and the eval does not check urgency on that case.

**Spec correction:** the draft dug the JSON out of any surrounding text. Kousen's setup notes say text around the answer should count as a failed case, so I tightened it: formatting marks are allowed, extra words fail.

**Intent amended:** the `irrelevant` rule changed what the program should do, and the intent wins when it disagrees with the spec. So the intent was updated first ("Update intent: non-support messages get urgency irrelevant, not checked"). This also narrows my earlier "check it on all five" to the four support-request cases. Then the spec was committed ("Approve spec").

## 3. Build plan (Oct 1, 2026)

**Plan:** `classifier.py` (sends one message with fixed instructions, strips formatting, rejects extra words, checks every field, prints JSON plus a token line), `cases.json` (five cases), `eval.py` (runs each case, prints PASS/FAIL and a summary with tokens).

**My response, verbatim:**
> approved

## 4. Test cases (Oct 1, 2026)

**Draft cases:** (1) charged twice → billing, high; (2) Export to PDF broken, browser workaround → technical, medium; (3) upgrade Basic to Pro → sales, low; (4) app crashed at checkout, charge but no order → billing or technical, high; (5) "What's your favorite movie?" → unknown.

**Issues raised:** case 5 was too easy, and a deceptive request ("Can you recommend a good pizza place near campus?") would be a stronger trap. Case 4's urgency could fairly be read as medium.

**My response, verbatim:**
> yeah, case 5 needs to be pressure tested with a more deceptive example. case 4 should be high.

**Result:** case 5 is now "Can you recommend a good pizza place near campus?", expected `unknown`, urgency not checked. Case 4 stays `high`, since money left the customer's card.

## 5. First run, MiniMax (Oct 1, 2026)

5/5 passed; 1,653 tokens in, 457 out. Committed as "Classifier and eval, first run".

## 6. Second model, MiMo (Oct 1, 2026)

**Result:** 4/5. `not_support` failed because the reply was cut off mid-word (`{"category": "unknown", "urgency": "relev`) and was not valid JSON. Three diagnostic re-sends of the same message all came back correct (`unknown` / `irrelevant`).

**Options I was given:**
- A. Model error: the expected answer is unambiguous and MiMo agreed with it three times; the failure is unreliable output from the cheaper model.
- B. Judgment call in the test.
- Optional: add the reason the reply ended to the "not JSON" error message, as a separate commit.

**My response, verbatim:**
> A

**Result:** recorded as a model error in `CHECKS.md`. The optional error-message change was not taken.

## 7. README wording (Oct 1, 2026)

**Options I was given:** draft wording for the spec correction, and two lines of code to explain. A: `result = json.loads(cleaned)` in `classifier.py`, where the reply is read (recommended, because it connects the spec correction to the MiMo failure). B: `if result["category"] not in case["categories"]:` in `eval.py`, where a case is judged.

**My response, verbatim:**
> wording fine

**Result:** the drafted wording went into the README as written, with line A, the recommended line.

## Conventions note
The Conventions section of CLAUDE.md uses the defaults from my lab guide (Python, MiniMax as default, snake_case file names), not choices confirmed with a team.
