# Quality Metrics & API Endpoint Selection — ArchAItect

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

```
avg_deps_per_service = total_dependencies / total_services
coupling_score = clamp(20 + avg_deps_per_service × 15, min=10, max=100)
```

- Starts at a base of 20.
- Each average dependency per service adds 15 points.
- A low score (< 40) means services are loosely coupled — **good**.
- The frontend rating correctly inverts this: < 40 → "Excellent (Low)", > 65 → "High Coupling (Risk)".

### 2. Scalability (higher = better)

```
scalability_base = clamp(50 + total_services × 5, max=95)
scalability_score = max(40, scalability_base − coupling_score ÷ 10)
```

- More services → better independent scaling.
- High coupling penalizes scalability (tightly coupled services can't scale independently).

### 3. Maintainability (higher = better)

```
ideal_count = 7 services
service_diff_penalty = |total_services − 7| × 5
maintainability_base = max(50, 90 − service_diff_penalty)
maintainability_score = max(40, maintainability_base − coupling_score ÷ 8)
```

- Sweet spot is **7 services** (DDD best practice for bounded contexts).
- Too few services → monolith risk. Too many → cognitive overload.
- High coupling also reduces maintainability.

### 4. Fault Isolation (higher = better)

```
async_deps = count of dependencies where type == "async"
sync_deps  = total_dependencies − async_deps

fault_isolation_score = clamp(85 − sync_deps × 4 + async_deps × 2, min=35, max=98)
```

- Async dependencies (message queues, event buses) **improve** isolation (+2 each).
- Sync dependencies (direct HTTP calls) **reduce** isolation (−4 each) because one failure cascades.

---

## Does This Solve the Use Case?

**Yes — partially.** Here is an honest assessment:

| Goal from the image | Implemented? | Notes |
|---|---|---|
| Identify microservices from requirements | ✅ Yes | NLP domain detection + keyword matching |
| Generate API endpoints per service | ✅ Yes | Domain-mapped CRUD templates |
| Quality metrics (coupling, scalability, etc.) | ✅ Yes | Structural formula-based scores |
| Traceability matrix (requirement → service) | ⚠️ Partial | `analysis_metadata` captures counts; no visual matrix |
| IDL / Protobuf / Thrift generation | ❌ No | Only JSON/Markdown/Mermaid/PlantUML export |
| Store and learn from past decisions | ❌ No | File-based cache only, no feedback loop |
| Evaluate cohesion feedback loop | ⚠️ Partial | Cohesion score per service exists in metadata but not displayed |

---

## How Selecting a Microservice Shows Its API Endpoints

### Flow

```
User clicks node on canvas
    → GraphCanvas.tsx: setSelectedService(service)
        → Right panel renders selectedService.apis[]
            → Each ApiEndpoint shows: method, path, description
                → User can add / edit / delete endpoints inline
                    → "Save Changes" calls PUT /api/v1/analysis/{project_id}
```

### What an ApiEndpoint Contains

```typescript
// frontend/src/types.ts
interface ApiEndpoint {
  path: string;        // e.g. "/api/v1/orders/{id}"
  method: string;      // GET | POST | PUT | DELETE
  description: string; // Human-readable description
}
```

### Where API Endpoints Come From

Each microservice domain has a **hardcoded template** of realistic endpoints in `_generate_api_endpoints()`:

| Domain | Example endpoints generated |
|---|---|
| Authentication & Identity | POST /auth/signup, POST /auth/login, POST /auth/refresh … |
| Order Management | POST /orders, GET /orders/{id}, PUT /orders/{id}/cancel … |
| Payment & Billing | POST /payments/charge, POST /payments/refund … |
| Notification | POST /notifications/send, GET /notifications/templates … |
| Any unknown domain | Generic GET/POST/PUT /api/v1/{domain} CRUD set |

---

## What Is Still Missing / Can Be Improved

1. **Traceability Matrix** — a table mapping each requirement sentence → which service covers it. Currently only counts are stored in `analysis_metadata`.
2. **Cohesion score is hidden** — calculated per service (`metadata.cohesion_score`) but never shown in the UI.
3. **Coupling score display confusion** — for Coupling, a *lower* number is better, but it's displayed the same way as the other three metrics where higher = better. The rating label corrects this but the progress bar is misleading (a low coupling bar looks "bad").
4. **Metrics are structure-based only** — they reflect service count and dependency count, not actual semantic quality of boundaries.
5. **No IDL generation** (Protobuf/Thrift) — the image mentions this as a solution feature, it is not yet implemented.
