"""Shared model client + helpers used by every agent.

NOTE: This project originally targeted the Claude API. Because only a Gemini
free-tier key was available, the *internals* of this file now call Google
Gemini — but the public functions (`call_json`, `call_json_with_search`) keep
the SAME names and signatures, so no other file in the project changed.

Get a free key (no credit card): https://aistudio.google.com/apikey
Free model used: gemini-2.5-flash  (1,500 requests/day, web search grounding).
"""
import os
import json
import re
import time
from pathlib import Path
from google import genai
from google.genai import types
from dotenv import load_dotenv

# Load .env from the backend/ folder explicitly, no matter where uvicorn is run.
_ENV_PATH = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=_ENV_PATH)

MODEL = os.getenv("MODEL", "gemini-2.5-flash")
# Free fallback model used if the primary stays overloaded (also free tier).
FALLBACK_MODEL = os.getenv("FALLBACK_MODEL", "gemini-2.5-flash-lite")
_API_KEY = os.getenv("GEMINI_API_KEY")

if not _API_KEY or _API_KEY.strip() in ("", "your-gemini-key-here"):
    raise RuntimeError(
        "GEMINI_API_KEY is not set.\n"
        f"  Expected a .env file at: {_ENV_PATH}\n"
        "  It must contain a line like:  GEMINI_API_KEY=AIza...\n"
        "  Get a free key at https://aistudio.google.com/apikey\n"
        "  (Check the file isn't named '.env.txt' and has no quotes around the key.)"
    )

client = genai.Client(api_key=_API_KEY)

# ONLY genuine transient server problems are worth retrying. A retry on a 4xx
# client error (bad/oversized request, exhausted quota, invalid key) will NEVER
# succeed — retrying it just burns time and quota and hangs the UI.
_TRANSIENT_SUBSTRINGS = ("503", "unavailable", "overloaded", "high demand",
                         "deadline", "timeout", "500 ", "internal error")


def _status_code(err: Exception) -> int | None:
    """Best-effort extraction of an HTTP status code from a google-genai error."""
    code = getattr(err, "code", None) or getattr(err, "status_code", None)
    if isinstance(code, int):
        return code
    # google-genai often embeds the code in the message, e.g. "429 RESOURCE_EXHAUSTED"
    m = re.search(r"\b(4\d\d|5\d\d)\b", str(err))
    return int(m.group(1)) if m else None


def _classify(err: Exception) -> str:
    """Return one of: 'transient' | 'quota' | 'client' | 'unknown'."""
    code = _status_code(err)
    msg = str(err).lower()

    if code in (500, 502, 503, 504) or any(s in msg for s in _TRANSIENT_SUBSTRINGS):
        return "transient"
    if code == 429 or "resource_exhausted" in msg or "quota" in msg:
        return "quota"
    if code is not None and 400 <= code < 500:
        return "client"
    return "unknown"


def _generate_with_retry(*, model_config, contents, max_retries: int = 4):
    """Call Gemini, retrying ONLY genuine transient errors with backoff.
    Falls back to FALLBACK_MODEL if the primary stays transiently unavailable.
    Fails fast (no pointless retries) on client errors and quota exhaustion.
    """
    delay = 1.5
    last_err: Exception | None = None
    models_to_try = [MODEL, FALLBACK_MODEL]

    for model_name in models_to_try:
        model, config = model_config(model_name)
        for attempt in range(max_retries):
            try:
                return client.models.generate_content(
                    model=model, contents=contents, config=config
                )
            except Exception as e:  # noqa: BLE001 - we inspect/classify it
                last_err = e
                kind = _classify(e)

                if kind == "client":
                    # 4xx — request itself is wrong (too large, bad arg). No retry.
                    raise RuntimeError(
                        f"Request rejected by the model ({_status_code(e)}). "
                        f"This usually means the input was malformed or too large. "
                        f"Details: {e}"
                    ) from e

                if kind == "quota":
                    # Free-tier quota hit — retrying in seconds won't help.
                    raise RuntimeError(
                        "Gemini free-tier quota/rate limit reached (429). "
                        "Wait a minute and try again, or reduce request frequency. "
                        f"Details: {e}"
                    ) from e

                # transient or unknown -> retry with backoff
                wait = delay * (2 ** attempt)
                print(f"[retry] {model_name} attempt {attempt+1}/{max_retries} "
                      f"failed ({kind}: {type(e).__name__}); waiting {wait:.1f}s")
                time.sleep(wait)
        print(f"[retry] {model_name} exhausted; trying next model")

    raise last_err if last_err else RuntimeError("generation failed")


def _strip_fences(text: str) -> str:
    """Remove ```json ... ``` fences if the model added them."""
    text = text.strip()
    text = re.sub(r"^```(?:json)?", "", text)
    text = re.sub(r"```$", "", text.strip())
    return text.strip()


def _parse_json(text: str) -> dict:
    cleaned = _strip_fences(text)
    if not cleaned:
        raise RuntimeError("Model returned an empty response.")
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", cleaned, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(0))
            except json.JSONDecodeError:
                pass
        # Likely the output was cut off at max_output_tokens (unbalanced braces).
        if cleaned.count("{") > cleaned.count("}"):
            raise RuntimeError(
                "Model response was truncated before completing the JSON "
                "(hit the output token limit). Try a more focused document."
            )
        raise RuntimeError(f"Could not parse model JSON output. Got: {cleaned[:200]}")


def call_json(system: str, user: str, max_tokens: int = 4000) -> dict:
    """Call the model and parse a JSON object out of the response.

    Uses Gemini's native JSON mode (response_mime_type) so output is reliably
    parseable. Retries transient 503/429 errors and falls back if needed.
    """
    def cfg(model_name):
        return model_name, types.GenerateContentConfig(
            system_instruction=system,
            max_output_tokens=max_tokens,
            temperature=0.4,
            response_mime_type="application/json",
        )

    resp = _generate_with_retry(model_config=cfg, contents=user)
    return _parse_json(resp.text)


def call_json_with_search(system: str, user: str, max_tokens: int = 4000) -> dict:
    """Like call_json but gives the model the Google Search grounding tool, so
    competitor intelligence is real, not hallucinated.

    Grounding and JSON mode can't be combined in one call, so we do two turns:
      1. a grounded research turn (real web results)
      2. a JSON-formatting turn that structures those findings.
    Both turns retry transient errors.
    """
    def cfg(model_name):
        return model_name, types.GenerateContentConfig(
            system_instruction=system,
            max_output_tokens=max_tokens,
            temperature=0.4,
            tools=[types.Tool(google_search=types.GoogleSearch())],
        )

    research = _generate_with_retry(model_config=cfg, contents=user)
    findings = research.text or ""
    return call_json(
        system="You convert research notes into strict JSON. Output ONLY the JSON object, no prose, no code fences.",
        user=f"Research notes:\n\n{findings}\n\nReturn the JSON object exactly matching the schema described in the notes.",
        max_tokens=max_tokens,
    )
