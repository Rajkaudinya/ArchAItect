"""
Advanced AI-Powered Microservice Architecture Analyzer
Uses NLP, entity recognition, semantic clustering, and dependency analysis
"""
import os
import re
import json
from typing import Dict, Any, List, Tuple, Set
from collections import defaultdict
from app.models.analysis import (
    AnalysisResult, MicroserviceSchema, ApiEndpoint,
    DependencyInfo, MetricScores
)
from app.services.nlp_engine import NLPEngine
from app.services.clarification_engine import ClarificationEngine

try:
    from groq import Groq as _Groq
    _groq_client = _Groq(api_key=os.getenv("GROQ_API_KEY", ""))
except Exception:
    _groq_client = None

# ── The exactly-6 canonical microservices every analysis produces ─────────────
CANONICAL_SERVICES = [
    {
        "id": "user-service",
        "name": "User Service",
        "domain": "User & Authentication",
        "keywords": ["user", "auth", "login", "register", "signup", "password",
                     "profile", "account", "session", "credential", "role", "permission"],
        "database": "PostgreSQL",
        "database_reasoning": "ACID transactions ensure credential integrity; read replicas handle high-volume profile queries.",
        "scaling": [
            "Horizontal scaling with stateless JWT — no sticky sessions needed",
            "Redis cache for token blacklisting and rate-limit counters",
            "Read replicas for user-profile lookups"
        ],
        "default_apis": [
            ("POST", "/api/v1/auth/register",     "Register a new user account"),
            ("POST", "/api/v1/auth/login",         "Authenticate and issue JWT token"),
            ("POST", "/api/v1/auth/refresh",       "Refresh an expired JWT token"),
            ("POST", "/api/v1/auth/logout",        "Invalidate token and end session"),
            ("GET",  "/api/v1/users/{id}/profile", "Fetch authenticated user profile"),
            ("PUT",  "/api/v1/users/{id}/profile", "Update user profile details"),
        ],
    },
    {
        "id": "product-service",
        "name": "Product Service",
        "domain": "Product & Catalog",
        "keywords": ["product", "catalog", "inventory", "stock", "item", "sku",
                     "category", "search", "browse", "listing", "warehouse"],
        "database": "MongoDB",
        "database_reasoning": "Flexible document model accommodates diverse product attributes; Atlas Search enables full-text catalog queries.",
        "scaling": [
            "CDN caching for product images and catalog pages",
            "ElasticSearch index for fast full-text and faceted search",
            "Distributed locking (Redis) for inventory reservation to avoid overselling"
        ],
        "default_apis": [
            ("GET",  "/api/v1/products",           "List products with filters and pagination"),
            ("POST", "/api/v1/products",           "Create a new product listing (admin)"),
            ("GET",  "/api/v1/products/{id}",      "Get detailed product information"),
            ("PUT",  "/api/v1/products/{id}",      "Update product details or pricing"),
            ("GET",  "/api/v1/products/search",    "Full-text search across catalog"),
            ("POST", "/api/v1/inventory/reserve",  "Reserve stock units for an order"),
        ],
    },
    {
        "id": "cart-service",
        "name": "Cart Service",
        "domain": "Cart & Checkout",
        "keywords": ["cart", "basket", "checkout", "add", "remove", "wishlist",
                     "shopping", "coupon", "discount", "promo"],
        "database": "Redis",
        "database_reasoning": "Sub-millisecond in-memory reads; TTL-based auto-expiry handles abandoned carts without a cleanup job.",
        "scaling": [
            "Redis Cluster for distributed, low-latency cart state",
            "Session-affinity routing to reduce cross-node cache misses",
            "Async checkout event published to Order Service via message queue"
        ],
        "default_apis": [
            ("GET",  "/api/v1/cart",               "Get current user's cart contents"),
            ("POST", "/api/v1/cart/items",         "Add a product to the cart"),
            ("PUT",  "/api/v1/cart/items/{id}",    "Update item quantity in cart"),
            ("DELETE", "/api/v1/cart/items/{id}",  "Remove item from cart"),
            ("POST", "/api/v1/cart/checkout",      "Initiate checkout and create order"),
            ("DELETE", "/api/v1/cart",             "Clear entire cart (after order placed)"),
        ],
    },
    {
        "id": "order-service",
        "name": "Order Service",
        "domain": "Order Management",
        "keywords": ["order", "fulfillment", "tracking", "status", "purchase",
                     "place", "shipment", "delivery", "cancel", "confirm"],
        "database": "PostgreSQL",
        "database_reasoning": "ACID guarantees atomic order-state transitions; append-only event log enables full order history.",
        "scaling": [
            "Event sourcing + CQRS separates write (commands) from read (queries)",
            "Saga pattern coordinates multi-step checkout (stock → payment → ship)",
            "Kafka topic per order-lifecycle event for downstream consumers"
        ],
        "default_apis": [
            ("POST", "/api/v1/orders",             "Place a new customer order"),
            ("GET",  "/api/v1/orders",             "List user's orders with filters"),
            ("GET",  "/api/v1/orders/{id}",        "Get order details and current status"),
            ("PUT",  "/api/v1/orders/{id}/cancel", "Cancel order and trigger refund"),
            ("GET",  "/api/v1/orders/{id}/track",  "Real-time order tracking info"),
            ("PUT",  "/api/v1/orders/{id}/status", "Update order status (internal)"),
        ],
    },
    {
        "id": "payment-service",
        "name": "Payment Service",
        "domain": "Payment & Billing",
        "keywords": ["payment", "pay", "billing", "invoice", "refund", "transaction",
                     "stripe", "paypal", "charge", "gateway", "card"],
        "database": "PostgreSQL",
        "database_reasoning": "Financial ledger demands strict ACID; immutable append-only audit trail for regulatory compliance.",
        "scaling": [
            "Idempotency keys on every charge call — safe to retry on network failure",
            "Circuit breaker (Resilience4j) isolates gateway outages from order flow",
            "PCI-DSS tokenisation — raw card data never stored on our servers"
        ],
        "default_apis": [
            ("POST", "/api/v1/payments/charge",         "Process payment for an order"),
            ("POST", "/api/v1/payments/refund",         "Initiate a full or partial refund"),
            ("GET",  "/api/v1/payments/{id}/status",    "Check payment transaction status"),
            ("GET",  "/api/v1/invoices",                "List customer billing invoices"),
            ("GET",  "/api/v1/invoices/{id}",           "Download a specific invoice PDF"),
            ("POST", "/api/v1/payments/webhook",        "Receive payment gateway callbacks"),
        ],
    },
    {
        "id": "notification-service",
        "name": "Notification Service",
        "domain": "Notification & Communication",
        "keywords": ["notification", "email", "sms", "push", "notify", "alert",
                     "message", "send", "template", "reminder", "receipt"],
        "database": "Redis",
        "database_reasoning": "Message queue state in Redis for pub/sub throughput; MongoDB for durable template storage.",
        "scaling": [
            "RabbitMQ/Kafka topic per channel (email, SMS, push) — independent scaling",
            "Dead-letter queue + exponential back-off retry for failed deliveries",
            "Horizontal worker pool scaled by queue depth via KEDA"
        ],
        "default_apis": [
            ("POST", "/api/v1/notifications/send",          "Enqueue a notification for delivery"),
            ("GET",  "/api/v1/notifications/{id}/status",   "Check notification delivery status"),
            ("GET",  "/api/v1/notifications/templates",     "List available message templates"),
            ("POST", "/api/v1/notifications/templates",     "Create or update a template"),
            ("GET",  "/api/v1/notifications/history",       "User's notification history"),
        ],
    },
]

# Canonical dependency rules (always present, refined from document context)
CANONICAL_DEPENDENCIES = [
    ("cart-service",         "product-service",      "sync",  "Validates product existence and stock before adding to cart"),
    ("cart-service",         "user-service",         "sync",  "Associates cart with authenticated user session"),
    ("order-service",        "cart-service",         "sync",  "Reads cart contents to create order line-items"),
    ("order-service",        "product-service",      "sync",  "Reserves inventory units when order is confirmed"),
    ("order-service",        "payment-service",      "sync",  "Triggers payment charge during checkout"),
    ("order-service",        "notification-service", "async", "Publishes order-confirmed event → sends confirmation email/SMS"),
    ("payment-service",      "notification-service", "async", "Publishes payment-result event → sends receipt or failure alert"),
    ("user-service",         "notification-service", "async", "Publishes account events → sends welcome email, password-reset link"),
]

class RequirementAnalyzer:
    def __init__(self):
        self.nlp_engine = NLPEngine()
        
    def analyze_requirements(
        self,
        text: str,
        project_id: str,
        filename: str,
        sections: Dict[str, str] = None,
        clarification_answers: List[Dict] = None,
    ) -> AnalysisResult:
        """
        Analyze requirements and always produce exactly the 6 canonical microservices.
        Groq LLM populates each service with document-specific descriptions and APIs.
        Clarification answers (if provided) are appended as extra context before
        the LLM call so re-analysis reflects user input.
        """
        print(f"Analyzing: {filename}")

        # Append clarification answers as extra context so LLM sees them
        enriched_text = text
        if clarification_answers:
            notes = "\n\n=== CLARIFICATION ANSWERS ===\n"
            for qa in clarification_answers:
                q = qa.get("question", "")
                a = qa.get("answer", "").strip()
                if a:
                    notes += f"Q: {q}\nA: {a}\n\n"
            enriched_text = text + notes
            print(f"   Appended {len(clarification_answers)} clarification answers to context")

        # Step 1: NLP extraction — actors, capabilities, entities, FR-IDs
        print("Step 1: NLP extraction...")
        extraction = self.nlp_engine.extract_entities_and_actions(enriched_text)
        entities   = extraction.get("entities", [])
        actions    = extraction.get("actions", [])
        fr_ids     = self.nlp_engine.extract_fr_ids(enriched_text)
        actors     = self.nlp_engine.extract_actors(enriched_text)
        capabilities = self.nlp_engine.extract_capabilities(enriched_text)
        print(f"   {len(actors)} actors, {len(capabilities)} capabilities, {len(fr_ids)} FR-IDs")

        # Step 2: Build exactly 6 canonical services (LLM-enriched)
        print("Step 2: Building 6 canonical microservices via LLM...")
        services = self._build_six_canonical_services(enriched_text, actors, capabilities, entities)
        print(f"   {len(services)} services built")

        # Step 3: Clarification questions (surface ambiguities for the user)
        print("Step 3: Detecting clarification questions...")
        # Build lightweight domain tuples for the clarification engine
        domain_tuples = [(t["domain"], 80.0, t["keywords"], "") for t in CANONICAL_SERVICES]
        clarifications = ClarificationEngine().detect_ambiguities(
            enriched_text, entities, actors, capabilities, fr_ids, domain_tuples
        )
        print(f"   {len(clarifications)} clarifications")

        # Step 4: Flow diagram
        print("Step 4: Generating user-journey flow diagram...")
        flow_diagram = self._generate_llm_flow_diagram(actors, capabilities, entities, domain_tuples, enriched_text)

        # Step 5: Canonical dependencies (filtered by document presence)
        print("Step 5: Building canonical service dependencies...")
        dependencies = self._build_canonical_dependencies(enriched_text)
        print(f"   {len(dependencies)} dependencies")

        # Step 6: Metrics
        print("Step 6: Computing metrics...")
        metrics = self._calculate_metrics(services, dependencies, enriched_text, {})

        # Step 7: Traceability
        print("Step 7: Traceability matrix...")
        traceability = self._build_traceability_canonical(enriched_text, services, fr_ids)

        # FR-ID impact map
        svc_fr_ids = self._assign_fr_ids_to_canonical(services, fr_ids, enriched_text)
        impact_map = self._compute_impact_map(svc_fr_ids)

        preview = enriched_text[:500] + "..." if len(enriched_text) > 500 else enriched_text

        result = AnalysisResult(
            project_id=project_id,
            raw_filename=filename,
            raw_content_preview=preview,
            microservices=services,
            dependencies=dependencies,
            metrics=metrics,
            raw_feedback="",
            analysis_metadata={
                "total_services": len(services),
                "total_dependencies": len(dependencies),
                "entities_found": len(entities),
                "actions_found": len(actions),
                "sections_analyzed": len(sections) if sections else 0,
                "nlp_enabled": self.nlp_engine.initialized,
                "traceability": traceability,
                "fr_ids": fr_ids,
                "actors": actors,
                "capabilities": capabilities[:20],
                "impact_map": impact_map,
                "clarifications": clarifications,
                "flow_diagram": flow_diagram,
            },
        )
        print("Analysis complete!")
        return result

    # ─────────────────────────────────────────────────────────────────────────
    # Canonical-6 service builders
    # ─────────────────────────────────────────────────────────────────────────

    def _build_six_canonical_services(
        self,
        text: str,
        actors: List[Dict],
        capabilities: List[Dict],
        entities: List[str],
    ) -> List[MicroserviceSchema]:
        """
        Always produces exactly the 6 canonical microservices.
        Groq LLM enriches each service with document-specific descriptions and APIs.
        Falls back to template content if LLM is unavailable.
        """
        # Summarise actors and capabilities for the LLM prompt
        actor_lines = []
        for a in actors[:6]:
            caps = [c for c in a.get("capabilities", [])[:4] if c]
            actor_lines.append(f"  {a['actor'].capitalize()}: {', '.join(caps) or '(general)'}")

        cap_sample = [c["capability"] for c in capabilities[:15] if c.get("capability")]

        doc_excerpt = text[:2500]

        system_msg = (
            "You are a senior software architect. You output ONLY valid JSON — "
            "no prose, no markdown fences, no explanation."
        )

        user_msg = f"""Given the requirements document below, populate the 6 microservices.

DOCUMENT (excerpt):
{doc_excerpt}

ACTORS DETECTED: {'; '.join(actor_lines) or 'User, Admin, System'}
KEY CAPABILITIES: {', '.join(cap_sample) or 'register, login, browse, order, pay, notify'}

Return ONLY this JSON (no other text):
{{
  "services": [
    {{
      "id": "user-service",
      "description": "<1-2 sentences specific to THIS document — mention concrete feature names>",
      "apis": [
        {{"path": "/api/v1/...", "method": "POST|GET|PUT|DELETE", "description": "<action>"}},
        ...  (3-5 entries grounded in the document requirements)
      ]
    }},
    {{
      "id": "product-service",
      "description": "...",
      "apis": [...]
    }},
    {{
      "id": "cart-service",
      "description": "...",
      "apis": [...]
    }},
    {{
      "id": "order-service",
      "description": "...",
      "apis": [...]
    }},
    {{
      "id": "payment-service",
      "description": "...",
      "apis": [...]
    }},
    {{
      "id": "notification-service",
      "description": "...",
      "apis": [...]
    }}
  ]
}}"""

        llm_data: Dict[str, Any] = {}
        try:
            if _groq_client is None:
                raise RuntimeError("Groq client unavailable")
            resp = _groq_client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {"role": "system", "content": system_msg},
                    {"role": "user",   "content": user_msg},
                ],
                temperature=0.1,
                max_tokens=2000,
            )
            raw = resp.choices[0].message.content.strip()
            # Strip accidental fences
            raw = re.sub(r"^```(?:json)?\s*\n?", "", raw, flags=re.MULTILINE)
            raw = re.sub(r"\n?```\s*$", "", raw, flags=re.MULTILINE)
            llm_data = json.loads(raw)
            print("   LLM service descriptions generated OK")
        except Exception as exc:
            print(f"   LLM enrichment failed ({exc}) — using templates")

        # Map LLM output by service id
        llm_by_id: Dict[str, Dict] = {}
        for svc in llm_data.get("services", []):
            llm_by_id[svc.get("id", "")] = svc

        services: List[MicroserviceSchema] = []
        text_lower = text.lower()

        for tmpl in CANONICAL_SERVICES:
            sid = tmpl["id"]
            llm_svc = llm_by_id.get(sid, {})

            # Description: LLM if available, else template
            description = llm_svc.get("description") or \
                f"Handles all {tmpl['domain']} operations for the system."

            # APIs: merge LLM-provided + template defaults
            apis: List[ApiEndpoint] = []
            seen_paths: Set[str] = set()

            # LLM-grounded endpoints first (inferred=False)
            for ep in llm_svc.get("apis", [])[:5]:
                path = ep.get("path", "")
                method = ep.get("method", "GET").upper()
                desc = ep.get("description", "")
                if path and path not in seen_paths:
                    seen_paths.add(path)
                    apis.append(ApiEndpoint(path=path, method=method, description=desc, inferred=False))

            # Fill with template defaults (inferred=True) up to 6 total
            for method, path, desc in tmpl["default_apis"]:
                if path not in seen_paths and len(apis) < 6:
                    seen_paths.add(path)
                    apis.append(ApiEndpoint(path=path, method=method, description=desc, inferred=True))

            # Keyword match confidence from document
            matched_kws = [kw for kw in tmpl["keywords"] if kw in text_lower]
            confidence = min(100.0, len(matched_kws) * 12.0 + 20.0)

            services.append(MicroserviceSchema(
                id=sid,
                name=tmpl["name"],
                description=description,
                domain=tmpl["domain"],
                database=tmpl["database"],
                database_reasoning=tmpl["database_reasoning"],
                boundary_justification=(
                    f"{tmpl['name']} owns a distinct bounded context "
                    f"({', '.join(matched_kws[:4]) or tmpl['domain'].lower()}). "
                    "Isolated deployment boundary prevents cascading failures."
                ),
                inferred=confidence < 32,   # flagged if domain barely mentioned
                justified_fr_ids=[],
                apis=apis,
                scaling_recommendations=tmpl["scaling"],
                metadata={
                    "confidence": round(confidence, 1),
                    "matched_keywords": matched_kws[:8],
                },
            ))

        return services

    def _build_canonical_dependencies(self, text: str) -> List[DependencyInfo]:
        """Return canonical inter-service dependencies that are relevant to this document."""
        text_lower = text.lower()
        deps: List[DependencyInfo] = []
        for source, target, dep_type, desc in CANONICAL_DEPENDENCIES:
            # Include dep if at least one keyword from either service appears in text
            src_tmpl = next(t for t in CANONICAL_SERVICES if t["id"] == source)
            tgt_tmpl = next(t for t in CANONICAL_SERVICES if t["id"] == target)
            all_kws = src_tmpl["keywords"] + tgt_tmpl["keywords"]
            if any(kw in text_lower for kw in all_kws[:6]):
                deps.append(DependencyInfo(source=source, target=target, type=dep_type, description=desc))
        return deps

    def _assign_fr_ids_to_canonical(
        self,
        services: List[MicroserviceSchema],
        fr_ids: Dict[str, List[Dict]],
        text: str,
    ) -> Dict[str, Set[str]]:
        """Map FR-IDs to canonical services by keyword overlap."""
        svc_fr: Dict[str, Set[str]] = {s.id: set() for s in services}
        tmpl_map = {t["id"]: t["keywords"] for t in CANONICAL_SERVICES}
        for fr_id, occ_list in fr_ids.items():
            for occ in occ_list:
                sent = occ.get("sentence", "").lower()
                for svc in services:
                    kws = tmpl_map.get(svc.id, [])
                    if any(kw in sent for kw in kws):
                        svc_fr[svc.id].add(fr_id)
        # Stamp services
        for svc in services:
            svc.justified_fr_ids = sorted(svc_fr[svc.id])
            if fr_ids and len(svc.justified_fr_ids) < 1:
                svc.inferred = True
        return svc_fr

    def _build_traceability_canonical(
        self,
        text: str,
        services: List[MicroserviceSchema],
        fr_ids: Dict[str, List[Dict]],
    ) -> List[Dict]:
        """Build traceability matrix for canonical services."""
        fr_by_sentence: Dict[str, List[str]] = {}
        for fr_id, occs in fr_ids.items():
            for occ in occs:
                fr_by_sentence.setdefault(occ["sentence"], []).append(fr_id)

        lines = text.split("\n")
        matrix = []
        tmpl_map = {t["id"]: t for t in CANONICAL_SERVICES}

        for svc in services:
            tmpl = tmpl_map.get(svc.id, {})
            kws = tmpl.get("keywords", [])
            relevant = []
            seen: Set[str] = set()
            for line_num, line in enumerate(lines, 1):
                line_strip = line.strip()
                if len(line_strip) <= 20:
                    continue
                if any(kw in line_strip.lower() for kw in kws):
                    display = line_strip[:160]
                    if display not in seen:
                        seen.add(display)
                        relevant.append({
                            "text": display,
                            "line": line_num,
                            "fr_ids": fr_by_sentence.get(line_strip, []),
                        })
                if len(relevant) >= 4:
                    break
            conf = svc.metadata.get("confidence", 50.0) if svc.metadata else 50.0
            matrix.append({
                "service_id": svc.id,
                "service_name": svc.name,
                "domain": svc.domain,
                "confidence": conf,
                "matched_keywords": (svc.metadata or {}).get("matched_keywords", kws[:6]),
                "requirement_sentences": relevant,
                "boundary_justification": svc.boundary_justification,
                "justified_fr_ids": svc.justified_fr_ids,
                "inferred": svc.inferred,
            })
        return matrix

    def _generate_llm_flow_diagram(
        self,
        actors: List[Dict],
        capabilities: List[Dict],
        entities: List[str],
        domains: List[Tuple],
        full_text: str,
    ) -> str:
        """
        Use Groq LLM to generate a semantically correct, DDD-aligned Mermaid flowchart
        of the user journey.  The LLM receives the actual document text as primary
        context (not just noisy NLP extractions) so it can reason about actors, their
        roles, and the correct business flow order itself.

        Falls back to the NLP-heuristic method when Groq is unavailable.
        """
        # ── Build actor summary (used as a hint, not the primary source) ────
        actor_summary_lines: List[str] = []
        for a in actors[:8]:
            caps = [c for c in a.get("capabilities", [])[:5] if c]
            if caps:
                actor_summary_lines.append(f"  • {a['actor'].capitalize()}: {', '.join(caps)}")
            else:
                actor_summary_lines.append(f"  • {a['actor'].capitalize()}")
        actor_hint = "\n".join(actor_summary_lines) if actor_summary_lines else "  • User (inferred)"

        # ── Domain names → bounded context subgraph hints ────────────────────
        domain_names = [d[0] for d in domains[:10]]
        domain_hint = ", ".join(domain_names) if domain_names else "Order, Payment, Notification"

        # ── Pass as much document text as the context window allows ─────────
        # Groq llama3-8b supports 8 k tokens; 3 000 chars ≈ ~750 tokens — safe limit
        doc_text = full_text[:3000]

        system_msg = (
            "You are a senior software architect expert in Domain-Driven Design (DDD) "
            "and microservice architecture. You produce clean, syntactically valid Mermaid "
            "flowcharts. You output ONLY the raw Mermaid diagram — no prose, no code fences."
        )

        user_msg = f"""TASK: Generate a Mermaid `flowchart TD` that shows the complete, semantically correct HIGH-LEVEL USER JOURNEY for the system described in the requirements document below.

═══════════════════════════════════════
REQUIREMENTS DOCUMENT (excerpt):
═══════════════════════════════════════
{doc_text}

═══════════════════════════════════════
HINTS (extracted by NLP — use only as guidance, the document text is authoritative):
Actors detected:
{actor_hint}

DDD Bounded Contexts detected:
{domain_hint}
═══════════════════════════════════════

STRICT RULES — follow every one:
1.  Start with `flowchart TD` (top-down).
2.  Represent each ACTOR as a stadium/rounded shape: `ActorID([Actor Name])`.
3.  Use SUBGRAPHS to group steps by DDD bounded context:
      subgraph PaymentService["Payment & Billing"]
        ...
      end
4.  Show the COMPLETE HAPPY PATH in document order:
    - Registration / Login → Browse / Search → Select / Add to Cart →
      Checkout → Payment → Order Confirmation → Fulfillment / Shipping →
      Delivery → Notification  (adapt to what the document actually describes).
5.  Add DECISION DIAMONDS ({{...}}) for key branching points:
    - Authentication check, Stock availability, Payment success/failure,
      any business rule that produces two outcomes.
6.  Show at least ONE ERROR / FAILURE path per decision (retry, cancel, error page).
7.  System-triggered async steps (emails, notifications, webhooks) use dashed arrows: `-->|async|`.
8.  Each node ID must be a simple alphanumeric token (no spaces, no special chars).
9.  Labels must be human-readable business language — NOT class names or method names.
10. Maximum 30 nodes total. Every subgraph must have at least 2 nodes.
11. Output ONLY the raw Mermaid syntax. No explanation. No ```mermaid fences. No prose.

Generate the diagram now:"""

        try:
            if _groq_client is None:
                raise RuntimeError("Groq client not available")

            response = _groq_client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {"role": "system", "content": system_msg},
                    {"role": "user",   "content": user_msg},
                ],
                temperature=0.15,   # low temperature → more deterministic, structurally correct output
                max_tokens=1800,
            )
            raw = response.choices[0].message.content.strip()

            # ── Strip accidental markdown fences ─────────────────────────────
            raw = re.sub(r"^```(?:mermaid)?\s*\n?", "", raw, flags=re.MULTILINE)
            raw = re.sub(r"\n?```\s*$", "", raw, flags=re.MULTILINE)
            raw = raw.strip()

            # ── Validate: must begin with a Mermaid chart declaration ────────
            if re.match(r"^(flowchart|graph)\s+", raw, re.IGNORECASE):
                # Basic structural sanity: must have at least 3 arrows
                if raw.count("-->") >= 3:
                    print("   ✅ LLM flow diagram generated via Groq")
                    return raw
                else:
                    print("   ⚠️  LLM diagram is too sparse — retrying with fallback")
            else:
                print("   ⚠️  LLM returned non-Mermaid output — falling back to NLP method")

        except Exception as e:
            print(f"   ⚠️  Groq flow generation failed ({e}) — falling back to NLP method")

        # ── Fallback: NLP-heuristic generation ───────────────────────────────
        return self.nlp_engine.extract_user_flows(full_text, actors, capabilities)

    def _build_microservice_schema(
        self,
        domain_name: str,
        keywords: List[str],
        text: str,
        actions: List[str],
        entities: List[str],
        concepts: List[str],
        boundary_justification: str = "",
    ) -> MicroserviceSchema:
        """Build a complete microservice schema with APIs, database, and recommendations"""
        
        # Generate service ID
        service_id = domain_name.lower().replace(" ", "-").replace("&", "and")
        
        # Generate description
        description = self._generate_service_description(domain_name, keywords, text)
        
        # Suggest database type
        db_type, db_reason = self.nlp_engine.suggest_database_type(domain_name, keywords)
        
        # Extract action verbs from document text near this domain's keywords
        doc_verbs = self.nlp_engine.extract_domain_action_verbs(text, keywords)

        # Generate API endpoints — document verbs take priority over templates
        apis = self._generate_api_endpoints(domain_name, keywords, actions, entities, doc_verbs)
        
        # Generate scaling recommendations
        scaling_recs = self._generate_scaling_recommendations(domain_name, keywords)
        
        # Calculate cohesion score for this service
        cohesion = self.nlp_engine.calculate_cohesion_score(keywords, text)
        
        return MicroserviceSchema(
            id=service_id,
            name=self._format_service_name(domain_name),
            description=description,
            domain=domain_name,
            database=db_type,
            database_reasoning=db_reason,
            boundary_justification=boundary_justification,
            apis=apis,
            scaling_recommendations=scaling_recs,
            metadata={
                "cohesion_score": round(cohesion, 2),
                "keyword_count": len(keywords),
                "confidence": "high" if len(keywords) > 3 else "medium"
            }
        )
        
    def _format_service_name(self, domain_name: str) -> str:
        """Convert domain name to proper service name"""
        # "Authentication & Identity" -> "Identity Service"
        name_map = {
            "Authentication & Identity": "Identity Service",
            "Order Management": "Order Management Service",
            "Payment & Billing": "Payment & Billing Service",
            "Notification & Communication": "Notification Dispatcher Service",
            "Inventory & Catalog": "Catalog & Stock Service",
            "User Management": "User Profile Service",
            "Analytics & Reporting": "Business Analytics Service",
            "Search & Discovery": "Search & Discovery Service",
            "Content Management": "Content Management Service",
            "Shipping & Logistics": "Shipping & Logistics Service",
            "Customer Support": "Customer Support Service",
            "Product Reviews": "Review & Rating Service"
        }
        
        return name_map.get(domain_name, domain_name + " Service")
        
    def _generate_service_description(self, domain_name: str, keywords: List[str], text: str) -> str:
        """Generate intelligent service description based on domain and keywords"""
        
        descriptions = {
            "Authentication & Identity": "Manages user authentication, authorization, JWT token lifecycle, and role-based access control with secure credential validation.",
            "Order Management": "Processes customer orders, manages order lifecycle states, handles inventory reservations, and coordinates fulfillment workflows.",
            "Payment & Billing": "Integrates with payment gateways (Stripe, PayPal), processes transactions, manages invoices, and maintains financial ledgers.",
            "Notification & Communication": "Handles asynchronous notification delivery through multiple channels (email, SMS, push) with template management and delivery tracking.",
            "Inventory & Catalog": "Maintains product catalog, tracks real-time inventory levels across warehouses, and manages stock reservations and replenishment.",
            "User Management": "Manages user profiles, preferences, account settings, and customer data with GDPR compliance and data privacy controls.",
            "Analytics & Reporting": "Aggregates system events, generates business intelligence reports, and provides real-time dashboards with KPI tracking.",
            "Search & Discovery": "Provides full-text search, filtering, and recommendation capabilities with indexed product catalogs and personalized results.",
            "Content Management": "Manages digital content, media assets, document storage, and content delivery with versioning and access controls.",
            "Shipping & Logistics": "Handles shipping address validation, carrier integration, package tracking, and delivery status updates.",
            "Customer Support": "Manages support tickets, customer inquiries, chat sessions, and knowledge base with automated routing and escalation.",
            "Product Reviews": "Collects and manages product reviews, ratings, customer feedback with moderation and sentiment analysis."
        }
        
        return descriptions.get(domain_name, f"Handles {domain_name.lower()} related operations and business logic.")
        
    def _generate_api_endpoints(
        self, 
        domain_name: str,
        keywords: List[str],
        actions: List[str],
        entities: List[str],
        doc_verbs: List[Tuple[str, str, int]] = None,
    ) -> List[ApiEndpoint]:
        """
        Generate RESTful API endpoints.
        Priority: actual verb-entity pairs found in the document (inferred=False)
        → template entries for gaps (inferred=True).
        """
        
        endpoints = []
        service_path = domain_name.lower().replace(" ", "").replace("&", "")
        
        # Standard CRUD operations mapping
        crud_templates = {
            "Authentication & Identity": [
                {"path": f"/api/v1/auth/signup", "method": "POST", "desc": "Register a new user with secure credentials"},
                {"path": f"/api/v1/auth/login", "method": "POST", "desc": "Authenticate user and issue JWT token"},
                {"path": f"/api/v1/auth/refresh", "method": "POST", "desc": "Refresh expired JWT token"},
                {"path": f"/api/v1/auth/logout", "method": "POST", "desc": "Invalidate user session and revoke token"},
                {"path": f"/api/v1/users/profile", "method": "GET", "desc": "Retrieve authenticated user profile"},
            ],
            "Order Management": [
                {"path": f"/api/v1/orders", "method": "POST", "desc": "Create a new customer order"},
                {"path": f"/api/v1/orders/{{id}}", "method": "GET", "desc": "Retrieve order details and history"},
                {"path": f"/api/v1/orders", "method": "GET", "desc": "List all orders with pagination and filters"},
                {"path": f"/api/v1/orders/{{id}}/cancel", "method": "PUT", "desc": "Cancel order and trigger refund workflow"},
                {"path": f"/api/v1/orders/{{id}}/status", "method": "GET", "desc": "Get real-time order status"},
            ],
            "Payment & Billing": [
                {"path": f"/api/v1/payments/charge", "method": "POST", "desc": "Process payment and charge customer card"},
                {"path": f"/api/v1/payments/refund", "method": "POST", "desc": "Issue refund for completed transaction"},
                {"path": f"/api/v1/invoices", "method": "GET", "desc": "List customer invoices and billing history"},
                {"path": f"/api/v1/payments/{{id}}/status", "method": "GET", "desc": "Check payment transaction status"},
            ],
            "Notification & Communication": [
                {"path": f"/api/v1/notifications/send", "method": "POST", "desc": "Queue notification for delivery"},
                {"path": f"/api/v1/notifications/{{id}}/status", "method": "GET", "desc": "Check notification delivery status"},
                {"path": f"/api/v1/notifications/templates", "method": "GET", "desc": "List available notification templates"},
            ],
            "Inventory & Catalog": [
                {"path": f"/api/v1/catalog/products", "method": "GET", "desc": "List products with filters and search"},
                {"path": f"/api/v1/catalog/products/{{id}}", "method": "GET", "desc": "Get detailed product information"},
                {"path": f"/api/v1/inventory/reserve", "method": "POST", "desc": "Reserve inventory for order"},
                {"path": f"/api/v1/inventory/{{sku}}/stock", "method": "GET", "desc": "Check current stock levels"},
            ],
            "User Management": [
                {"path": f"/api/v1/users", "method": "POST", "desc": "Create new user account"},
                {"path": f"/api/v1/users/{{id}}", "method": "GET", "desc": "Retrieve user profile data"},
                {"path": f"/api/v1/users/{{id}}", "method": "PUT", "desc": "Update user profile information"},
                {"path": f"/api/v1/users/{{id}}", "method": "DELETE", "desc": "Deactivate user account"},
            ],
            "Analytics & Reporting": [
                {"path": f"/api/v1/analytics/dashboard", "method": "GET", "desc": "Get dashboard metrics and KPIs"},
                {"path": f"/api/v1/analytics/reports", "method": "GET", "desc": "List available analytical reports"},
                {"path": f"/api/v1/analytics/events", "method": "POST", "desc": "Ingest system event for tracking"},
            ],
        }
        
        # Get predefined endpoints or generate generic ones
        if domain_name in crud_templates:
            endpoint_defs = crud_templates[domain_name]
        else:
            # Generate generic CRUD endpoints
            resource = domain_name.lower().replace(" ", "")
            endpoint_defs = [
                {"path": f"/api/v1/{resource}", "method": "GET", "desc": f"List {domain_name} resources"},
                {"path": f"/api/v1/{resource}", "method": "POST", "desc": f"Create new {domain_name} resource"},
                {"path": f"/api/v1/{resource}/{{id}}", "method": "GET", "desc": f"Retrieve {domain_name} by ID"},
                {"path": f"/api/v1/{resource}/{{id}}", "method": "PUT", "desc": f"Update {domain_name} resource"},
            ]
            
        # ── Document-grounded endpoints (inferred=False) ─────────────────────
        VERB_METHOD: Dict[str, str] = {
            "create": "POST", "add": "POST", "register": "POST", "submit": "POST",
            "place": "POST", "upload": "POST", "send": "POST", "post": "POST",
            "get": "GET", "retrieve": "GET", "fetch": "GET", "view": "GET",
            "list": "GET", "search": "GET", "find": "GET", "show": "GET", "browse": "GET",
            "update": "PUT", "modify": "PUT", "edit": "PUT", "change": "PUT", "set": "PUT",
            "delete": "DELETE", "remove": "DELETE", "cancel": "DELETE", "deactivate": "DELETE",
        }
        doc_paths_used: Set[str] = set()
        if doc_verbs:
            for verb, entity, _line in doc_verbs[:6]:
                method = VERB_METHOD.get(verb, "POST")
                entity_slug = entity.replace(" ", "-").rstrip("s")
                if method in ("GET", "DELETE", "PUT"):
                    path = f"/api/v1/{entity_slug}s/{{id}}"
                else:
                    path = f"/api/v1/{entity_slug}s"
                if path not in doc_paths_used:
                    doc_paths_used.add(path)
                    endpoints.append(ApiEndpoint(
                        path=path,
                        method=method,
                        description=f"{verb.capitalize()} {entity} — derived from document line {_line}",
                        inferred=False,
                    ))

        # ── Template-based endpoints for gaps (inferred=True) ─────────────────
        for ep_def in endpoint_defs:
            if ep_def["path"] not in doc_paths_used:
                endpoints.append(ApiEndpoint(
                    path=ep_def["path"],
                    method=ep_def["method"],
                    description=ep_def["desc"],
                    inferred=not bool(doc_verbs),  # inferred only when doc gave us nothing
                ))

        return endpoints[:8]  # cap at 8 per service
        
    def _generate_scaling_recommendations(self, domain_name: str, keywords: List[str]) -> List[str]:
        """Generate intelligent scaling and architecture recommendations"""
        
        recommendations = {
            "Authentication & Identity": [
                "Implement Redis caching layer for session management and token blacklisting",
                "Deploy behind API Gateway with rate limiting (1000 req/min per client)",
                "Use read replicas for user profile lookups to handle high read traffic",
                "Implement OAuth 2.0 and SSO for enterprise integrations"
            ],
            "Order Management": [
                "Implement event sourcing to track complete order lifecycle history",
                "Use message queue (RabbitMQ/Kafka) for async order processing",
                "Deploy database read replicas for order history queries",
                "Implement circuit breaker pattern for external service calls",
                "Use saga pattern for distributed transaction management"
            ],
            "Payment & Billing": [
                "Implement retry logic with exponential backoff for payment gateway calls",
                "Use circuit breaker pattern (Hystrix/Resilience4j) for external API failures",
                "Queue payment processing jobs asynchronously to handle spikes",
                "Implement idempotency keys to prevent duplicate charges",
                "Enable PCI-DSS compliant encryption for sensitive payment data"
            ],
            "Notification & Communication": [
                "Horizontal auto-scaling based on message queue depth",
                "Use pub/sub pattern (Redis Pub/Sub, AWS SNS) for event-driven notifications",
                "Implement worker pool for parallel notification delivery",
                "Add retry mechanism with dead letter queue for failed deliveries"
            ],
            "Inventory & Catalog": [
                "Deploy CDN (CloudFlare, AWS CloudFront) for product images and catalog data",
                "Implement Redis master-slave caching for frequently accessed products",
                "Use distributed locking (Redis, etcd) for inventory reservation",
                "Implement eventual consistency for non-critical stock updates"
            ],
            "Analytics & Reporting": [
                "Use Kafka streaming pipeline to decouple analytics from transactional systems",
                "Implement CQRS pattern with separate read/write databases",
                "Use columnar storage (ClickHouse, BigQuery) for analytical queries",
                "Deploy Elasticsearch for real-time aggregations and dashboards"
            ],
        }
        
        default_recs = [
            "Implement health check endpoints for orchestrator monitoring",
            "Use containerization (Docker) with orchestration (Kubernetes)",
            "Implement centralized logging with correlation IDs",
            "Deploy behind load balancer for high availability"
        ]
        
        return recommendations.get(domain_name, default_recs)
        
    def _extract_dependencies(
        self, 
        service_dicts: List[Dict], 
        text: str,
        services: List[MicroserviceSchema]
    ) -> List[DependencyInfo]:
        """
        Extract inter-service dependencies using keyword-based substring matching.
        Service IDs are matched by domain keywords so rules never fail due to exact ID mismatches.
        """
        dependencies = []
        text_lower = text.lower()
        service_ids = [s.id for s in services]

        def find_service(keywords: List[str]) -> str:
            """Return the first service ID that contains any of the given keywords."""
            for sid in service_ids:
                if any(kw in sid for kw in keywords):
                    return sid
            return None

        def find_services(keywords: List[str]) -> List[str]:
            """Return all service IDs that contain any of the given keywords."""
            return [sid for sid in service_ids if any(kw in sid for kw in keywords)]

        def add_dep(source_id: str, target_id: str, dep_type: str, desc: str):
            """Add a dependency if both services exist and it is not a duplicate."""
            if not source_id or not target_id:
                return
            if source_id == target_id:
                return
            if source_id not in service_ids or target_id not in service_ids:
                return
            if not any(d.source == source_id and d.target == target_id for d in dependencies):
                dependencies.append(DependencyInfo(
                    source=source_id,
                    target=target_id,
                    type=dep_type,
                    description=desc
                ))

        # ── Rule set ──────────────────────────────────────────────────────────
        # Each rule: text_pattern must appear in document, then for every
        # service matching from_keywords → add dep to service matching to_keywords.
        rules = [
            # Every transactional service calls auth to validate tokens
            {
                "text_pattern": "auth",
                "from_keywords_groups": [
                    ["order"], ["payment", "billing"], ["catalog", "inventory"],
                    ["user", "profile"], ["notification", "communication"],
                    ["shipping", "logistics"], ["search", "discovery"],
                    ["support"], ["review", "rating"], ["content"],
                ],
                "to_keywords": ["auth", "identity"],
                "type": "sync",
                "desc": "Validates JWT tokens and retrieves user permissions"
            },
            # Order → Payment (sync: checkout must confirm payment before proceeding)
            {
                "text_pattern": "order",
                "from_keywords_groups": [["order"]],
                "to_keywords": ["payment", "billing"],
                "type": "sync",
                "desc": "Processes payment transaction during order checkout"
            },
            # Order → Inventory/Catalog (sync: must confirm stock before confirming order)
            {
                "text_pattern": "order",
                "from_keywords_groups": [["order"]],
                "to_keywords": ["catalog", "inventory"],
                "type": "sync",
                "desc": "Reserves inventory and validates product availability"
            },
            # Order → Notification (async: fire-and-forget confirmation email/SMS)
            {
                "text_pattern": "order",
                "from_keywords_groups": [["order"]],
                "to_keywords": ["notification", "communication"],
                "type": "async",
                "desc": "Sends order confirmation and status updates via message queue"
            },
            # Order → Shipping (async: fulfillment triggers shipment creation)
            {
                "text_pattern": "shipping",
                "from_keywords_groups": [["order"]],
                "to_keywords": ["shipping", "logistics"],
                "type": "async",
                "desc": "Initiates shipment after order is confirmed and paid"
            },
            # Payment → Notification (async: payment events trigger customer alerts)
            {
                "text_pattern": "payment",
                "from_keywords_groups": [["payment", "billing"]],
                "to_keywords": ["notification", "communication"],
                "type": "async",
                "desc": "Triggers payment success/failure notification via event bus"
            },
            # Shipping → Notification (async: delivery status updates)
            {
                "text_pattern": "shipping",
                "from_keywords_groups": [["shipping", "logistics"]],
                "to_keywords": ["notification", "communication"],
                "type": "async",
                "desc": "Notifies customer on shipment and delivery tracking updates"
            },
            # Search → Catalog (sync: search queries the product index)
            {
                "text_pattern": "search",
                "from_keywords_groups": [["search", "discovery"]],
                "to_keywords": ["catalog", "inventory"],
                "type": "sync",
                "desc": "Queries product catalog index for full-text search results"
            },
            # Support → User (sync: agents need customer profile context)
            {
                "text_pattern": "support",
                "from_keywords_groups": [["support"]],
                "to_keywords": ["user", "profile"],
                "type": "sync",
                "desc": "Fetches customer profile data to provide support context"
            },
            # Support → Order (sync: agents look up order history for issue resolution)
            {
                "text_pattern": "support",
                "from_keywords_groups": [["support"]],
                "to_keywords": ["order"],
                "type": "sync",
                "desc": "Retrieves order history to resolve customer complaints"
            },
            # Review → Catalog (async: reviews are linked to product entries)
            {
                "text_pattern": "review",
                "from_keywords_groups": [["review", "rating"]],
                "to_keywords": ["catalog", "inventory"],
                "type": "async",
                "desc": "Associates submitted product review with catalog entry"
            },
            # All key services stream events to Analytics (async: never block on analytics)
            {
                "text_pattern": "analytics",
                "from_keywords_groups": [
                    ["order"], ["payment", "billing"], ["catalog", "inventory"],
                    ["user", "profile"], ["shipping", "logistics"], ["search"],
                ],
                "to_keywords": ["analytics", "reporting"],
                "type": "async",
                "desc": "Streams operational events for business intelligence and reporting"
            },
        ]

        for rule in rules:
            if rule["text_pattern"] not in text_lower:
                continue

            target_id = find_service(rule["to_keywords"])
            if not target_id:
                continue

            for from_keywords in rule["from_keywords_groups"]:
                for source_id in find_services(from_keywords):
                    add_dep(source_id, target_id, rule["type"], rule["desc"])

        return dependencies
        
    def _compute_svc_fr_ids(
        self,
        services: List[MicroserviceSchema],
        significant_domains: List[Tuple],
        fr_ids: Dict[str, List[Dict]],
    ) -> Dict[str, Set[str]]:
        """
        Assign each FR-ID to every service whose matched keywords appear in
        that FR-ID's source sentence.  Central computation reused by the gate,
        metrics, impact map, and traceability builder.
        """
        kw_map: Dict[str, List[str]] = {
            svc.id: d[2] for svc, d in zip(services, significant_domains)
        }
        svc_fr: Dict[str, Set[str]] = {svc.id: set() for svc in services}
        for fr_id, occ_list in fr_ids.items():
            for occ in occ_list:
                sentence_lower = occ["sentence"].lower()
                for svc_id, kws in kw_map.items():
                    if any(kw in sentence_lower for kw in kws):
                        svc_fr[svc_id].add(fr_id)
        return svc_fr

    def _apply_fr_id_gate(
        self,
        services: List[MicroserviceSchema],
        svc_fr_ids: Dict[str, Set[str]],
        total_fr_count: int,
    ) -> List[MicroserviceSchema]:
        """
        When the document contains FR-IDs, stamp each service's inferred flag.
        A service with < 2 FR-IDs is inferred — it may be noise from keyword
        frequency, not from a stated requirement.  We keep it but flag it so
        the UI can surface it clearly rather than silently hallucinating.
        """
        for svc in services:
            fr_set = svc_fr_ids.get(svc.id, set())
            svc.justified_fr_ids = sorted(fr_set)
            if total_fr_count >= 2:
                svc.inferred = len(fr_set) < 2
        return services

    def _compute_impact_map(
        self, svc_fr_ids: Dict[str, Set[str]]
    ) -> Dict[str, List[str]]:
        """
        Invert service→FR-IDs to FR-ID→[service_ids].
        Used for change-impact analysis: if FR-X changes, which services are affected?
        """
        impact: Dict[str, List[str]] = {}
        for svc_id, fr_set in svc_fr_ids.items():
            for fr_id in fr_set:
                impact.setdefault(fr_id, []).append(svc_id)
        return impact

    def _merge_overlapping_services(
        self,
        services: List[MicroserviceSchema],
        significant_domains: List[Tuple],
        fr_ids: Dict[str, List[Dict]],
    ) -> Tuple[List[MicroserviceSchema], List[Tuple]]:
        """
        Drop the lower-scoring partner of any service pair whose FR-IDs overlap > 60%.
        An FR-ID belongs to a service when it appears in a sentence that also
        contains at least one of the service's matched domain keywords.

        This is the merge gate that prevents over-engineering: two supposed
        boundaries that the document treats as a single concern collapse into one.
        """
        if not fr_ids:
            return services, significant_domains

        # Build per-service FR-ID sets
        kw_map: Dict[str, List[str]] = {
            svc.id: d[2] for svc, d in zip(services, significant_domains)
        }
        svc_fr: Dict[str, set] = {}
        for svc in services:
            matched: set = set()
            for fr_id, occ_list in fr_ids.items():
                for occ in occ_list:
                    if any(kw in occ["sentence"].lower() for kw in kw_map[svc.id]):
                        matched.add(fr_id)
                        break
            svc_fr[svc.id] = matched

        score_map: Dict[str, float] = {
            svc.id: d[1] for svc, d in zip(services, significant_domains)
        }
        to_remove: set = set()

        for i in range(len(services)):
            if services[i].id in to_remove:
                continue
            for j in range(i + 1, len(services)):
                if services[j].id in to_remove:
                    continue
                a_fr = svc_fr[services[i].id]
                b_fr = svc_fr[services[j].id]
                if not a_fr or not b_fr:
                    continue
                shared = len(a_fr & b_fr)
                overlap = shared / min(len(a_fr), len(b_fr))
                if overlap > 0.60:
                    drop_id = (
                        services[j].id
                        if score_map[services[i].id] >= score_map[services[j].id]
                        else services[i].id
                    )
                    to_remove.add(drop_id)
                    keep_name = next(
                        s.name for s in services
                        if s.id != drop_id and s.id in {services[i].id, services[j].id}
                    )
                    drop_name = next(s.name for s in services if s.id == drop_id)
                    print(f"   🔀 Merged '{drop_name}' into '{keep_name}' ({overlap:.0%} FR-ID overlap)")

        if not to_remove:
            return services, significant_domains

        kept_svcs = [s for s in services if s.id not in to_remove]
        kept_doms = [d for s, d in zip(services, significant_domains) if s.id not in to_remove]
        return kept_svcs, kept_doms

    def _build_traceability(
        self,
        text: str,
        services: List[MicroserviceSchema],
        significant_domains: List[Tuple],
        fr_ids: Dict[str, List[Dict]] = None,
        svc_fr_ids: Dict[str, Set[str]] = None,
    ) -> List[Dict]:
        """
        Build a requirements-traceability matrix with:
        • Line-level provenance on every matched sentence
        • justified_fr_ids: the exact FR-IDs that justify this service boundary
        • boundary_justification: the DDD split rationale
        """
        # Build sentence → FR-IDs reverse lookup
        fr_by_sentence: Dict[str, List[str]] = {}
        if fr_ids:
            for fr_id, occurrences in fr_ids.items():
                for occ in occurrences:
                    fr_by_sentence.setdefault(occ["sentence"], []).append(fr_id)

        lines = text.split('\n')
        matrix = []
        for service, domain_entry in zip(services, significant_domains):
            domain_name, confidence, matched_keywords = domain_entry[0], domain_entry[1], domain_entry[2]
            relevant = []
            seen: set = set()
            for line_num, line in enumerate(lines, 1):
                line_strip = line.strip()
                if len(line_strip) <= 20:
                    continue
                if any(kw in line_strip.lower() for kw in matched_keywords):
                    display = line_strip if len(line_strip) <= 160 else line_strip[:157] + "..."
                    if display not in seen:
                        seen.add(display)
                        relevant.append({
                            "text": display,
                            "line": line_num,
                            "fr_ids": fr_by_sentence.get(line_strip, []),
                        })
                if len(relevant) >= 3:
                    break

            matrix.append({
                "service_id": service.id,
                "service_name": service.name,
                "domain": domain_name,
                "confidence": round(confidence, 1),
                "matched_keywords": matched_keywords[:6],
                "requirement_sentences": relevant,
                "boundary_justification": service.boundary_justification,
                "justified_fr_ids": sorted(svc_fr_ids.get(service.id, set())) if svc_fr_ids else service.justified_fr_ids,
                "inferred": service.inferred,
            })

        return matrix

    def _real_coupling_from_fr_ids(
        self,
        services: List[MicroserviceSchema],
        svc_fr_ids: Dict[str, Set[str]] = None,
    ) -> int:
        """
        Real coupling = mean fraction of each service's FR-IDs that are also
        cited by at least one other service, scaled 0-100.

        Formula: mean( |cross_fr(S)| / |fr(S)| ) × 100
        Returns None when no FR-ID data is available (triggers structural fallback).
        """
        if not svc_fr_ids:
            return None
        per_svc = []
        for svc in services:
            fr_set = svc_fr_ids.get(svc.id, set())
            if not fr_set:
                continue
            cross = {
                fr for fr in fr_set
                if any(fr in svc_fr_ids.get(o.id, set()) for o in services if o.id != svc.id)
            }
            per_svc.append(len(cross) / len(fr_set))
        if not per_svc:
            return None
        return min(95, int(sum(per_svc) / len(per_svc) * 100))

    def _real_cohesion(
        self,
        fr_set: Set[str],
        matched_kws: List[str],
        fr_ids_data: Dict[str, List[Dict]],
    ) -> float:
        """
        Cohesion = % of FR-ID pairs within a service that share ≥1 domain keyword.
        Formula: |sharing_pairs| / |total_pairs| × 100
        Returns 100 for single-FR-ID services (trivially cohesive).
        """
        if len(fr_set) <= 1:
            return 100.0 if fr_set else 50.0
        fr_list = list(fr_set)
        fr_kws: Dict[str, Set[str]] = {}
        for fr_id in fr_list:
            occs = fr_ids_data.get(fr_id, [])
            kw_set: Set[str] = set()
            for occ in occs:
                s = occ.get("sentence", "").lower()
                for kw in matched_kws:
                    if kw in s:
                        kw_set.add(kw)
            fr_kws[fr_id] = kw_set
        total_pairs = len(fr_list) * (len(fr_list) - 1) / 2
        sharing = sum(
            1
            for i, a in enumerate(fr_list)
            for b in fr_list[i + 1 :]
            if fr_kws.get(a, set()) & fr_kws.get(b, set())
        )
        return round(sharing / total_pairs * 100, 1) if total_pairs else 50.0

    def _calculate_metrics(
        self,
        services: List[MicroserviceSchema],
        dependencies: List[DependencyInfo],
        text: str,
        svc_fr_ids: Dict[str, Set[str]] = None,
    ) -> MetricScores:
        """
        Calculate architecture quality metrics.

        Coupling  (lower = better): when FR-ID data is available, uses the real
          formula — cross-service FR-ID references / total FR-IDs per service,
          averaged across services. Formula: mean(|cross_fr(S)| / |fr(S)|) × 100
          Fallback to structural avg-deps/service when no FR-IDs exist.

        Cohesion  (stored per-service in metadata): % of FR-ID pairs in a service
          that share ≥1 domain keyword.
          Formula: |sharing_pairs| / |total_pairs| × 100

        Scalability & Fault Isolation: remain structural (dependency topology).
        """
        n_services = len(services)
        n_deps = len(dependencies)

        if n_services == 0:
            return MetricScores(scalability=0, coupling=100, maintainability=0, fault_isolation=0)

        avg_deps = n_deps / n_services

        # ── Real coupling from FR-ID cross-references ─────────────────────
        real_coupling = self._real_coupling_from_fr_ids(services, svc_fr_ids)

        # ── Real cohesion per service (stored in metadata) ────────────────
        # Formula: |sharing_pairs| / |total_pairs| × 100
        # where a "sharing pair" is two FR-IDs in the same service that reference
        # at least one common domain keyword.
        if svc_fr_ids:
            for svc in services:
                fr_set = svc_fr_ids.get(svc.id, set())
                cohesion = self._real_cohesion(fr_set, svc.justified_fr_ids or list(fr_set), {})
                if svc.metadata is not None:
                    svc.metadata["cohesion_score"] = round(cohesion, 1)
                    svc.metadata["fr_id_count"] = len(fr_set)

        # ── Coupling ─────────────────────────────────────────────────────────
        # Use real FR-ID cross-reference formula when data is available.
        # Formula: mean(|cross_fr(S)| / |fr(S)|) × 100, averaged over services.
        # Fallback: structural avg-deps/service bands when FR-IDs absent.
        if real_coupling is not None:
            coupling_score = real_coupling
        elif avg_deps == 0:
            coupling_score = 35
        elif avg_deps <= 1:
            coupling_score = int(20 + avg_deps * 15)
        elif avg_deps <= 3:
            coupling_score = int(35 + (avg_deps - 1) * 10)
        elif avg_deps <= 5:
            coupling_score = int(55 + (avg_deps - 3) * 10)
        else:
            coupling_score = min(95, int(75 + (avg_deps - 5) * 4))

        # ── Scalability ───────────────────────────────────────────────────────
        # More services → each can scale independently.
        # High coupling cancels the benefit (can't deploy/scale independently).
        #   3  services → base 57  |  12 services → base 93
        scalability_base = min(93, 45 + n_services * 4)
        # Penalty kicks in only when coupling is above the healthy threshold (55)
        coupling_excess = max(0, coupling_score - 55)
        scalability_score = max(30, int(scalability_base - coupling_excess * 0.6))

        # ── Maintainability ───────────────────────────────────────────────────
        # DDD optimal range: 5-10 services.
        # Too few (1-4) → likely a hidden monolith. Too many (>12) → cognitive overload.
        # Coupling also makes maintenance harder across service boundaries.
        if n_services <= 2:
            maint_base = 35
        elif n_services <= 5:
            maint_base = 50 + (n_services - 3) * 8    # 50 → 66
        elif n_services <= 10:
            maint_base = 66 + (n_services - 5) * 3    # 66 → 81
        else:
            maint_base = max(55, 81 - (n_services - 10) * 4)  # degrades past 10

        coupling_excess = max(0, coupling_score - 40)
        maintainability_score = max(30, int(maint_base - coupling_excess * 0.4))

        # ── Fault Isolation ───────────────────────────────────────────────────
        # Async dependencies buffer failures (queue absorbs spikes, retries are safe).
        # Sync dependencies create cascading failure paths.
        # With no dependency data: neutral base of 50.
        async_deps = sum(1 for d in dependencies if d.type == "async")
        sync_deps = n_deps - async_deps

        if n_deps == 0:
            fault_isolation_score = 50  # neutral — no dependency topology known
        else:
            async_ratio = async_deps / n_deps
            # Ratio 0 (all sync) → base 35 | ratio 1 (all async) → base 90
            fi_base = int(35 + async_ratio * 55)
            # Each sync dep beyond 3 adds additional cascading risk
            extra_sync_penalty = max(0, sync_deps - 3) * 3
            fault_isolation_score = min(95, max(25, fi_base - extra_sync_penalty))

        return MetricScores(
            scalability=scalability_score,
            coupling=coupling_score,
            maintainability=maintainability_score,
            fault_isolation=fault_isolation_score
        )


# Singleton instance
_analyzer_instance = None

def get_analyzer() -> RequirementAnalyzer:
    """Get or create singleton analyzer instance"""
    global _analyzer_instance
    if _analyzer_instance is None:
        _analyzer_instance = RequirementAnalyzer()
    return _analyzer_instance
