# ArchAItect Improvement Recommendations

## Current Problems Identified

### 1. **Hardcoded Domain Patterns (12 Domains)**
**Problem:**
- 12 predefined domains in `nlp_engine.py::_load_domain_patterns()`
- Hardcoded keywords like `["auth", "login", "jwt"]` for Authentication
- Not flexible for different industries (healthcare, finance, gaming, etc.)
- Always generates too many services (e.g., e-commerce gets 7-12 services)

**Example:**
```python
"Authentication & Identity": ["auth", "login", "jwt", "token", ...],
"Order Management": ["order", "cart", "checkout", ...],
"Payment & Billing": ["payment", "stripe", "invoice", ...],
# ... 9 more domains
```

### 2. **Opaque Metrics Scoring**
**Problem:**
- Users don't understand WHY they got a coupling score of 67
- No visibility into what factors influenced the score
- Metrics feel like "black box" magic numbers
- Can't explain to stakeholders: "Why is my architecture scored 58/100?"

### 3. **Synthetic/Demo Feel**
**Problem:**
- E-commerce example always generates similar results
- Feels like template output rather than real analysis
- Doesn't adapt to unique business domains

---

## Proposed Solutions

### Solution 1: Reduce to 5-6 Core Bounded Contexts

**Rationale:** DDD (Domain-Driven Design) recommends 5-10 services for most systems. Smaller is better.

**Proposed Core Domains (Universal):**
```python
CORE_DOMAINS = {
    "Identity & Access": {
        "triggers": ["auth", "login", "user", "permission", "role", "session"],
        "why": "Almost every system needs authentication/authorization",
        "database": "PostgreSQL (ACID for user credentials)",
    },
    
    "Business Logic Core": {
        "triggers": ["order", "transaction", "booking", "request", "workflow", "process"],
        "why": "Central domain-specific business operations",
        "database": "PostgreSQL (transactional integrity)",
    },
    
    "Payment & Finance": {
        "triggers": ["payment", "billing", "invoice", "charge", "refund", "pricing"],
        "why": "Financial transactions require isolation",
        "database": "PostgreSQL (ledger consistency)",
    },
    
    "Notification & Events": {
        "triggers": ["notify", "email", "sms", "alert", "message", "event"],
        "why": "Async communication hub",
        "database": "Redis (fast queue)",
    },
    
    "Data & Analytics": {
        "triggers": ["report", "analytics", "dashboard", "metrics", "search", "query"],
        "why": "Read-heavy operations, reporting",
        "database": "Elasticsearch/ClickHouse (analytical queries)",
    },
    
    # Optional 6th (only if strong signals):
    "Content & Media": {
        "triggers": ["upload", "file", "document", "media", "asset", "storage"],
        "why": "Large object storage and CDN delivery",
        "database": "S3 + DynamoDB (blob metadata)",
    }
}
```

**Benefits:**
- Fewer services → easier to maintain
- Aligns with DDD bounded context principles
- Still covers 90% of systems

---

### Solution 2: Dynamic Keyword Extraction (Not Hardcoded)

**Approach A: TF-IDF + Clustering**
```python
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import AgglomerativeClustering

def extract_dynamic_domains(text: str, target_clusters: int = 5):
    """
    Extract domains dynamically without predefined keywords.
    
    Steps:
    1. Split text into paragraphs/sections
    2. Extract top keywords per section using TF-IDF
    3. Cluster semantically similar sections
    4. Name clusters based on dominant verbs + nouns
    5. Generate service per cluster
    """
    # Split into logical sections
    sections = split_by_headers_or_paragraphs(text)
    
    # Extract TF-IDF features
    vectorizer = TfidfVectorizer(max_features=100, ngram_range=(1, 2))
    tfidf_matrix = vectorizer.fit_transform(sections)
    
    # Cluster semantically similar sections
    clustering = AgglomerativeClustering(n_clusters=target_clusters)
    labels = clustering.fit_predict(tfidf_matrix.toarray())
    
    # For each cluster, extract dominant keywords
    domains = {}
    for cluster_id in range(target_clusters):
        cluster_sections = [sections[i] for i in range(len(sections)) if labels[i] == cluster_id]
        keywords = extract_top_keywords(cluster_sections, top_n=10)
        domain_name = generate_domain_name(keywords)  # e.g., "Payment Processing Service"
        domains[domain_name] = keywords
    
    return domains
```

**Approach B: LLM-Based Domain Identification (Smart)**
```python
def identify_domains_with_llm(text: str, api_key: str = None):
    """
    Use LLM to intelligently identify bounded contexts.
    
    Prompt:
    "Analyze the following requirements and identify 5-6 distinct microservice
    bounded contexts following DDD principles. For each context, provide:
    1. Service name
    2. Primary responsibilities (1 sentence)
    3. Key entities/concepts
    4. Database recommendation
    
    Requirements:
    {text}
    
    Return as JSON."
    """
    if not api_key:
        return fallback_to_keyword_matching()
    
    response = call_llm_api(prompt, api_key)
    return parse_structured_response(response)
```

**Approach C: Hybrid (Current Keywords + Dynamic Extraction)**
```python
def hybrid_domain_detection(text: str):
    """
    1. Check for core universal domains (auth, payment, notification)
    2. For remaining text, use TF-IDF to extract 2-3 custom domains
    3. Limit total to 5-6 services
    """
    # Check core patterns (always look for these)
    detected = check_core_patterns(text, CORE_DOMAINS)
    
    # If we have < 5 services, extract more dynamically
    if len(detected) < 5:
        remaining_text = remove_detected_sections(text, detected)
        custom_domains = extract_dynamic_domains(remaining_text, target=5-len(detected))
        detected.extend(custom_domains)
    
    return detected[:6]  # Cap at 6
```

---

### Solution 3: Transparent Metrics with Dependency Tracking

**Problem:** Users don't understand how scores are calculated.

**Solution:** Add a `metric_breakdown` object explaining each score.

**New Data Structure:**
```python
@dataclass
class MetricBreakdown:
    metric_name: str
    final_score: int
    factors: List[Dict[str, Any]]  # What influenced the score
    recommendation: str

# Example output:
{
    "metric_name": "Coupling",
    "final_score": 67,
    "rating": "Moderate",
    "factors": [
        {
            "factor": "Total Dependencies",
            "value": 18,
            "impact": "High",
            "explanation": "18 dependencies detected across 6 services"
        },
        {
            "factor": "Average Dependencies per Service",
            "value": 3.0,
            "impact": "+20 points",
            "explanation": "3 deps/service falls in 'moderate coupling' band (35-55 range)"
        },
        {
            "factor": "Sync vs Async Dependencies",
            "value": "14 sync, 4 async",
            "impact": "+10 points penalty",
            "explanation": "Sync dependencies create tighter coupling"
        }
    ],
    "recommendation": "Reduce sync dependencies by introducing message queues for Order→Notification",
    "dependencies_breakdown": [
        {"from": "order-service", "to": "payment-service", "type": "sync", "coupling_contribution": 5},
        {"from": "order-service", "to": "identity-service", "type": "sync", "coupling_contribution": 5},
        # ... all deps with their contribution
    ]
}
```

**Updated Metrics Calculation:**
```python
def _calculate_metrics_with_explanation(services, dependencies, text):
    """
    Return both scores AND detailed breakdown of how each score was calculated.
    """
    n_services = len(services)
    n_deps = len(dependencies)
    avg_deps = n_deps / n_services
    
    # Calculate coupling with tracking
    coupling_factors = []
    
    if avg_deps == 0:
        coupling_score = 35
        coupling_factors.append({
            "factor": "No Dependencies Detected",
            "value": 0,
            "impact": "Score set to 35",
            "explanation": "Suspicious: real systems need some integration"
        })
    elif avg_deps <= 1:
        coupling_score = int(20 + avg_deps * 15)
        coupling_factors.append({
            "factor": "Very Low Dependency Density",
            "value": f"{avg_deps:.1f} deps/service",
            "impact": f"+{int(avg_deps * 15)} points",
            "explanation": "Excellent: Services are loosely coupled"
        })
    # ... rest of bands
    
    # Add per-service coupling contribution
    service_coupling = defaultdict(int)
    for dep in dependencies:
        service_coupling[dep.source] += 1
        coupling_factors.append({
            "factor": f"Dependency: {dep.source} → {dep.target}",
            "type": dep.type,
            "impact": "+5 points" if dep.type == "sync" else "+2 points",
            "explanation": dep.description
        })
    
    coupling_breakdown = MetricBreakdown(
        metric_name="Coupling",
        final_score=coupling_score,
        factors=coupling_factors,
        recommendation=generate_coupling_recommendation(coupling_score, dependencies)
    )
    
    # Same for other metrics...
    
    return {
        "scores": MetricScores(...),
        "breakdowns": {
            "coupling": coupling_breakdown,
            "scalability": scalability_breakdown,
            "maintainability": maintainability_breakdown,
            "fault_isolation": fault_isolation_breakdown
        }
    }
```

---

### Solution 4: Dependency Scoring Matrix

**What Dependencies Should We Look For?**

| Dependency Type | Coupling Impact | Fault Isolation Impact | Detection Pattern |
|---|---|---|---|
| **Sync API Call** | +5 points | -4 points | Keywords: "validate", "check", "before", "call", "request" |
| **Async Message** | +2 points | +2 points | Keywords: "queue", "event", "publish", "notify", "trigger" |
| **Shared Database** | +8 points | -6 points | Same database mentioned in multiple services |
| **Data Replication** | +3 points | +3 points | Keywords: "replicate", "sync", "copy", "cache" |
| **Circuit Breaker** | +1 point | +5 points | Keywords: "circuit breaker", "fallback", "retry", "timeout" |
| **API Gateway** | +2 points | +4 points | Keywords: "gateway", "proxy", "load balancer" |

**Dependency Detection Rules (Clear & Transparent):**
```python
DEPENDENCY_RULES = [
    {
        "name": "Authentication Token Validation",
        "pattern": "auth|token|jwt|validate credentials",
        "from": ["order-service", "payment-service", "catalog-service"],
        "to": "identity-service",
        "type": "sync",
        "coupling_impact": 5,
        "explanation": "All services must validate JWT tokens with Identity service",
        "recommendation": "Cache validated tokens to reduce calls"
    },
    {
        "name": "Payment Processing",
        "pattern": "payment|charge|transaction",
        "from": "order-service",
        "to": "payment-service",
        "type": "sync",
        "coupling_impact": 5,
        "explanation": "Order must wait for payment confirmation before completion",
        "recommendation": "Consider async payment with order state machine"
    },
    {
        "name": "Order Notification",
        "pattern": "order.*notify|send.*confirmation",
        "from": "order-service",
        "to": "notification-service",
        "type": "async",
        "coupling_impact": 2,
        "explanation": "Order publishes event; Notification consumes from queue",
        "recommendation": "Good: Already using async pattern"
    }
]
```

---

## Implementation Plan (Phased Approach)

### Phase 1: Reduce to 5-6 Core Domains ⚡ (Quick Win)
**Time:** 2-3 hours  
**Impact:** High

1. Replace 12 domains with 5-6 core domains in `nlp_engine.py`
2. Adjust confidence threshold to ensure 5-6 services (not 10+)
3. Update `_format_service_name()` and description mappings
4. Test with e-commerce example → should get ~5 services

**Files to modify:**
- `backend/app/services/nlp_engine.py` → `_load_domain_patterns()`
- `backend/app/services/analyzer_v2.py` → update thresholds in line 47

### Phase 2: Add Metrics Breakdown & Transparency 📊
**Time:** 4-5 hours  
**Impact:** High

1. Create `MetricBreakdown` model in `backend/app/models/analysis.py`
2. Update `_calculate_metrics()` to return breakdown data
3. Add frontend panel to show "Why this score?" with factors list
4. Add dependency contribution table

**Files to modify:**
- `backend/app/models/analysis.py` → add `MetricBreakdown` class
- `backend/app/services/analyzer_v2.py` → `_calculate_metrics_with_explanation()`
- `frontend/src/components/MetricsGrid.tsx` → add breakdown modal/panel

### Phase 3: Improve Dependency Detection Clarity 🔗
**Time:** 3-4 hours  
**Impact:** Medium

1. Replace implicit rules with explicit `DEPENDENCY_RULES` list
2. Add `coupling_impact` and `fault_isolation_impact` per rule
3. Show dependency detection reasoning in UI
4. Allow users to accept/reject suggested dependencies

**Files to modify:**
- `backend/app/services/analyzer_v2.py` → `_extract_dependencies()` use explicit rules
- Add `DEPENDENCY_RULES` configuration
- Frontend: Show detected dependencies with reasoning

### Phase 4: Dynamic Domain Extraction (Advanced) 🚀
**Time:** 8-10 hours  
**Impact:** High (but complex)

1. Implement TF-IDF keyword extraction
2. Add semantic clustering using sentence-transformers
3. Fallback to core patterns if clustering fails
4. Allow users to provide custom domain hints

**Files to create:**
- `backend/app/services/domain_extractor.py` → TF-IDF + clustering logic
- Update `nlp_engine.py` to use dynamic extraction

---

## Recommended Approach: Start with Phase 1 + Phase 2

**Why:**
- Quick wins that address immediate concerns
- Makes the tool feel less "synthetic"
- Provides transparency users are asking for
- Reduces cognitive load (5-6 services vs 12)

**Then:**
- Phase 3 if users need more control over dependencies
- Phase 4 only if you need to support wildly different industries

---

## Questions to Answer Before Implementation

1. **Target service count:** Should we allow users to specify "I want 4-8 services" as input?
2. **Industry templates:** Do you want predefined templates (e-commerce, healthcare, fintech)?
3. **User control:** Should users be able to edit/merge/split detected domains?
4. **Metric weights:** Should users be able to customize what matters (e.g., "I care more about scalability than coupling")?
5. **API integration:** Should we support LLM APIs (OpenAI, Gemini) for smart domain detection?

---

## Expected Outcomes After Phase 1+2

### Before (Current State):
```
E-commerce Requirements → 12 services detected
Coupling: 72 (no explanation)
User: "Why 72? What do I do about it?"
```

### After (Improved):
```
E-commerce Requirements → 5 services detected
Coupling: 42 (Healthy Range)

Breakdown:
- Total dependencies: 12
- Avg per service: 2.4 deps/service
- Band: Healthy (35-55 range)
- Biggest contributor: Order→Payment (sync, +5 points)
- Recommendation: "Consider async payment confirmation via message queue to reduce coupling by ~8 points"

Dependencies:
✓ order-service → identity-service (sync, auth token validation) [+5 coupling]
✓ order-service → payment-service (sync, charge processing) [+5 coupling]
✓ order-service → notification-service (async, order confirmation) [+2 coupling]
...
```

---

**Decision Required:** Which phases should we implement first?
