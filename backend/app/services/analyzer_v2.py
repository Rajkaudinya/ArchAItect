"""
Advanced AI-Powered Microservice Architecture Analyzer
Uses NLP, entity recognition, semantic clustering, and dependency analysis
"""
import re
import json
from typing import Dict, Any, List, Tuple
from collections import defaultdict
from app.models.analysis import (
    AnalysisResult, MicroserviceSchema, ApiEndpoint, 
    DependencyInfo, MetricScores
)
from app.services.nlp_engine import NLPEngine

class RequirementAnalyzer:
    def __init__(self):
        self.nlp_engine = NLPEngine()
        
    def analyze_requirements(self, text: str, project_id: str, filename: str, 
                           sections: Dict[str, str] = None) -> AnalysisResult:
        """
        Advanced AI-powered analysis of requirements using NLP and semantic understanding.
        
        Process:
        1. Extract entities, actions, and concepts using NLP
        2. Identify service domains using semantic similarity
        3. Generate API endpoints based on actions and entities
        4. Extract dependencies through co-occurrence analysis
        5. Calculate quality metrics (coupling, cohesion, etc.)
        """
        print(f"🔍 Analyzing requirements document: {filename}")
        
        # Step 1: Entity and concept extraction
        print("📊 Step 1: Extracting entities and concepts...")
        extraction = self.nlp_engine.extract_entities_and_actions(text)
        entities = extraction.get("entities", [])
        actions = extraction.get("actions", [])
        concepts = extraction.get("concepts", [])
        
        print(f"   Found: {len(entities)} entities, {len(actions)} actions, {len(concepts)} concepts")
        
        # Step 2: Identify service domains
        print("🎯 Step 2: Identifying microservice domains...")
        detected_domains = self.nlp_engine.identify_service_domains(text, sections)
        
        # Filter domains with sufficient confidence
        significant_domains = [d for d in detected_domains if d[1] > 15]
        
        # Ensure we have at least some core services
        if len(significant_domains) < 2:
            significant_domains = detected_domains[:5]  # Take top 5
            
        print(f"   Detected {len(significant_domains)} microservice domains")
        
        # Step 3: Build microservices
        print("⚙️  Step 3: Generating microservice schemas...")
        services = []
        
        for domain_name, confidence, matched_keywords in significant_domains:
            service = self._build_microservice_schema(
                domain_name, 
                matched_keywords, 
                text, 
                actions, 
                entities,
                concepts
            )
            if service:
                services.append(service)
                
        print(f"   Generated {len(services)} microservices")
        
        # Step 4: Extract dependencies
        print("🔗 Step 4: Analyzing service dependencies...")
        service_dicts = [
            {
                "name": s.id,
                "keywords": matched_keywords
            }
            for s, (_, _, matched_keywords) in zip(services, significant_domains)
        ]
        
        dependencies = self._extract_dependencies(service_dicts, text, services)
        print(f"   Identified {len(dependencies)} dependencies")
        
        # Step 5: Calculate metrics
        print("📈 Step 5: Computing architecture quality metrics...")
        metrics = self._calculate_metrics(services, dependencies, text)

        # Step 6: Build traceability matrix
        print("🗂️  Step 6: Building requirements traceability matrix...")
        traceability = self._build_traceability(text, services, significant_domains)
        
        # Generate content preview
        preview = text[:500] + "..." if len(text) > 500 else text
        
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
                "concepts_found": len(concepts),
                "sections_analyzed": len(sections) if sections else 0,
                "nlp_enabled": self.nlp_engine.initialized,
                "traceability": traceability
            }
        )
        
        print("✅ Analysis complete!")
        return result
        
    def _build_microservice_schema(
        self, 
        domain_name: str, 
        keywords: List[str],
        text: str,
        actions: List[str],
        entities: List[str],
        concepts: List[str]
    ) -> MicroserviceSchema:
        """Build a complete microservice schema with APIs, database, and recommendations"""
        
        # Generate service ID
        service_id = domain_name.lower().replace(" ", "-").replace("&", "and")
        
        # Generate description
        description = self._generate_service_description(domain_name, keywords, text)
        
        # Suggest database type
        db_type, db_reason = self.nlp_engine.suggest_database_type(domain_name, keywords)
        
        # Generate API endpoints
        apis = self._generate_api_endpoints(domain_name, keywords, actions, entities)
        
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
        entities: List[str]
    ) -> List[ApiEndpoint]:
        """Generate RESTful API endpoints based on domain and extracted actions"""
        
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
            
        # Convert to ApiEndpoint objects
        for ep_def in endpoint_defs:
            endpoints.append(ApiEndpoint(
                path=ep_def["path"],
                method=ep_def["method"],
                description=ep_def["desc"]
            ))
            
        return endpoints
        
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
        
    def _build_traceability(
        self,
        text: str,
        services: List[MicroserviceSchema],
        significant_domains: List[Tuple]
    ) -> List[Dict]:
        """
        Build a requirements-traceability matrix.
        For each service, find the top sentences from the document that contain
        its matched domain keywords.  Returns a list ordered by service.
        """
        import re as _re

        # Split document into clean sentences
        raw_sentences = _re.split(r'(?<=[.!?])\s+', text.strip())
        sentences = [s.strip() for s in raw_sentences if len(s.strip()) > 20]

        matrix = []
        for service, (domain_name, confidence, matched_keywords) in zip(services, significant_domains):
            relevant = []
            seen = set()
            for sentence in sentences:
                sentence_lower = sentence.lower()
                # Collect sentences that contain at least one matched keyword
                if any(kw in sentence_lower for kw in matched_keywords):
                    # Truncate very long sentences for display
                    display = sentence if len(sentence) <= 160 else sentence[:157] + "..."
                    if display not in seen:
                        seen.add(display)
                        relevant.append(display)
                if len(relevant) >= 3:  # cap at 3 sentences per service
                    break

            matrix.append({
                "service_id": service.id,
                "service_name": service.name,
                "domain": domain_name,
                "confidence": round(confidence, 1),
                "matched_keywords": matched_keywords[:6],  # top 6 keywords
                "requirement_sentences": relevant
            })

        return matrix

    def _calculate_metrics(
        self, 
        services: List[MicroserviceSchema], 
        dependencies: List[DependencyInfo],
        text: str
    ) -> MetricScores:
        """
        Calculate architecture quality metrics from structural properties.

        All scores are 0-100.  For Coupling, lower = better design.
        For Scalability, Maintainability, and Fault Isolation, higher = better.
        """
        n_services = len(services)
        n_deps = len(dependencies)

        if n_services == 0:
            return MetricScores(scalability=0, coupling=100, maintainability=0, fault_isolation=0)

        avg_deps = n_deps / n_services

        # ── Coupling ─────────────────────────────────────────────────────────
        # avg deps/service → score bands (lower score = looser coupling = better)
        #   0      deps/svc  → 35  suspicious: real systems always have some integration
        #   0-1    deps/svc  → 20-35  very loose (good for isolated services)
        #   1-3    deps/svc  → 35-55  healthy coupling range for microservices
        #   3-5    deps/svc  → 55-75  moderate, manageable
        #   5+     deps/svc  → 75-95  high coupling, deployment risk
        if avg_deps == 0:
            coupling_score = 35
        elif avg_deps <= 1:
            coupling_score = int(20 + avg_deps * 15)          # 20 → 35
        elif avg_deps <= 3:
            coupling_score = int(35 + (avg_deps - 1) * 10)   # 35 → 55
        elif avg_deps <= 5:
            coupling_score = int(55 + (avg_deps - 3) * 10)   # 55 → 75
        else:
            coupling_score = min(95, int(75 + (avg_deps - 5) * 4))  # 75 → 95

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
