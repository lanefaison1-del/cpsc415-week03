#!/usr/bin/env python3
"""Classify one customer-support message.

Usage: python3 classifier.py "the message"

Reads CHAT_BASE_URL, CHAT_MODEL and OPENROUTER_API_KEY from the environment.
Prints a JSON object with category, urgency and reason on standard output,
and a usage line on standard error. See spec.md.
"""
import json
import os
import socket
import sys
import urllib.error
import urllib.request

CATEGORIES = {"billing", "technical", "sales", "unknown"}
URGENCIES = {"low", "medium", "high"}
MAX_TOKENS = 1000
TIMEOUT_SECONDS = 60

SYSTEM_MESSAGE = (
    "Classify one customer-support message. Reply with only a JSON object, "
    "no other text, with exactly these keys: category, urgency, reason.\n"
    "category: billing (charges, refunds, invoices, payments); technical "
    "(something in the product is broken or not working); sales (questions "
    "about plans, pricing, buying, or upgrading); unknown (not a "
    "customer-support request at all). If a message fits two categories, "
    "choose the main issue and say why in reason.\n"
    "urgency: high if money was lost or the service is down; medium if a "
    "feature is broken but there is a workaround; low if it is a question or "
    "a request; irrelevant if the category is unknown.\n"
    "reason: one sentence."
)


def fail(message, code=1):
    print("error: " + message, file=sys.stderr)
    sys.exit(code)


def read_settings():
    settings = {}
    for name in ("CHAT_BASE_URL", "CHAT_MODEL", "OPENROUTER_API_KEY"):
        value = os.environ.get(name, "").strip()
        if not value:
            fail("missing environment variable " + name, 2)
        settings[name] = value
    message = " ".join(sys.argv[1:]).strip()
    if not message:
        fail('missing message. Usage: python3 classifier.py "the message"', 2)
    return settings, message


def call_model(settings, message):
    url = settings["CHAT_BASE_URL"].rstrip("/") + "/chat/completions"
    body = {
        "model": settings["CHAT_MODEL"],
        "messages": [
            {"role": "system", "content": SYSTEM_MESSAGE},
            {"role": "user", "content": message},
        ],
        "temperature": 0,
        "max_tokens": MAX_TOKENS,
    }
    request = urllib.request.Request(
        url,
        data=json.dumps(body).encode("utf-8"),
        headers={
            "Authorization": "Bearer " + settings["OPENROUTER_API_KEY"],
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=TIMEOUT_SECONDS) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as error:
        detail = error.read().decode("utf-8", "replace")[:200]
        fail("HTTP {} from the API: {}".format(error.code, detail))
    except socket.timeout:
        fail("timeout after {} seconds".format(TIMEOUT_SECONDS))
    except urllib.error.URLError as error:
        if isinstance(error.reason, socket.timeout):
            fail("timeout after {} seconds".format(TIMEOUT_SECONDS))
        fail("cannot reach the API: {}".format(error.reason))


def strip_formatting(text):
    """Remove surrounding whitespace and a Markdown code fence, nothing else."""
    text = text.strip()
    lines = text.split("\n")
    if (
        len(lines) >= 2
        and lines[0].strip().lower() in ("```", "```json")
        and lines[-1].strip() == "```"
    ):
        text = "\n".join(lines[1:-1]).strip()
    return text


def parse_reply(text):
    """Turn the model's reply into a dict, or fail if it is not pure JSON."""
    cleaned = strip_formatting(text)
    try:
        result = json.loads(cleaned)
    except ValueError:
        result = None
    if not isinstance(result, dict):
        fail("reply is not JSON: " + text[:200].replace("\n", " "))
    return result


def check_fields(result):
    """Check each field against the allowed values; return the cleaned object."""
    for field in ("category", "urgency", "reason"):
        if field not in result:
            fail("invalid {}: missing".format(field))
    category = str(result["category"]).strip().lower()
    urgency = str(result["urgency"]).strip().lower()
    reason = str(result["reason"]).strip()
    if category not in CATEGORIES:
        fail("invalid category: {}".format(result["category"]))
    allowed = URGENCIES | {"irrelevant"} if category == "unknown" else URGENCIES
    if urgency not in allowed:
        fail("invalid urgency: {}".format(result["urgency"]))
    if not reason:
        fail("invalid reason: empty")
    return {"category": category, "urgency": urgency, "reason": reason}


def main():
    settings, message = read_settings()
    data = call_model(settings, message)

    usage = data.get("usage") or {}
    print(
        "model: {} | input tokens: {} | output tokens: {}".format(
            data.get("model", settings["CHAT_MODEL"]),
            usage.get("prompt_tokens", 0),
            usage.get("completion_tokens", 0),
        ),
        file=sys.stderr,
    )

    choice = (data.get("choices") or [{}])[0]
    content = (choice.get("message") or {}).get("content") or ""
    if not content.strip():
        fail("empty reply (finish_reason: {})".format(choice.get("finish_reason")))

    result = check_fields(parse_reply(content))
    print(json.dumps(result))


if __name__ == "__main__":
    main()
