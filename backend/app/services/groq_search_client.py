"""Small Groq Compound wrapper for JSON responses grounded by web search."""
import json
import re
import time
from typing import Any, Dict, Optional, Set

from app.config import settings


def _extract_json(text: str) -> Dict[str, Any]:
    """Parse a JSON object even when the model wraps it in a Markdown fence."""
    fenced = re.search(r"```(?:json)?\s*(\{.*\})\s*```", text, flags=re.DOTALL | re.IGNORECASE)
    candidate = fenced.group(1) if fenced else text

    try:
        data = json.loads(candidate)
    except json.JSONDecodeError:
        start = candidate.find("{")
        end = candidate.rfind("}")
        if start == -1 or end == -1:
            raise ValueError("Groq response did not contain a JSON object")
        data = json.loads(candidate[start:end + 1])

    if not isinstance(data, dict):
        raise ValueError("Groq response must be a JSON object")
    return data


def call_json_with_search(system: str, user: str, max_tokens: Optional[int] = None) -> Dict[str, Any]:
    """Call Groq Compound with server-side web search and return parsed JSON."""
    if not settings.GROQ_API_KEY_3:
        raise RuntimeError("GROQ_API_KEY_3 is not configured")

    try:
        from groq import Groq
    except ImportError as exc:
        raise RuntimeError("The groq package is not installed") from exc

    client = Groq(
        api_key=settings.GROQ_API_KEY_3,
        max_retries=0,
        default_headers={"Groq-Model-Version": settings.COMPETITOR_GROQ_VERSION},
    )
    response = _create_completion_with_retry(client, system, user, max_tokens)

    message = response.choices[0].message
    text = message.content or ""
    if not text:
        raise ValueError("Groq returned no final text response")
    return _keep_grounded_services(_extract_json(text), _search_result_urls(message))


def _create_completion_with_retry(client: Any, system: str, user: str, max_tokens: Optional[int]) -> Any:
    """Retry one transient rate limit using Groq's retry-after header."""
    try:
        return _create_completion(client, system, user, max_tokens)
    except Exception as exc:
        if getattr(exc, "status_code", None) != 429:
            raise
        retry_after = _retry_after_seconds(exc)
        if retry_after > settings.COMPETITOR_GROQ_MAX_RETRY_SECONDS:
            raise
        time.sleep(retry_after)
        return _create_completion(client, system, user, max_tokens)


def _create_completion(client: Any, system: str, user: str, max_tokens: Optional[int]) -> Any:
    request = {
        "model": settings.COMPETITOR_GROQ_MODEL,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
    }
    if max_tokens is not None:
        request["max_completion_tokens"] = max_tokens
    return client.chat.completions.create(
        **request,
    )


def _retry_after_seconds(exc: Exception) -> float:
    response = getattr(exc, "response", None)
    headers = getattr(response, "headers", {})
    try:
        return max(1.0, float(headers.get("retry-after", 1)))
    except (TypeError, ValueError):
        return 1.0


def _search_result_urls(message: Any) -> Set[str]:
    """Collect URLs returned by Groq's actual server-side web search tool."""
    urls: Set[str] = set()
    for tool in getattr(message, "executed_tools", None) or []:
        search_results = getattr(tool, "search_results", None)
        if search_results is None and isinstance(tool, dict):
            search_results = tool.get("search_results")
        results = getattr(search_results, "results", None)
        if results is None and isinstance(search_results, dict):
            results = search_results.get("results", [])
        for result in results or []:
            url = getattr(result, "url", None)
            if url is None and isinstance(result, dict):
                url = result.get("url")
            if url:
                urls.add(url.rstrip("/"))
    return urls


def _keep_grounded_services(data: Dict[str, Any], search_urls: Set[str]) -> Dict[str, Any]:
    """Drop generated source cards unless their URL came from web search."""
    if not search_urls:
        data["known_services"] = []
        return data

    grounded_services = []
    for service in data.get("known_services", []):
        source_hint = service.get("source_hint", "")
        match = re.search(r"https?://[^\s)]+", source_hint)
        if match and match.group(0).rstrip("/") in search_urls:
            grounded_services.append(service)
    data["known_services"] = grounded_services
    return data
