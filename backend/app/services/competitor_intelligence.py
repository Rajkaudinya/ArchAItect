"""Web-grounded competitor architecture research powered by Groq Compound."""
from typing import List

from app.services.groq_search_client import call_json_with_search


SYSTEM = """You are a software architecture researcher. You search the web for
public information (engineering blogs, conference talks, and technical docs)
about how well-known companies build their backend systems. You ONLY report
architecture details that you found in search results. If you cannot confirm
something, say it is a general industry pattern rather than claiming a specific
company does it."""

PROMPT = """The user is building this kind of system: {app_type}

1. Identify ONE well-known company that operates a system in this same domain
   (for example: e-commerce -> Amazon; streaming -> Netflix; ride-hail -> Uber).
2. Search the web for how that company structures its microservices/backend.
3. Compare it to these proposed services: {service_names}

Return ONLY a JSON object with EXACTLY this shape:
{{
  "competitor": "Company name",
  "why_relevant": "one sentence on why they are a good comparison",
  "known_services": [
    {{
      "name": "their service/system name",
      "purpose": "what it does",
      "source_hint": "public source title and clickable URL"
    }}
  ],
  "insights": ["2-4 actionable takeaways comparing their approach to the user's proposed services"]
}}

Base everything on what you actually find in search. Keep known_services to 4-7
items when public sources support that many. Include an EXACT public URL from
your web-search results in every source_hint. Do not invent service names or
URLs. Return fewer known_services rather than filling gaps with assumptions.
Keep each purpose, source_hint, and insight under 35 words."""


def run(app_type: str, service_names: List[str]) -> dict:
    user = PROMPT.format(app_type=app_type, service_names=", ".join(service_names))
    try:
        return call_json_with_search(SYSTEM, user)
    except Exception as exc:
        # Competitor research is optional; it must never break core analysis.
        return {
            "competitor": "Unavailable",
            "why_relevant": _failure_message(exc),
            "known_services": [],
            "insights": [],
        }


def _failure_message(exc: Exception) -> str:
    """Expose actionable setup errors without leaking upstream response details."""
    message = str(exc)
    if "GROQ_API_KEY_3 is not configured" in message:
        return "Competitor research is not configured. Add GROQ_API_KEY_3 to the root .env file and restart the backend."
    if "groq package is not installed" in message:
        return "Competitor research is not installed. Run pip install -r requirements.txt in the backend environment and restart the backend."
    if getattr(exc, "status_code", None) == 429:
        return "Groq rate limit reached for competitor research. Wait briefly and click Research Again. If this persists, review the GROQ_API_KEY_3 project limits."
    if getattr(exc, "status_code", None) == 413:
        return "Groq rejected the competitor research payload. Restart the backend to use the lightweight Compound Mini search configuration, then try again."
    return f"Competitor research could not complete ({type(exc).__name__}). Check the backend logs for details."
