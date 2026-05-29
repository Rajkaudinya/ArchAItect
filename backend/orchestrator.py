"""Orchestrator — runs the agent pipeline and yields progress events.

Yields dicts shaped as {"step": str, "status": "running"|"done", "data": ...}
so the API layer can stream them to the UI as Server-Sent Events.
"""
from agents import domain_agent, decompose_agent, dependency_agent, competitor_agent
from preprocess import condense

STEPS = [
    ("domain", "Extracting domain model"),
    ("decompose", "Identifying microservice boundaries"),
    ("dependencies", "Mapping service dependencies"),
    ("competitor", "Researching how competitors are built"),
    ("synthesis", "Assembling the architecture"),
]


def run_pipeline(doc: str):
    """Generator. Yields progress + the final 'result' event."""
    result = {}

    # 0. Token-free pre-processing: condense ANY document down to a bounded,
    # high-signal digest in pure Python BEFORE the LLM sees it. This is what
    # makes long real-world docs work without burning tokens or breaking.
    condensed = condense(doc, char_budget=6000)
    digest = condensed["digest"]
    yield {
        "step": "preprocess",
        "status": "done",
        "data": {
            "original_chars": condensed["original_chars"],
            "digest_chars": condensed["digest_chars"],
            "compressed": condensed["compressed"],
        },
    }

    # 1. Domain (works on the digest, not the raw document)
    yield {"step": "domain", "label": "Extracting domain model", "status": "running"}
    domain = domain_agent.run(digest)
    result["domain"] = domain
    yield {"step": "domain", "status": "done", "data": domain}

    # 2. Decompose
    yield {"step": "decompose", "label": "Identifying microservice boundaries", "status": "running"}
    decomp = decompose_agent.run(domain)
    result["services"] = decomp.get("services", [])
    yield {"step": "decompose", "status": "done", "data": decomp}

    # 3. Dependencies
    yield {"step": "dependencies", "label": "Mapping service dependencies", "status": "running"}
    deps = dependency_agent.run(decomp)
    result["edges"] = deps.get("edges", [])
    result["shared_concerns"] = deps.get("shared_concerns", [])
    yield {"step": "dependencies", "status": "done", "data": deps}

    # 4. Competitor intel (web search)
    yield {"step": "competitor", "label": "Researching how competitors are built", "status": "running"}
    names = [s.get("name", "") for s in result["services"]]
    comp = competitor_agent.run(domain.get("app_type", "software system"), names)
    result["competitor"] = comp
    yield {"step": "competitor", "status": "done", "data": comp}

    # 5. Synthesis (assemble final payload)
    yield {"step": "synthesis", "label": "Assembling the architecture", "status": "running"}
    final = {
        "app_type": domain.get("app_type"),
        "summary": domain.get("summary"),
        "actors": domain.get("actors", []),
        "functional_areas": domain.get("functional_areas", []),
        "services": result["services"],
        "edges": result["edges"],
        "shared_concerns": result["shared_concerns"],
        "competitor": result["competitor"],
        "preprocess": {
            "original_chars": condensed["original_chars"],
            "digest_chars": condensed["digest_chars"],
            "compressed": condensed["compressed"],
        },
    }
    yield {"step": "synthesis", "status": "done", "data": final}
    yield {"step": "result", "status": "complete", "data": final}
