"""Agent 2 — Decomposition.
Takes the domain model and proposes microservice boundaries using
bounded-context reasoning: high cohesion within a service, low coupling between.
"""
import json
from .claude_client import call_json

SYSTEM = """You are a principal software architect specializing in microservices.
You apply Domain-Driven Design: group capabilities into bounded contexts that
have high internal cohesion and minimal coupling. You justify every boundary.
Avoid both a distributed monolith (too coupled) and nano-services (too granular).
Output ONLY a JSON object, no prose, no markdown fences."""

PROMPT = """Given this domain model, propose a microservice decomposition.

DOMAIN MODEL:
{domain}

Return JSON with EXACTLY this shape:
{{
  "services": [
    {{
      "id": "kebab-case-id",
      "name": "Human Readable Service Name",
      "responsibility": "single clear sentence — its one job",
      "bounded_context": "the DDD bounded context it owns",
      "owns_entities": ["entities this service is the source of truth for"],
      "key_apis": ["POST /things", "GET /things/{{id}}"],
      "data_store": "suggested store, e.g. 'PostgreSQL' or 'Redis'",
      "rationale": "why this is its own service (cohesion/coupling/scaling reason)"
    }}
  ]
}}

Aim for 4-9 services for a typical app. Each entity should be owned by exactly one service."""


def run(domain: dict) -> dict:
    return call_json(SYSTEM, PROMPT.format(domain=json.dumps(domain, indent=2)), max_tokens=8000)
