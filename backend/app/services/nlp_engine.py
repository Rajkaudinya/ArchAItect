"""
Advanced NLP Engine for Microservice Boundary Detection
Uses open-source transformers, spaCy, and semantic similarity
"""
import os
import re
import numpy as np
from typing import List, Dict, Any, Tuple, Set, Optional
from collections import defaultdict, Counter
import warnings
warnings.filterwarnings('ignore')

class NLPEngine:
    def __init__(self):
        self.initialized = False
        self.nlp = None
        self.embedder = None
        self.domain_keywords = self._load_domain_patterns()
        
    def _load_domain_patterns(self) -> Dict[str, List[str]]:
        """
        Define 6 core domain-specific bounded contexts for microservice identification.
        Based on Domain-Driven Design principles and industry best practices.
        Optimized for 5-6 service generation instead of synthetic 12+ services.
        """
        return {
            # Domain 1: Identity & Access Management
            "Identity & Access": [
                "auth", "login", "register", "signup", "user", "password", "jwt", "token",
                "session", "oauth", "sso", "identity", "credential", "permission", "role",
                "access control", "authorization", "authentication", "user profile", "account",
                "user settings", "preferences", "user data", "user registration", "user account",
                "profile management", "customer profile", "user identity", "rbac"
            ],
            
            # Domain 2: Business Core (Transactions & Catalog)
            "Business Core": [
                "order", "cart", "checkout", "purchase", "buy", "shopping", "basket",
                "order processing", "fulfillment", "order status", "order tracking",
                "order history", "order lifecycle", "payment", "pay", "invoice", "billing",
                "charge", "refund", "transaction", "stripe", "paypal", "credit card", "pricing",
                "subscription", "payment gateway", "payment processing", "financial transaction",
                "inventory", "stock", "warehouse", "product", "catalog", "item", "sku",
                "product catalog", "product list", "stock level", "inventory management",
                "supplier", "product details", "price", "discount", "cart management"
            ],
            
            # Domain 3: Logistics & Fulfillment
            "Logistics & Fulfillment": [
                "shipping", "delivery", "logistics", "tracking", "carrier", "address",
                "shipment", "delivery status", "shipping address", "courier", "warehouse",
                "fulfillment center", "dispatch", "route", "transit", "package", "delivery tracking",
                "shipping label", "shipping cost", "delivery time", "tracking number", "fulfillment"
            ],
            
            # Domain 4: Notification & Events
            "Notification & Events": [
                "notification", "notify", "email", "sms", "alert", "message", "push",
                "send email", "send message", "communication", "reminder", "template",
                "notification service", "messaging", "event", "webhook", "broadcast",
                "message queue", "event bus", "publish", "subscribe", "push notification",
                "email template", "sms gateway", "communication channel"
            ],
            
            # Domain 5: Data & Analytics
            "Data & Analytics": [
                "analytics", "report", "dashboard", "metrics", "kpi", "insights", "statistics",
                "monitoring", "tracking", "analysis", "data visualization", "business intelligence",
                "reporting", "data warehouse", "etl", "data pipeline", "telemetry", "logs",
                "audit", "metrics collection", "real-time analytics", "batch processing"
            ],
            
            # Domain 6: Support & Engagement
            "Support & Engagement": [
                "support", "ticket", "help", "chat", "feedback", "complaint", "issue",
                "customer service", "support ticket", "help desk", "review", "rating",
                "comment", "testimonial", "rate product", "product review", "user review",
                "rating system", "search", "filter", "query", "browse", "discover", "find",
                "recommendation", "search engine", "indexing", "elasticsearch", "content",
                "cms", "document", "media", "upload", "file", "asset", "content management",
                "digital asset", "file storage", "faq", "knowledge base"
            ]
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
                print("[OK] spaCy model 'en_core_web_sm' loaded successfully")
            except OSError:
                # Download if not available - use subprocess for better error handling
                print("[INFO] Downloading spaCy model 'en_core_web_sm'...")
                try:
                    subprocess.check_call(
                        [sys.executable, "-m", "spacy", "download", "en_core_web_sm"],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE
                    )
                    self.nlp = spacy.load("en_core_web_sm")
                    print("[OK] spaCy model downloaded and loaded successfully")
                except Exception as download_error:
                    print(f"[WARNING] Failed to download spaCy model: {download_error}")
                    print("[INFO] Please run manually: python -m spacy download en_core_web_sm")
                    raise
                
            # Initialize sentence transformer for semantic similarity
            from sentence_transformers import SentenceTransformer
            print("[INFO] Loading sentence transformer model...")
            self.embedder = SentenceTransformer('all-MiniLM-L6-v2')
            
            self.initialized = True
            print("[OK] NLP Engine initialized successfully")
        except Exception as e:
            print(f"[WARNING] NLP initialization failed: {e}. Using fallback heuristics.")
            print("[INFO] The system will still work with reduced accuracy using rule-based methods.")
            self.initialized = False
            
    def extract_entities_and_actions(self, text: str) -> Dict[str, List[str]]:
        """Extract entities, actions, and key concepts from text"""
        if not self.initialized or self.nlp is None:
            return self._fallback_extraction(text)
            
        doc = self.nlp(text.lower())
        
        entities = []
        actions = []
        concepts = []
        
        # Extract named entities
        for ent in doc.ents:
            if ent.label_ in ['ORG', 'PRODUCT', 'GPE', 'PERSON', 'WORK_OF_ART']:
                entities.append(ent.text)
                
        # Extract verbs (actions) and nouns (concepts)
        for token in doc:
            if token.pos_ == 'VERB' and not token.is_stop:
                actions.append(token.lemma_)
            elif token.pos_ == 'NOUN' and not token.is_stop:
                concepts.append(token.lemma_)
                
        # Extract compound nouns (multi-word concepts)
        for chunk in doc.noun_chunks:
            if len(chunk.text.split()) > 1:
                concepts.append(chunk.text)
                
        return {
            "entities": list(set(entities)),
            "actions": list(set(actions)),
            "concepts": list(set(concepts))
        }
        
    def _fallback_extraction(self, text: str) -> Dict[str, List[str]]:
        """Simple keyword extraction without NLP models"""
        words = re.findall(r'\b\w+\b', text.lower())
        
        # Common action verbs
        action_verbs = ['create', 'read', 'update', 'delete', 'send', 'receive', 'process',
                       'manage', 'handle', 'store', 'retrieve', 'validate', 'authenticate']
        
        actions = [w for w in words if w in action_verbs]
        concepts = [w for w in words if len(w) > 4 and w not in action_verbs]
        
        return {
            "entities": [],
            "actions": list(set(actions)),
            "concepts": list(set(concepts[:50]))  # Limit to top 50
        }
        
    def identify_service_domains(self, text: str, sections: Optional[Dict[str, str]] = None) -> List[Tuple[str, float, List[str]]]:
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
