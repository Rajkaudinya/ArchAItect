# Quality Metrics & API Endpoint Selection — ArchAItect

---

## Executive Summary — Mathematics & Traceability

**Quality Metrics (all 0-100 scale):**

| Metric | Formula Summary | Good Score | Bad Score |
|---|---|---|---|
| **Coupling** | Band-based on `avg_deps/service`: 0→35, 0-1→20-35, 1-3→35-55, 3-5→55-75, 5+→75-95 | **< 40** (loose) | **> 75** (tight) |
| **Scalability** | `base = 45 + services×4` penalized by `(coupling-55)×0.6` if coupling>55 | **> 75** | **< 50** |
| **Maintainability** | Band-based on service count (optimal: 5-10), penalized by `(coupling-40)×0.4` | **> 70** | **< 45** |
| **Fault Isolation** | `35 + async_ratio×55 - max(0, sync_deps-3)×3` | **> 70** | **< 40** |

**Traceability Matrix:**  
Regex-splits requirements into sentences → matches each service's keywords → stores top 3 sentences per service → proves requirement coverage.

**Complete Pipeline:**  
Text → NLP extraction (spaCy) → Domain detection (keyword scoring) → Schema generation → Database selection → API templates → Dependency rules → Cohesion calc → Metrics → Traceability → JSON output.

---

## Where Is Everything Defined?

| Concern | File | Location |
|---|---|---|
| **MetricScores model** (data shape) | `backend/app/models/analysis.py` | `class MetricScores` — lines 28–32 |
| **Metrics calculation logic** | `backend/app/services/analyzer_v2.py` | `_calculate_metrics()` — line 437 |
| **Frontend display cards** | `frontend/src/components/MetricsGrid.tsx` | Full file |
| **API endpoint generation** | `backend/app/services/analyzer_v2.py` | `_generate_api_endpoints()` — line ~220 |
| **API endpoint model** | `backend/app/models/analysis.py` | `class ApiEndpoint` — lines 12–18 |
| **Click-to-inspect (frontend)** | `frontend/src/components/GraphCanvas.tsx` | `setSelectedService(service)` on node click |

---

## How Each Quality Metric Is Calculated

All four scores are computed **after** services and dependencies are generated, in `_calculate_metrics()` inside `analyzer_v2.py`.

### 1. Coupling (lower raw score = better design)

**Formula (Band-based):**
```python
avg_deps = total_dependencies / total_services

if avg_deps == 0:
    coupling_score = 35  # suspicious: real systems need some integration
elif avg_deps ≤ 1:
    coupling_score = 20 + avg_deps × 15  # Range: 20→35 (very loose, good)
elif avg_deps ≤ 3:
    coupling_score = 35 + (avg_deps - 1) × 10  # Range: 35→55 (healthy)
elif avg_deps ≤ 5:
    coupling_score = 55 + (avg_deps - 3) × 10  # Range: 55→75 (moderate)
else:
    coupling_score = min(95, 75 + (avg_deps - 5) × 4)  # Range: 75→95 (high risk)
```

**Interpretation:**
- **20-35**: Excellent (very loose coupling)
- **35-55**: Healthy coupling for microservices
- **55-75**: Moderate, manageable
- **75-95**: High coupling, deployment risk

### 2. Scalability (higher = better)

**Formula:**
```python
scalability_base = min(93, 45 + total_services × 4)
coupling_excess = max(0, coupling_score - 55)
scalability_score = max(30, scalability_base - coupling_excess × 0.6)
```

**Logic:**
- More services (3→12) gives base score 57→93
- Coupling above 55 penalizes scalability (tightly coupled services can't scale independently)
- Penalty factor: 0.6 points per coupling point above 55

### 3. Maintainability (higher = better)

**Formula (DDD-aligned):**
```python
if total_services ≤ 2:
    maint_base = 35  # monolith risk
elif total_services ≤ 5:
    maint_base = 50 + (total_services - 3) × 8  # Range: 50→66
elif total_services ≤ 10:
    maint_base = 66 + (total_services - 5) × 3  # Range: 66→81 (optimal)
else:
    maint_base = max(55, 81 - (total_services - 10) × 4)  # degrades past 10

coupling_excess = max(0, coupling_score - 40)
maintainability_score = max(30, maint_base - coupling_excess × 0.4)
```

**Logic:**
- Sweet spot: **5-10 services** (DDD bounded context best practice)
- Too few (≤2) → hidden monolith
- Too many (>10) → cognitive overload
- Coupling above 40 reduces maintainability (penalty: 0.4× per point)

### 4. Fault Isolation (higher = better)

**Formula:**
```python
async_deps = count where dependency.type == "async"
sync_deps = total_dependencies - async_deps

if total_dependencies == 0:
    fault_isolation_score = 50  # neutral baseline
else:
    async_ratio = async_deps / total_dependencies
    fi_base = 35 + async_ratio × 55  # all-sync=35, all-async=90
    extra_sync_penalty = max(0, sync_deps - 3) × 3
    fault_isolation_score = min(95, max(25, fi_base - extra_sync_penalty))
```

**Logic:**
- **Async dependencies** (queues, event buses) buffer failures → higher score
- **Sync dependencies** (HTTP calls) create cascading failures → lower score
- Async ratio 0 (all sync) → base 35 | ratio 1 (all async) → base 90
- Each sync dependency beyond 3 adds cascading risk (-3 points each)

---

## Traceability Matrix — How Requirements Map to Services

**Location:** `analyzer_v2.py` → `_build_traceability()` (lines 503-546)

**Algorithm:**
```python
1. Split requirements text into sentences (regex: split on [.!?])
2. For each microservice + its matched domain keywords:
   - Scan all sentences, find those containing ≥1 keyword
   - Extract top 3 sentences (max 160 chars each)
   - Store: service_id, service_name, domain, confidence, keywords, sentences
3. Return matrix as list of dicts
```

**Output Structure:**
```json
{
  "service_id": "identity-service",
  "service_name": "Identity Service",
  "domain": "Authentication & Identity",
  "confidence": 78.5,
  "matched_keywords": ["auth", "login", "jwt", "token", "password", "signup"],
  "requirement_sentences": [
    "Users must authenticate using secure JWT tokens.",
    "The system shall support OAuth 2.0 and SSO integration.",
    "Password reset flows must include email verification."
  ]
}
```

**Usage:** Stored in `analysis_metadata.traceability[]` — proves which requirements justify each service's existence.

---

## How API Endpoints Are Generated & Displayed

**Generation Logic:** `analyzer_v2.py` → `_generate_api_endpoints()` (line ~220)

**Process:**
1. **Domain Matching:** Each service domain has hardcoded CRUD endpoint templates
   - Authentication & Identity → `/api/v1/auth/signup`, `/auth/login`, `/auth/refresh`, `/users/profile`
   - Order Management → `/api/v1/orders`, `/orders/{id}`, `/orders/{id}/cancel`, `/orders/{id}/status`
   - Payment & Billing → `/api/v1/payments/charge`, `/payments/refund`, `/invoices`, `/payments/{id}/status`
   - Inventory & Catalog → `/api/v1/catalog/products`, `/catalog/products/{id}`, `/inventory/reserve`
   - Unknown domains → Generic CRUD: `GET/POST /api/v1/{domain}`, `GET/PUT/DELETE /api/v1/{domain}/{id}`

2. **Endpoint Structure:**
   ```typescript
   interface ApiEndpoint {
     path: string;        // e.g. "/api/v1/orders/{id}"
     method: string;      // GET | POST | PUT | DELETE
     description: string; // "Retrieve order details and history"
   }
   ```

**User Interaction Flow:**
```
User clicks service node in graph
  → GraphCanvas.tsx: setSelectedService(service)
    → Right panel renders selectedService.apis[]
      → Display: method badge + path + description
        → User can inline edit/add/delete endpoints
          → "Save Changes" → PUT /api/v1/analysis/{project_id}
            → Updates JSON file → Reloads analysis
```

**Why This Matters:**  
Realistic API contracts help architects immediately see the service interface without manual design, enabling faster API-first development and contract testing.

---

## Complete Analysis Pipeline — One-Line Explanations

| Step | File | Method | What It Does | Mathematics / Logic |
|---|---|---|---|---|
| **1. Entity Extraction** | `nlp_engine.py` | `extract_entities_and_actions()` | Uses spaCy NLP to extract verbs (actions), nouns (concepts), named entities (ORG, PRODUCT, etc.) from requirements text | POS tagging: `token.pos_ == 'VERB'` → actions, `token.pos_ == 'NOUN'` → concepts |
| **2. Domain Detection** | `nlp_engine.py` | `identify_service_domains()` | Matches 12 predefined domain patterns (Auth, Order, Payment, etc.) against text using keyword scoring + semantic similarity | `score = Σ(keyword_matches × phrase_length × 2) + (section_mentions × 3)` → confidence (0-100) |
| **3. Service Schema Generation** | `analyzer_v2.py` | `_build_microservice_schema()` | Constructs full service definition: ID, name, description, database, APIs, scaling recs, cohesion score | Each service gets domain-mapped templates |
| **4. Database Selection** | `nlp_engine.py` | `suggest_database_type()` | Scores domain keywords against DB type indicators (SQL: transaction/order, NoSQL: catalog/profile, Cache: session/queue, Timeseries: analytics/log) | `score_SQL = Σ(2 if indicator in text)` → pick max score |
| **5. API Endpoint Generation** | `analyzer_v2.py` | `_generate_api_endpoints()` | Maps domain to CRUD templates (Auth → `/auth/signup`, Order → `/orders/{id}`, etc.) or generates generic REST endpoints | Hardcoded domain→endpoint templates |
| **6. Scaling Recommendations** | `analyzer_v2.py` | `_generate_scaling_recommendations()` | Returns domain-specific architectural patterns (Auth→Redis cache, Order→Event sourcing, Payment→Circuit breaker) | Lookup table per domain |
| **7. Dependency Extraction** | `analyzer_v2.py` | `_extract_dependencies()` | Applies 12 rule-based patterns (e.g., if "auth" in text → all services depend on Identity; if "order" + "payment" → Order→Payment sync dependency) | Pattern matching: `if text_pattern in doc AND service matches from_keywords → add dependency` |
| **8. Cohesion Calculation** | `nlp_engine.py` | `calculate_cohesion_score()` | Measures keyword co-occurrence density within sentences | `cohesion = min(100, (co_occurrence_count / max_possible) × 1000)` |
| **9. Metrics Calculation** | `analyzer_v2.py` | `_calculate_metrics()` | Computes 4 scores (Coupling, Scalability, Maintainability, Fault Isolation) using band-based formulas | See formulas above ↑ |
| **10. Traceability Matrix** | `analyzer_v2.py` | `_build_traceability()` | Maps each service back to 3 requirement sentences that contain its keywords | Sentence-keyword matching + top-3 selection |
| **11. Result Assembly** | `analyzer_v2.py` | `analyze_requirements()` | Packages everything into `AnalysisResult` model with metadata (entity counts, NLP status, traceability) | JSON serialization → stored in `data/analysis_{project_id}.json` |

---

## Does This Solve the Use Case?

**Yes — partially.** Here is an honest assessment:

| Goal from the image | Implemented? | Notes |
|---|---|---|
| Identify microservices from requirements | ✅ Yes | NLP domain detection + keyword matching with confidence scoring |
| Generate API endpoints per service | ✅ Yes | Domain-mapped CRUD templates with realistic paths/methods |
| Quality metrics (coupling, scalability, etc.) | ✅ Yes | Band-based structural formulas using service/dependency topology |
| Traceability matrix (requirement → service) | ✅ Yes | Each service linked to top 3 requirement sentences via keyword matching |
| IDL / Protobuf / Thrift generation | ❌ No | Only JSON/Markdown/Mermaid/PlantUML export formats supported |
| Store and learn from past decisions | ❌ No | File-based cache only, no ML feedback loop or historical learning |
| Display cohesion in UI | ⚠️ Partial | Cohesion score calculated per service (`metadata.cohesion_score`) but not shown in frontend |
| Coupling visualization clarity | ⚠️ Needs fix | Progress bar misleading (low coupling looks "bad" but is actually good) |

---

## What Is Still Missing / Can Be Improved

1. **Coupling score UI confusion** — For Coupling, a *lower* number is better, but the progress bar displays it the same way as other metrics where higher=better. The rating label correctly shows "Excellent (Low)" vs "High Coupling (Risk)" but the bar itself is visually misleading.

2. **Cohesion score is hidden** — Calculated per service (`metadata.cohesion_score`) using keyword co-occurrence density, but never displayed in the UI. Should add to service detail panel.

3. **Metrics are structure-based only** — Scores reflect service count and dependency topology, not actual semantic quality of domain boundaries. A human architect might disagree with the numerical score.

4. **No IDL generation** (Protobuf/Thrift) — The original vision mentions generating interface definition languages for type-safe service contracts. Currently only exports JSON/Markdown diagrams.

5. **No feedback loop** — System doesn't learn from user edits (e.g., if user deletes a dependency or merges services, those corrections should inform future analyses).

6. **Traceability not visualized** — Matrix is stored in `analysis_metadata.traceability[]` but not shown in the UI. Could add a "Requirements Coverage" tab showing which sentences justify each service.

---

## Quick Reference Card — All Formulas

```python
# ══════════════════════════════════════════════════════════════════════════
# QUALITY METRICS CALCULATION — analyzer_v2.py::_calculate_metrics()
# ══════════════════════════════════════════════════════════════════════════

n_services = len(services)
n_deps = len(dependencies)
avg_deps = n_deps / n_services

# ── COUPLING (lower = better) ────────────────────────────────────────────
if avg_deps == 0:     coupling_score = 35
elif avg_deps ≤ 1:    coupling_score = 20 + avg_deps × 15
elif avg_deps ≤ 3:    coupling_score = 35 + (avg_deps - 1) × 10
elif avg_deps ≤ 5:    coupling_score = 55 + (avg_deps - 3) × 10
else:                 coupling_score = min(95, 75 + (avg_deps - 5) × 4)

# ── SCALABILITY (higher = better) ────────────────────────────────────────
scalability_base = min(93, 45 + n_services × 4)
coupling_excess = max(0, coupling_score - 55)
scalability_score = max(30, scalability_base - coupling_excess × 0.6)

# ── MAINTAINABILITY (higher = better) ────────────────────────────────────
if n_services ≤ 2:    maint_base = 35
elif n_services ≤ 5:  maint_base = 50 + (n_services - 3) × 8
elif n_services ≤ 10: maint_base = 66 + (n_services - 5) × 3
else:                 maint_base = max(55, 81 - (n_services - 10) × 4)

coupling_excess = max(0, coupling_score - 40)
maintainability_score = max(30, maint_base - coupling_excess × 0.4)

# ── FAULT ISOLATION (higher = better) ────────────────────────────────────
async_deps = count(d for d in dependencies if d.type == "async")
sync_deps = n_deps - async_deps

if n_deps == 0:
    fault_isolation_score = 50
else:
    async_ratio = async_deps / n_deps
    fi_base = 35 + async_ratio × 55
    extra_sync_penalty = max(0, sync_deps - 3) × 3
    fault_isolation_score = min(95, max(25, fi_base - extra_sync_penalty))

# ══════════════════════════════════════════════════════════════════════════
# TRACEABILITY MATRIX — analyzer_v2.py::_build_traceability()
# ══════════════════════════════════════════════════════════════════════════

sentences = regex_split(text, r'(?<=[.!?])\s+')
for each service with matched_keywords:
    relevant_sentences = [s for s in sentences if any(kw in s.lower() for kw in matched_keywords)]
    traceability[service] = relevant_sentences[:3]  # top 3

# ══════════════════════════════════════════════════════════════════════════
# DOMAIN DETECTION SCORE — nlp_engine.py::identify_service_domains()
# ══════════════════════════════════════════════════════════════════════════

for each domain:
    score = Σ(len(keyword.split()) × 2 for keyword in matched_keywords)
    if sections:
        score += section_mentions × 3
    confidence = min(100, score × 2)
    if confidence > 10:
        detected_domains.append((domain_name, confidence, matched_keywords))

# ══════════════════════════════════════════════════════════════════════════
# COHESION SCORE — nlp_engine.py::calculate_cohesion_score()
# ══════════════════════════════════════════════════════════════════════════

co_occurrence_count = count of sentences where ≥2 keywords appear together
max_possible = len(keywords) × len(sentences)
cohesion = min(100, (co_occurrence_count / max_possible) × 1000)
```

---

**End of Document**
