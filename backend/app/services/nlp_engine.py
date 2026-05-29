"""
Advanced NLP Engine for Microservice Boundary Detection
Uses open-source transformers, spaCy, and semantic similarity
"""
import os
import re
import numpy as np
from typing import List, Dict, Any, Tuple, Set
from collections import defaultdict, Counter
import warnings
warnings.filterwarnings('ignore')

class NLPEngine:
    def __init__(self):
        self.initialized = False
        self.nlp = None
        self.embedder = None
        self.domain_keywords = self._load_domain_patterns()
        self.ddd_rules = self._load_ddd_rules()
        
    def _load_domain_patterns(self) -> Dict[str, List[str]]:
        """Define comprehensive domain-specific keywords for microservice identification"""
        return {
            "Authentication & Identity": [
                "auth", "login", "register", "signup", "user", "password", "jwt", "token",
                "session", "oauth", "sso", "identity", "credential", "permission", "role",
                "access control", "authorization", "authentication"
            ],
            "Order Management": [
                "order", "cart", "checkout", "purchase", "buy", "shopping", "basket",
                "order processing", "fulfillment", "order status", "order tracking",
                "order history", "order lifecycle"
            ],
            "Payment & Billing": [
                "payment", "pay", "invoice", "billing", "charge", "refund", "transaction",
                "stripe", "paypal", "credit card", "pricing", "subscription", "checkout payment",
                "payment gateway", "payment processing", "financial transaction"
            ],
            "Notification & Communication": [
                "notification", "notify", "email", "sms", "alert", "message", "push",
                "send email", "send message", "communication", "reminder", "template",
                "notification service", "messaging"
            ],
            "Inventory & Catalog": [
                "inventory", "stock", "warehouse", "product", "catalog", "item", "sku",
                "product catalog", "product list", "stock level", "inventory management",
                "supplier", "product details"
            ],
            "User Management": [
                "user profile", "account", "user settings", "preferences", "user data",
                "user registration", "user account", "profile management", "customer"
            ],
            "Analytics & Reporting": [
                "analytics", "report", "dashboard", "metrics", "kpi", "insights", "statistics",
                "monitoring", "tracking", "analysis", "data visualization", "business intelligence"
            ],
            "Search & Discovery": [
                "search", "filter", "query", "browse", "discover", "find", "recommendation",
                "search engine", "indexing", "elasticsearch"
            ],
            "Content Management": [
                "content", "cms", "document", "media", "upload", "file", "asset",
                "content management", "digital asset", "file storage"
            ],
            "Shipping & Logistics": [
                "shipping", "delivery", "logistics", "tracking", "carrier", "address",
                "shipment", "delivery status", "shipping address", "courier"
            ],
            "Customer Support": [
                "support", "ticket", "help", "chat", "feedback", "complaint", "issue",
                "customer service", "support ticket", "help desk"
            ],
            "Product Reviews": [
                "review", "rating", "comment", "feedback", "testimonial", "rate product",
                "product review", "user review", "rating system"
            ]
        }

    def _load_ddd_rules(self) -> Dict[str, Dict[str, Any]]:
        """
        DDD boundary rules per domain.  Three gates — at least one must fire
        with concrete evidence for the domain to become a service boundary.

        owned_data          – data entities exclusively owned by this bounded context
        failure_keywords    – phrases signalling this context can fail independently
        external_systems    – third-party integrations that impose their own SLAs
        can_fail_independently – structural: this context has external failure modes
        primary_actors      – who initiates work in this context
        """
        return {
            "Authentication & Identity": {
                "owned_data": ["credential", "password", "token", "jwt", "session", "role", "permission"],
                "failure_keywords": ["invalid credentials", "token expired", "unauthorized", "auth failed"],
                "external_systems": ["oauth", "sso", "ldap", "saml", "active directory"],
                "can_fail_independently": True,
                "primary_actors": ["user", "admin"],
            },
            "Order Management": {
                "owned_data": ["order", "cart", "basket", "checkout", "fulfillment"],
                "failure_keywords": ["order failed", "checkout error", "order cancelled"],
                "external_systems": [],
                "can_fail_independently": False,
                "primary_actors": ["customer", "buyer", "user"],
            },
            "Payment & Billing": {
                "owned_data": ["payment", "transaction", "invoice", "charge", "refund", "billing"],
                "failure_keywords": ["payment failed", "declined", "payment error", "charge failed"],
                "external_systems": ["stripe", "paypal", "payment gateway", "credit card", "bank"],
                "can_fail_independently": True,
                "primary_actors": ["customer"],
            },
            "Notification & Communication": {
                "owned_data": ["notification", "message", "template", "email", "sms", "alert"],
                "failure_keywords": ["delivery failed", "bounce", "undeliverable", "notification failed"],
                "external_systems": ["smtp", "sendgrid", "twilio", "ses", "push notification"],
                "can_fail_independently": True,
                "primary_actors": ["system"],
            },
            "Inventory & Catalog": {
                "owned_data": ["inventory", "stock", "product", "catalog", "sku", "warehouse"],
                "failure_keywords": ["out of stock", "stock unavailable", "inventory error"],
                "external_systems": [],
                "can_fail_independently": False,
                "primary_actors": ["admin", "customer"],
            },
            "User Management": {
                "owned_data": ["user profile", "account", "preferences", "user data"],
                "failure_keywords": ["profile update failed", "account error"],
                "external_systems": [],
                "can_fail_independently": False,
                "primary_actors": ["user", "customer"],
            },
            "Analytics & Reporting": {
                "owned_data": ["metrics", "report", "dashboard", "analytics", "event log"],
                "failure_keywords": ["report failed", "analytics unavailable"],
                "external_systems": ["bigquery", "elasticsearch", "clickhouse", "redshift", "kafka"],
                "can_fail_independently": True,
                "primary_actors": ["admin", "manager"],
            },
            "Search & Discovery": {
                "owned_data": ["search index", "query", "search result", "relevance"],
                "failure_keywords": ["search unavailable", "index error"],
                "external_systems": ["elasticsearch", "solr", "algolia", "opensearch"],
                "can_fail_independently": True,
                "primary_actors": ["customer", "user"],
            },
            "Content Management": {
                "owned_data": ["content", "media", "document", "asset", "file"],
                "failure_keywords": ["upload failed", "content error", "storage unavailable"],
                "external_systems": ["s3", "cdn", "cloudfront", "azure blob"],
                "can_fail_independently": True,
                "primary_actors": ["admin", "content manager"],
            },
            "Shipping & Logistics": {
                "owned_data": ["shipment", "delivery", "tracking", "carrier", "address"],
                "failure_keywords": ["shipping failed", "carrier error", "address invalid", "delivery failed"],
                "external_systems": ["fedex", "ups", "dhl", "usps", "carrier api"],
                "can_fail_independently": True,
                "primary_actors": ["system", "customer"],
            },
            "Customer Support": {
                "owned_data": ["ticket", "support case", "complaint", "chat session"],
                "failure_keywords": ["ticket creation failed", "support unavailable"],
                "external_systems": ["zendesk", "intercom", "freshdesk", "salesforce"],
                "can_fail_independently": True,
                "primary_actors": ["support agent", "customer"],
            },
            "Product Reviews": {
                "owned_data": ["review", "rating", "comment", "testimonial"],
                "failure_keywords": ["review submission failed", "moderation error"],
                "external_systems": [],
                "can_fail_independently": True,
                "primary_actors": ["customer", "buyer"],
            },
        }

    def initialize(self):
        """Lazy initialization of NLP models"""
        if self.initialized:
            return
            
        try:
            # Initialize spaCy for entity recognition and linguistic processing
            import spacy
            import subprocess
            import sys
            
            try:
                self.nlp = spacy.load("en_core_web_sm")
                print("✅ spaCy model 'en_core_web_sm' loaded successfully")
            except OSError:
                # Download if not available - use subprocess for better error handling
                print("📥 Downloading spaCy model 'en_core_web_sm'...")
                try:
                    subprocess.check_call(
                        [sys.executable, "-m", "spacy", "download", "en_core_web_sm"],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE
                    )
                    self.nlp = spacy.load("en_core_web_sm")
                    print("✅ spaCy model downloaded and loaded successfully")
                except Exception as download_error:
                    print(f"⚠️ Failed to download spaCy model: {download_error}")
                    print("💡 Please run manually: python -m spacy download en_core_web_sm")
                    raise
                
            # Initialize sentence transformer for semantic similarity
            from sentence_transformers import SentenceTransformer
            print("📥 Loading sentence transformer model...")
            self.embedder = SentenceTransformer('all-MiniLM-L6-v2')
            
            self.initialized = True
            print("✅ NLP Engine initialized successfully")
        except Exception as e:
            print(f"⚠️ NLP initialization failed: {e}. Using fallback heuristics.")
            print("💡 The system will still work with reduced accuracy using rule-based methods.")
            self.initialized = False
            
    def extract_entities_and_actions(self, text: str) -> Dict[str, List[Any]]:
        """Extract entities, actions, and key concepts with line-level provenance."""
        self.initialize()
        if not self.initialized:
            return self._fallback_extraction(text)

        lines = text.split('\n')
        char_to_line = self._build_char_to_line(text)

        doc = self.nlp(text)  # original case — better for NER

        entities: List[Dict] = []
        actions: List[Dict] = []
        concepts: List[Dict] = []
        seen_e: Set[str] = set()
        seen_a: Set[str] = set()
        seen_c: Set[str] = set()

        def _prov(char_idx: int) -> Tuple[int, str]:
            ln = char_to_line[min(char_idx, len(char_to_line) - 1)]
            sentence = lines[ln - 1].strip() if ln <= len(lines) else ""
            return ln, sentence

        for ent in doc.ents:
            if ent.label_ in ('ORG', 'PRODUCT', 'GPE', 'PERSON', 'WORK_OF_ART'):
                val = ent.text.lower()
                if val not in seen_e:
                    seen_e.add(val)
                    ln, sent = _prov(ent.start_char)
                    entities.append({"value": val, "line": ln, "sentence": sent})

        for token in doc:
            if token.pos_ == 'VERB' and not token.is_stop:
                val = token.lemma_.lower()
                if val not in seen_a:
                    seen_a.add(val)
                    ln, sent = _prov(token.idx)
                    actions.append({"value": val, "line": ln, "sentence": sent})
            elif token.pos_ == 'NOUN' and not token.is_stop:
                val = token.lemma_.lower()
                if val not in seen_c:
                    seen_c.add(val)
                    ln, sent = _prov(token.idx)
                    concepts.append({"value": val, "line": ln, "sentence": sent})

        for chunk in doc.noun_chunks:
            if len(chunk.text.split()) > 1:
                val = chunk.text.lower()
                if val not in seen_c:
                    seen_c.add(val)
                    ln, sent = _prov(chunk.start_char)
                    concepts.append({"value": val, "line": ln, "sentence": sent})

        return {"entities": entities, "actions": actions, "concepts": concepts}

    def _fallback_extraction(self, text: str) -> Dict[str, List[Any]]:
        """Simple keyword extraction without NLP models, with line provenance."""
        action_verbs = {'create', 'read', 'update', 'delete', 'send', 'receive', 'process',
                        'manage', 'handle', 'store', 'retrieve', 'validate', 'authenticate'}
        seen_a: Set[str] = set()
        seen_c: Set[str] = set()
        actions: List[Dict] = []
        concepts: List[Dict] = []

        for line_num, line in enumerate(text.split('\n'), 1):
            line_strip = line.strip()
            if not line_strip:
                continue
            for word in re.findall(r'\b\w+\b', line_strip.lower()):
                if word in action_verbs and word not in seen_a:
                    seen_a.add(word)
                    actions.append({"value": word, "line": line_num, "sentence": line_strip})
                elif len(word) > 4 and word not in action_verbs and word not in seen_c:
                    seen_c.add(word)
                    concepts.append({"value": word, "line": line_num, "sentence": line_strip})

        return {"entities": [], "actions": actions, "concepts": concepts[:50]}
        
    def identify_service_domains(self, text: str, sections: Dict[str, str] = None) -> List[Tuple[str, float, List[str]]]:
        """
        Identify potential microservice domains using semantic analysis
        Returns: List of (domain_name, confidence_score, matched_keywords)
        """
        self.initialize()
        
        text_lower = text.lower()
        detected_domains = []
        
        # Analyze each domain
        for domain_name, keywords in self.domain_keywords.items():
            matches = []
            score = 0.0
            
            # Count keyword matches
            for keyword in keywords:
                if keyword in text_lower:
                    matches.append(keyword)
                    # Weight longer phrases higher
                    score += len(keyword.split()) * 2
                    
            if matches or self._is_semantically_related(text, keywords):
                # Boost score if mentioned in multiple sections
                if sections:
                    section_mentions = sum(1 for section_text in sections.values() 
                                         if any(kw in section_text.lower() for kw in keywords))
                    score += section_mentions * 3
                    
                # Normalize score to 0-100 range
                confidence = min(100, score * 2)
                
                if confidence > 10:  # Threshold for inclusion
                    detected_domains.append((domain_name, confidence, matches))
                    
        # Sort by confidence
        detected_domains.sort(key=lambda x: x[1], reverse=True)
        
        return detected_domains
        
    def _is_semantically_related(self, text: str, keywords: List[str]) -> bool:
        """Check semantic similarity using embeddings"""
        if not self.initialized or not self.embedder:
            return False
            
        try:
            # Sample first 500 chars for efficiency
            text_sample = text[:500]
            keyword_phrase = " ".join(keywords[:10])
            
            embeddings = self.embedder.encode([text_sample, keyword_phrase])
            similarity = np.dot(embeddings[0], embeddings[1]) / (
                np.linalg.norm(embeddings[0]) * np.linalg.norm(embeddings[1])
            )
            
            return similarity > 0.3
        except:
            return False
            
    def extract_dependencies(self, services: List[Dict], text: str) -> List[Dict[str, str]]:
        """
        Extract dependencies between services based on text analysis
        """
        dependencies = []
        service_names = [s['name'].lower() for s in services]
        service_keywords = {s['name']: s.get('keywords', []) for s in services}
        
        # Split text into sentences for co-occurrence analysis
        sentences = re.split(r'[.!?]+', text)
        
        # Track co-occurrences
        co_occurrence = defaultdict(int)
        
        for sentence in sentences:
            sentence_lower = sentence.lower()
            mentioned_services = []
            
            for service in services:
                service_name = service['name']
                keywords = service.get('keywords', [])
                
                # Check if this service is mentioned in the sentence
                if any(kw in sentence_lower for kw in keywords):
                    mentioned_services.append(service_name)
                    
            # Create dependencies for co-occurring services
            for i, service1 in enumerate(mentioned_services):
                for service2 in mentioned_services[i+1:]:
                    pair = tuple(sorted([service1, service2]))
                    co_occurrence[pair] += 1
                    
        # Convert co-occurrences to dependencies
        for (service1, service2), count in co_occurrence.items():
            if count >= 2:  # Threshold: mentioned together at least twice
                # Determine direction and type based on keywords
                dep_type = self._determine_dependency_type(service1, service2, text)
                dependencies.append({
                    "source": service1,
                    "target": service2,
                    "type": dep_type,
                    "confidence": min(100, count * 20)
                })
                
        return dependencies
        
    def _determine_dependency_type(self, service1: str, service2: str, text: str) -> str:
        """Determine if dependency is sync or async based on context"""
        # Keywords indicating async patterns
        async_keywords = ['event', 'queue', 'message', 'notification', 'trigger', 
                         'publish', 'subscribe', 'async', 'background']
        
        # Keywords indicating sync patterns
        sync_keywords = ['call', 'request', 'api', 'validate', 'check', 'sync',
                        'immediately', 'before', 'during']
        
        text_lower = text.lower()
        
        # Count occurrences
        async_score = sum(1 for kw in async_keywords if kw in text_lower)
        sync_score = sum(1 for kw in sync_keywords if kw in text_lower)
        
        return "async" if async_score > sync_score else "sync"
        
    def calculate_cohesion_score(self, service_keywords: List[str], all_text: str) -> float:
        """Calculate how cohesive a service is (0-100)"""
        if not service_keywords:
            return 50.0
            
        # Higher cohesion = keywords appear together frequently
        text_lower = all_text.lower()
        
        # Count co-occurrences in same sentences
        sentences = re.split(r'[.!?]+', text_lower)
        co_occurrence_count = 0
        
        for sentence in sentences:
            mentions = sum(1 for kw in service_keywords if kw in sentence)
            if mentions >= 2:
                co_occurrence_count += mentions
                
        # Normalize: ratio of co-occurring mentions vs theoretical max, scaled to 0-100
        # Use a gentle multiplier (10) so mid-density docs score in the 20-70 range
        max_possible = len(service_keywords) * len(sentences)
        raw_ratio = co_occurrence_count / max_possible if max_possible > 0 else 0
        cohesion = round(min(100.0, max(0.0, raw_ratio * 10 * 100)), 2)
        
        return cohesion
        
    def suggest_database_type(self, domain_name: str, keywords: List[str]) -> Tuple[str, str]:
        """Suggest appropriate database type based on domain characteristics"""
        
        # SQL indicators
        sql_indicators = ['transaction', 'order', 'payment', 'billing', 'invoice', 
                         'financial', 'accounting', 'relational']
        
        # NoSQL indicators
        nosql_indicators = ['catalog', 'product', 'content', 'media', 'profile',
                           'document', 'flexible', 'schema-less']
        
        # Cache indicators
        cache_indicators = ['session', 'notification', 'temporary', 'queue',
                          'fast', 'real-time']
        
        # Time-series indicators
        timeseries_indicators = ['analytics', 'metrics', 'log', 'monitoring',
                                'tracking', 'statistics', 'event']
        
        keywords_lower = [k.lower() for k in keywords]
        text = " ".join(keywords_lower + [domain_name.lower()])
        
        # Score each type
        sql_score = sum(2 for ind in sql_indicators if ind in text)
        nosql_score = sum(2 for ind in nosql_indicators if ind in text)
        cache_score = sum(2 for ind in cache_indicators if ind in text)
        timeseries_score = sum(2 for ind in timeseries_indicators if ind in text)
        
        scores = {
            "PostgreSQL": (sql_score, "ACID compliance ensures transaction integrity and strong consistency for critical business operations."),
            "MongoDB": (nosql_score, "Flexible document structure accommodates dynamic schemas and rapid iteration."),
            "Redis": (cache_score, "Ultra-fast in-memory storage perfect for transient data and high-throughput operations."),
            "Elasticsearch": (timeseries_score, "Optimized for time-series data, full-text search, and analytical aggregations.")
        }
        
        # Select database with highest score
        db_type, (score, reason) = max(scores.items(), key=lambda x: x[1][0])
        
        # Default to PostgreSQL if no clear winner
        if score == 0:
            return "PostgreSQL", "General-purpose relational database suitable for structured data and complex queries."

        return db_type, reason

    # ── Provenance helpers ────────────────────────────────────────────────────

    def _build_char_to_line(self, text: str) -> List[int]:
        """Map each character position to its 1-indexed line number."""
        mapping: List[int] = []
        ln = 1
        for ch in text:
            mapping.append(ln)
            if ch == '\n':
                ln += 1
        return mapping

    def extract_fr_ids(self, text: str) -> Dict[str, List[Dict[str, Any]]]:
        """Scan for FR-[A-Z]+-\\d+ requirement IDs and map them to source lines."""
        pattern = re.compile(r'\bFR-[A-Z]+-\d+\b')
        result: Dict[str, List[Dict]] = {}
        for line_num, line in enumerate(text.split('\n'), 1):
            line_strip = line.strip()
            for m in pattern.finditer(line_strip):
                fr_id = m.group()
                result.setdefault(fr_id, []).append({
                    "sentence": line_strip,
                    "line": line_num,
                })
        return result

    # Known role vocabulary — covers formal + informal requirement styles
    _KNOWN_ROLES: List[str] = [
        "user", "admin", "administrator", "customer", "system", "manager",
        "operator", "client", "guest", "member", "buyer", "seller", "driver",
        "rider", "employee", "staff", "merchant", "vendor", "supplier",
        "agent", "support agent", "support", "owner", "moderator", "viewer",
        "approver", "reviewer", "auditor", "finance", "hr", "dispatcher",
    ]

    def extract_actors(self, text: str) -> List[Dict[str, Any]]:
        """
        Detect actors and their capabilities using multiple pattern strategies:

        Strategy 1 – spaCy modal-verb dependency parse (when models loaded)
        Strategy 2 – "As a <role>, I/the user can/shall <verb>" user-story pattern
        Strategy 3 – "<Role> can/shall/must/may/will/should/needs to <verb>" pattern
        Strategy 4 – "<Role>: <verb>" or "<Role> – <verb>" definition lines
        Strategy 5 – Header-anchored role sections (## Admin / ### Customer)
        Strategy 6 – "<Role> is responsible for <verb>" / "<Role> manages <noun>"
        Strategy 7 – Known-role scan: any sentence containing a known role word
                     paired with an action verb in the same clause.

        Returns [{actor, capabilities: [str], sentences: [{sentence, line}]}]
        """
        self.initialize()
        MODALS = {'shall', 'can', 'must', 'may', 'will', 'should'}
        ACTION_VERBS = {
            'login', 'register', 'signup', 'place', 'create', 'submit', 'view',
            'browse', 'search', 'filter', 'add', 'remove', 'update', 'edit',
            'delete', 'cancel', 'track', 'pay', 'checkout', 'upload', 'download',
            'approve', 'reject', 'manage', 'configure', 'monitor', 'review',
            'rate', 'comment', 'notify', 'send', 'receive', 'process', 'handle',
            'assign', 'schedule', 'generate', 'export', 'import', 'integrate',
            'authenticate', 'authorize', 'verify', 'validate', 'fulfil', 'fulfill',
            'ship', 'deliver', 'refund', 'charge', 'subscribe', 'recommend',
            'access', 'reset', 'change', 'set', 'get', 'list', 'fetch', 'show',
        }

        actors: Dict[str, Dict] = {}
        lines = text.split('\n')
        roles_pattern = '|'.join(re.escape(r) for r in sorted(self._KNOWN_ROLES, key=len, reverse=True))

        def record(actor: str, capability: str, line_num: int, sentence: str) -> None:
            actor = actor.strip().lower()
            if not actor or len(actor) <= 1 or actor in {'a', 'an', 'the', 'i', 'it'}:
                return
            # Normalise plural / possessive
            actor = re.sub(r"'s$", '', actor)
            if actor not in actors:
                actors[actor] = {"capabilities": [], "sentences": []}
            cap = capability.strip() if capability else ""
            if cap and cap not in actors[actor]["capabilities"]:
                actors[actor]["capabilities"].append(cap)
            entry = {"sentence": sentence, "line": line_num}
            if entry not in actors[actor]["sentences"]:
                actors[actor]["sentences"].append(entry)

        # ── Strategy 1: spaCy dependency parse (when spaCy model is available) ─
        # Use self.nlp directly — it is set even when sentence_transformers fails
        if self.nlp:
            char_to_line = self._build_char_to_line(text)
            doc = self.nlp(text)
            for token in doc:
                if token.pos_ != 'VERB':
                    continue
                if not any(c.lower_ in MODALS and c.dep_ == 'aux' for c in token.children):
                    continue
                subj = next((c for c in token.children if c.dep_ in ('nsubj', 'nsubjpass')), None)
                if subj is None:
                    continue
                obj_tok = next((c for c in token.children if c.dep_ in ('dobj', 'attr', 'pobj')), None)
                capability = f"{token.lemma_} {obj_tok.lemma_}" if obj_tok else token.lemma_
                ln = char_to_line[min(token.idx, len(char_to_line) - 1)]
                record(subj.lemma_.lower(), capability, ln,
                       lines[ln - 1].strip() if ln <= len(lines) else "")

        # ── Strategy 2: "As a <role>[, I/user] [shall|can|want to] <action>" ─
        as_a_re = re.compile(
            rf'[Aa]s\s+an?\s+(?P<role>{roles_pattern})'
            r'(?:[,.]?\s*(?:I|the\s+\w+)?\s*'
            r'(?:want\s+to|need\s+to|shall|can|must|should|will|am\s+able\s+to)?'
            r'\s*(?P<action>[a-zA-Z][a-zA-Z ]{1,30}))?',
        )

        # ── Strategy 3: "<Role> can/shall/must ... <action>" ─────────────────
        modal_re = re.compile(
            rf'(?P<role>{roles_pattern})\s+'
            r'(?:shall|can|must|may|will|should|needs?\s+to|is\s+able\s+to|is\s+allowed\s+to|has\s+to)\s+'
            r'(?P<action>[a-zA-Z][a-zA-Z ]{1,30})',
            re.IGNORECASE,
        )

        # ── Strategy 4: "<Role>: <action>" or "<Role> — <action>" definition lines
        defn_re = re.compile(
            rf'(?:^|\n)\s*(?P<role>{roles_pattern})\s*[:–\-]\s*(?P<action>[A-Za-z][^.\n]{{0,60}})',
            re.IGNORECASE | re.MULTILINE,
        )

        # ── Strategy 5: Markdown header "## Customer" / "### Admin" ─────────
        header_re = re.compile(
            rf'^#+\s*(?P<role>{roles_pattern})',
            re.IGNORECASE | re.MULTILINE,
        )

        # ── Strategy 6: "<Role> manages/handles/is responsible for <action>" ─
        resp_re = re.compile(
            rf'(?P<role>{roles_pattern})\s+'
            r'(?:is\s+responsible\s+for|manages?|handles?|oversees?|controls?|maintains?)\s+'
            r'(?P<action>[a-zA-Z][a-zA-Z ]{1,30})',
            re.IGNORECASE,
        )

        for line_num, line in enumerate(lines, 1):
            sentence = line.strip()
            if not sentence:
                continue

            for m in as_a_re.finditer(sentence):
                action = m.group('action') or ''
                record(m.group('role'), action.strip(), line_num, sentence)

            for m in modal_re.finditer(sentence):
                record(m.group('role'), m.group('action').strip(), line_num, sentence)

            for m in defn_re.finditer(sentence):
                record(m.group('role'), m.group('action').strip(), line_num, sentence)

            for m in header_re.finditer(sentence):
                record(m.group('role'), '', line_num, sentence)

            for m in resp_re.finditer(sentence):
                record(m.group('role'), m.group('action').strip(), line_num, sentence)

        # ── Strategy 7: Known-role scan — any sentence with a role + action verb ──
        verbs_alt = '|'.join(sorted(ACTION_VERBS, key=len, reverse=True))
        verb_re = re.compile(
            rf'(?P<role>{roles_pattern})[^.!?\n]{{0,60}}(?P<action>{verbs_alt})(?:\s+\w+){{0,3}}',
            re.IGNORECASE,
        )
        for line_num, line in enumerate(lines, 1):
            sentence = line.strip()
            if not sentence:
                continue
            for m in verb_re.finditer(sentence):
                role = m.group('role').lower()
                action = m.group('action').lower()
                record(role, action, line_num, sentence)

        result = [{"actor": k, **v} for k, v in actors.items()]
        # Sort by number of capability mentions descending (most prominent actors first)
        result.sort(key=lambda x: len(x["capabilities"]) + len(x["sentences"]), reverse=True)
        return result

    def extract_capabilities(self, text: str) -> List[Dict[str, Any]]:
        """
        Extract business capabilities as verb-object pairs, distinct from bare entities.
        "Process payment" is a capability; "payment" alone is an entity.
        Returns top-50 by frequency: [{capability, count, sentences: [{sentence, line}]}]
        """
        self.initialize()
        CAPABILITY_VERBS: Set[str] = {
            'process', 'manage', 'handle', 'create', 'update', 'delete', 'send',
            'receive', 'validate', 'authenticate', 'authorize', 'track', 'monitor',
            'generate', 'calculate', 'notify', 'schedule', 'assign', 'approve',
            'submit', 'search', 'filter', 'export', 'import', 'integrate',
            'configure', 'view', 'display', 'upload', 'download', 'register',
            'cancel', 'reserve', 'fulfill', 'ship', 'deliver', 'charge', 'refund',
            'subscribe', 'rate', 'review', 'recommend', 'place', 'login',
        }

        caps: Dict[str, Dict] = {}
        lines = text.split('\n')

        def record(cap: str, line_num: int, sentence: str) -> None:
            if cap not in caps:
                caps[cap] = {"count": 0, "sentences": []}
            caps[cap]["count"] += 1
            entry = {"sentence": sentence, "line": line_num}
            if entry not in caps[cap]["sentences"]:
                caps[cap]["sentences"].append(entry)

        if self.initialized and self.nlp:
            char_to_line = self._build_char_to_line(text)
            doc = self.nlp(text)
            for token in doc:
                if token.pos_ != 'VERB' or token.lemma_.lower() not in CAPABILITY_VERBS:
                    continue
                obj_tok = next((c for c in token.children if c.dep_ in ('dobj', 'attr')), None)
                if obj_tok is None:
                    continue
                cap = f"{token.lemma_.capitalize()} {obj_tok.lemma_}"
                ln = char_to_line[min(token.idx, len(char_to_line) - 1)]
                record(cap, ln, lines[ln - 1].strip() if ln <= len(lines) else "")
        else:
            verbs_re = '|'.join(sorted(CAPABILITY_VERBS, key=len, reverse=True))
            pattern = re.compile(
                rf'\b({verbs_re})\s+(?:a |an |the )?(\w+(?:\s+\w+){{0,2}})',
                re.IGNORECASE,
            )
            for line_num, line in enumerate(lines, 1):
                for m in pattern.finditer(line):
                    verb = m.group(1).lower()
                    if verb in CAPABILITY_VERBS:
                        cap = f"{verb.capitalize()} {m.group(2).strip().lower()}"
                        record(cap, line_num, line.strip())

        result = [{"capability": k, **v} for k, v in caps.items()]
        result.sort(key=lambda x: x["count"], reverse=True)
        return result[:50]

    # ── DDD boundary evaluation ───────────────────────────────────────────────

    def evaluate_ddd_boundaries(
        self,
        text: str,
        sections: Dict[str, str] = None,
        detected_actors: List[Dict] = None,
    ) -> List[Tuple[str, float, List[str], str]]:
        """
        Evaluate service boundaries using three DDD rules instead of keyword counting.

        Rule 1 – Data Ownership   : domain owns ≥2 distinct data entities found in text.
        Rule 2 – Transaction Boundary : domain has independent failure modes or external
                                        system integrations present in the document.
        Rule 3 – Actor Grouping   : domain is initiated by a distinct set of actors
                                    (cross-referenced with the actor extraction results).

        A domain becomes a boundary only when at least one rule fires with
        concrete evidence from the document text — not just keyword frequency.

        Returns: [(domain_name, rule_score, matched_keywords, justification)]
        """
        text_lower = text.lower()
        actor_names: Set[str] = {a["actor"] for a in (detected_actors or [])}

        results: List[Tuple[str, float, List[str], str]] = []

        for domain_name, rules in self.ddd_rules.items():
            keywords = self.domain_keywords.get(domain_name, [])

            # Domain must appear in the text at all
            matched_kws = [kw for kw in keywords if kw in text_lower]
            if not matched_kws:
                continue

            # ── Rule 1: Data Ownership ────────────────────────────────────
            owned_found = [d for d in rules["owned_data"] if d in text_lower]
            rule1 = len(owned_found) >= 2

            # ── Rule 2: Transaction Boundary ─────────────────────────────
            failure_hits = sum(1 for f in rules["failure_keywords"] if f in text_lower)
            external_hits = sum(1 for e in rules["external_systems"] if e in text_lower)
            rule2 = (rules["can_fail_independently"] and failure_hits >= 1) or external_hits >= 1

            # ── Rule 3: Actor Grouping ────────────────────────────────────
            domain_actors = [
                a for a in rules["primary_actors"]
                if a in actor_names or a in text_lower
            ]
            rule3 = len(domain_actors) >= 1

            fired: List[str] = []
            if rule1:
                fired.append("data_ownership")
            if rule2:
                fired.append("transaction_boundary")
            if rule3:
                fired.append("actor_grouping")

            if not fired:
                continue  # No DDD rule fired — not a valid boundary

            # Score is evidence-weighted, not keyword-frequency-weighted
            score = float(
                len(owned_found) * 10 * int(rule1)
                + (failure_hits * 8 + external_hits * 12) * int(rule2)
                + len(domain_actors) * 6 * int(rule3)
            )
            score = min(100.0, score)

            justification = self._build_boundary_justification(
                domain_name, fired, owned_found, domain_actors, external_hits > 0
            )
            results.append((domain_name, score, matched_kws, justification))

        results.sort(key=lambda x: x[1], reverse=True)
        return results

    def _build_boundary_justification(
        self,
        domain_name: str,
        fired_rules: List[str],
        owned_data: List[str],
        actors: List[str],
        has_external: bool,
    ) -> str:
        """
        Generate a factual DDD justification from the rules that triggered the split.
        Form: "Split because <domain> <evidence clause> [and <evidence clause>]."
        """
        parts: List[str] = []

        if "data_ownership" in fired_rules:
            data_str = ", ".join(owned_data[:3])
            parts.append(f"owns distinct data ({data_str})")

        if "transaction_boundary" in fired_rules:
            if has_external:
                parts.append(
                    "integrates with external systems that carry their own SLAs and failure modes"
                )
            else:
                parts.append(
                    "can fail or be unavailable without cascading to other bounded contexts"
                )

        if "actor_grouping" in fired_rules:
            actor_str = ", ".join(actors[:2])
            parts.append(f"is primarily initiated by distinct actors ({actor_str})")

        if not parts:
            return ""

        return f"Split because {domain_name} " + " and ".join(parts) + "."

    # ── Action-verb extraction & flow diagram ─────────────────────────────────

    # HTTP verb → method mapping (module-level constant referenced by two methods)
    _VERB_METHOD: Dict[str, str] = {
        "create": "POST", "add": "POST", "register": "POST", "submit": "POST",
        "place": "POST", "upload": "POST", "send": "POST", "post": "POST",
        "get": "GET", "retrieve": "GET", "fetch": "GET", "view": "GET",
        "list": "GET", "search": "GET", "find": "GET", "show": "GET", "browse": "GET",
        "update": "PUT", "modify": "PUT", "edit": "PUT", "change": "PUT", "set": "PUT",
        "delete": "DELETE", "remove": "DELETE", "cancel": "DELETE", "deactivate": "DELETE",
    }

    def extract_domain_action_verbs(
        self, text: str, keywords: List[str]
    ) -> List[Tuple[str, str, int]]:
        """
        Find verb-entity pairs in sentences that contain at least one domain keyword.
        Only verbs that map to HTTP methods are returned, so every result is
        directly actionable as an API endpoint.

        Returns: [(verb_lemma, entity_noun, source_line_number)]
        """
        self.initialize()
        seen: Set[Tuple[str, str]] = set()
        results: List[Tuple[str, str, int]] = []
        lines = text.split("\n")

        if self.initialized and self.nlp:
            for line_num, line in enumerate(lines, 1):
                line_strip = line.strip()
                if not line_strip or not any(kw in line_strip.lower() for kw in keywords):
                    continue
                doc = self.nlp(line_strip)
                for token in doc:
                    verb = token.lemma_.lower()
                    if token.pos_ != "VERB" or verb not in self._VERB_METHOD:
                        continue
                    obj_tok = next(
                        (c for c in token.children if c.dep_ in ("dobj", "attr", "pobj")),
                        None,
                    )
                    entity = obj_tok.lemma_.lower() if obj_tok else keywords[0] if keywords else "resource"
                    key = (verb, entity)
                    if key not in seen:
                        seen.add(key)
                        results.append((verb, entity, line_num))
        else:
            verbs_re = "|".join(self._VERB_METHOD)
            pattern = re.compile(rf"\b({verbs_re})\s+(?:a |an |the )?(\w+)", re.IGNORECASE)
            for line_num, line in enumerate(lines, 1):
                line_strip = line.strip()
                if not line_strip or not any(kw in line_strip.lower() for kw in keywords):
                    continue
                for m in pattern.finditer(line_strip):
                    verb, entity = m.group(1).lower(), m.group(2).lower()
                    if (verb, entity) not in seen:
                        seen.add((verb, entity))
                        results.append((verb, entity, line_num))

        return results

    # Domain → ordered flow steps (used by fallback generator)
    _DOMAIN_FLOW_ORDER: Dict[str, int] = {
        "Authentication & Identity": 10,
        "User Management": 20,
        "Search & Discovery": 30,
        "Inventory & Catalog": 40,
        "Order Management": 50,
        "Payment & Billing": 60,
        "Shipping & Logistics": 70,
        "Notification & Communication": 80,
        "Analytics & Reporting": 90,
        "Customer Support": 95,
        "Content Management": 35,
        "Product Reviews": 85,
    }

    def extract_user_flows(
        self, text: str, actors: List[Dict], capabilities: List[Dict]
    ) -> str:
        """
        Fallback Mermaid flowchart generator (used when LLM is unavailable).
        Produces a DDD-grouped TD diagram ordered by natural business flow
        rather than a flat actor→capability chain.
        """
        def _id(s: str) -> str:
            return re.sub(r"[^a-zA-Z0-9]", "_", s.strip())[:24]

        def _lbl(s: str) -> str:
            return s.strip()[:40].replace('"', "'")

        if not capabilities and not actors:
            return ""

        text_lower = text.lower()
        lines_out: List[str] = ["flowchart TD"]

        # ── Step 1: determine primary actors ─────────────────────────────────
        primary_actors = actors[:4] if actors else [{"actor": "user", "capabilities": []}]
        actor_ids = []
        for a in primary_actors:
            aid = _id(a["actor"])
            lines_out.append(f'    {aid}(["{a["actor"].capitalize()}"])')
            actor_ids.append(aid)

        # ── Step 2: bucket capabilities into domains ──────────────────────────
        domain_caps: Dict[str, List[str]] = {d: [] for d in self._DOMAIN_FLOW_ORDER}

        for cap_info in capabilities[:40]:
            cap = cap_info.get("capability", "")
            if not cap:
                continue
            cap_lower = cap.lower()
            assigned = False
            for domain, kws in self.domain_keywords.items():
                if any(kw in cap_lower for kw in kws):
                    domain_caps.setdefault(domain, []).append(cap)
                    assigned = True
                    break
            if not assigned:
                # Put unclassified caps in the closest matching domain by text scan
                for domain, kws in self.domain_keywords.items():
                    if any(kw in text_lower for kw in kws[:3]):
                        domain_caps.setdefault(domain, []).append(cap)
                        break

        # Only keep domains that appear in the document text
        active_domains = sorted(
            [
                (d, order, caps)
                for d, order in self._DOMAIN_FLOW_ORDER.items()
                for caps in [domain_caps.get(d, [])]
                if any(kw in text_lower for kw in self.domain_keywords.get(d, [])[:4])
            ],
            key=lambda x: x[1],
        )[:8]

        if not active_domains:
            # Nothing matched — produce a simple linear flow from capabilities
            prev = actor_ids[0] if actor_ids else None
            for cap_info in capabilities[:10]:
                cap = cap_info.get("capability", "")
                if not cap:
                    continue
                cid = _id(cap)
                lines_out.append(f'    {cid}["{_lbl(cap)}"]')
                if prev:
                    lines_out.append(f"    {prev} --> {cid}")
                prev = cid
            return "\n".join(lines_out)

        # ── Step 3: emit subgraphs per domain in business-flow order ─────────
        prev_node = actor_ids[0] if actor_ids else None
        subgraph_exit_nodes: List[str] = []

        for domain_name, _, caps in active_domains:
            sg_id = _id(domain_name) + "_sg"
            lines_out.append(f'    subgraph {sg_id}["{domain_name}"]')

            # Pick up to 4 representative steps for this domain
            steps = caps[:4] if caps else [f"{domain_name.split()[0]} step"]
            step_ids: List[str] = []
            for step in steps:
                sid = _id(step)
                # Ensure unique ids within diagram
                while lines_out.count(f"    {sid}[") > 0:
                    sid += "_"
                lines_out.append(f'        {sid}["{_lbl(step)}"]')
                step_ids.append(sid)

            # Chain steps within subgraph
            for i in range(len(step_ids) - 1):
                lines_out.append(f"        {step_ids[i]} --> {step_ids[i+1]}")

            lines_out.append("    end")

            # Connect from previous subgraph exit / actor
            if prev_node and step_ids:
                lines_out.append(f"    {prev_node} --> {step_ids[0]}")

            if step_ids:
                prev_node = step_ids[-1]
                subgraph_exit_nodes.append(step_ids[-1])

        # ── Step 4: add a generic terminal node ─────────────────────────────
        if subgraph_exit_nodes:
            lines_out.append('    END([" Journey Complete "])')
            lines_out.append(f"    {subgraph_exit_nodes[-1]} --> END")

        return "\n".join(lines_out)
