# ArchAItect - System Architecture Flow

## High-Level Overview

```
┌──────────────────────────────────────────────────────────────────┐
│                         USER INTERFACE                            │
│  (React + TypeScript + Vite + TailwindCSS)                       │
└───────────────────────┬──────────────────────────────────────────┘
                        │
                        │ HTTP REST API
                        ▼
┌──────────────────────────────────────────────────────────────────┐
│                    FASTAPI BACKEND (Python)                       │
│  • API Routes (upload, analysis, export)                         │
│  • File Parsing (txt, md, pdf, docx)                            │
│  • Business Logic Orchestration                                  │
└───────────────────────┬──────────────────────────────────────────┘
                        │
                        ▼
┌──────────────────────────────────────────────────────────────────┐
│                    ANALYSIS ENGINE PIPELINE                       │
│                                                                   │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  1. NLP EXTRACTION (nlp_engine.py)                      │   │
│  │     • spaCy: Extract entities, verbs, nouns             │   │
│  │     • Sentence-Transformers: Semantic embeddings        │   │
│  │     Output: entities[], actions[], concepts[]           │   │
│  └──────────────────────┬──────────────────────────────────┘   │
│                         │                                        │
│  ┌─────────────────────▼──────────────────────────────────┐   │
│  │  2. DOMAIN DETECTION (nlp_engine.py)                    │   │
│  │     • Match 12 hardcoded domain patterns                │   │
│  │     • Keyword scoring: Σ(phrase_length × 2)            │   │
│  │     • Confidence filtering (threshold: > 15)            │   │
│  │     Output: [(domain, confidence, keywords)]            │   │
│  └──────────────────────┬──────────────────────────────────┘   │
│                         │                                        │
│  ┌─────────────────────▼──────────────────────────────────┐   │
│  │  3. SERVICE SCHEMA GENERATION (analyzer_v2.py)          │   │
│  │     For each detected domain:                           │   │
│  │     • Generate service ID, name, description            │   │
│  │     • Database selection (SQL/NoSQL/Cache scoring)      │   │
│  │     • API endpoint templates (CRUD)                     │   │
│  │     • Scaling recommendations (cached patterns)         │   │
│  │     • Cohesion score: keyword co-occurrence             │   │
│  │     Output: MicroserviceSchema[]                        │   │
│  └──────────────────────┬──────────────────────────────────┘   │
│                         │                                        │
│  ┌─────────────────────▼──────────────────────────────────┐   │
│  │  4. DEPENDENCY EXTRACTION (analyzer_v2.py)              │   │
│  │     • Apply 12 rule-based patterns                      │   │
│  │     • Pattern matching (if "auth" in text → all→identity)│   │
│  │     • Keyword-based service matching                    │   │
│  │     Output: DependencyInfo[]                            │   │
│  └──────────────────────┬──────────────────────────────────┘   │
│                         │                                        │
│  ┌─────────────────────▼──────────────────────────────────┐   │
│  │  5. METRICS CALCULATION (analyzer_v2.py)                │   │
│  │     Band-based formulas:                                │   │
│  │     • Coupling: avg_deps → score bands                  │   │
│  │     • Scalability: service_count - coupling_penalty     │   │
│  │     • Maintainability: optimal 5-10 services            │   │
│  │     • Fault Isolation: async_ratio × 55 + base          │   │
│  │     Output: MetricScores                                │   │
│  └──────────────────────┬──────────────────────────────────┘   │
│                         │                                        │
│  ┌─────────────────────▼──────────────────────────────────┐   │
│  │  6. TRACEABILITY MATRIX (analyzer_v2.py)                │   │
│  │     • Split text into sentences (regex)                 │   │
│  │     • Match keywords to sentences                       │   │
│  │     • Top 3 sentences per service                       │   │
│  │     Output: traceability[]                              │   │
│  └──────────────────────┬──────────────────────────────────┘   │
│                         │                                        │
│                         ▼                                        │
│                AnalysisResult (JSON)                            │
└───────────────────────┬──────────────────────────────────────────┘
                        │
                        │ Save to File
                        ▼
┌──────────────────────────────────────────────────────────────────┐
│              FILE STORAGE (data/)                                 │
│  • projects.json                                                 │
│  • analysis_project-{uuid}.json                                  │
└──────────────────────────────────────────────────────────────────┘
                        │
                        │ Export Options
                        ▼
┌──────────────────────────────────────────────────────────────────┐
│              EXPORTER (exporter.py)                               │
│  • JSON Report                                                   │
│  • Markdown Document                                             │
│  • Mermaid Diagram                                               │
│  • PlantUML Diagram                                              │
└──────────────────────────────────────────────────────────────────┘
```

---

## Data Flow Step-by-Step

### Step 1: User Uploads Requirements
```
User (Browser)
    → POST /api/v1/analysis/upload
        • project_id: string
        • file: uploaded file (.txt, .md, .pdf, .docx)
    → Backend receives file
    → DocumentParser extracts raw text
```

### Step 2: NLP Processing
```
Raw Text
    → nlp_engine.extract_entities_and_actions()
        • spaCy tokenization
        • POS tagging (VERB → actions, NOUN → concepts)
        • Named entity recognition (ORG, PRODUCT, etc.)
    → Returns: {"entities": [...], "actions": [...], "concepts": [...]}
```

### Step 3: Domain Detection
```
Raw Text + Entities
    → nlp_engine.identify_service_domains()
        • For each of 12 predefined domains:
            - Count keyword matches
            - Calculate score = Σ(len(keyword.split()) × 2)
            - Add section bonus (×3 if in multiple sections)
            - Confidence = min(100, score × 2)
        • Filter domains where confidence > 15
        • Sort by confidence descending
    → Returns: [("Auth & Identity", 78.5, ["auth", "login"]), ...]
```

### Step 4: Service Generation
```
For each detected domain:
    → analyzer_v2._build_microservice_schema()
        • Generate service ID: domain.lower().replace(" ", "-")
        • Map domain → predefined description
        • Database selection:
            - Count SQL indicators (transaction, order, payment)
            - Count NoSQL indicators (catalog, profile, content)
            - Count Cache indicators (session, notification, queue)
            - Pick highest score
        • API endpoints: domain → CRUD template mapping
        • Scaling recs: domain → cached recommendations
        • Cohesion: keyword co-occurrence in sentences / max_possible
    → Returns: MicroserviceSchema
```

### Step 5: Dependency Detection
```
Services + Text
    → analyzer_v2._extract_dependencies()
        • Apply 12 hardcoded rules:
            Rule: if "auth" in text
                → all services (except identity) → identity-service (sync)
            Rule: if "order" + "payment" in text
                → order-service → payment-service (sync)
            Rule: if "order" + "notification" in text
                → order-service → notification-service (async)
            ... (9 more rules)
        • Match services by keyword substring matching
    → Returns: [DependencyInfo(source, target, type, desc), ...]
```

### Step 6: Metrics Calculation
```
Services + Dependencies
    → analyzer_v2._calculate_metrics()
        • n_services = len(services)
        • n_deps = len(dependencies)
        • avg_deps = n_deps / n_services
        
        Coupling:
            if avg_deps == 0: score = 35
            elif avg_deps ≤ 1: score = 20 + avg_deps × 15
            elif avg_deps ≤ 3: score = 35 + (avg_deps-1) × 10
            elif avg_deps ≤ 5: score = 55 + (avg_deps-3) × 10
            else: score = 75 + (avg_deps-5) × 4
        
        Scalability:
            base = min(93, 45 + n_services × 4)
            penalty = max(0, coupling - 55) × 0.6
            score = max(30, base - penalty)
        
        Maintainability:
            if n ≤ 2: base = 35
            elif n ≤ 5: base = 50 + (n-3)×8
            elif n ≤ 10: base = 66 + (n-5)×3
            else: base = 81 - (n-10)×4
            penalty = max(0, coupling-40) × 0.4
            score = max(30, base - penalty)
        
        Fault Isolation:
            async_ratio = async_deps / total_deps
            base = 35 + async_ratio × 55
            penalty = max(0, sync_deps-3) × 3
            score = min(95, max(25, base - penalty))
    
    → Returns: MetricScores(scalability, coupling, maintainability, fault_isolation)
```

### Step 7: Response to Frontend
```
AnalysisResult
    → JSON serialization
    → Save to data/analysis_project-{uuid}.json
    → Return HTTP 200 with JSON body
    → Frontend renders:
        • Graph visualization (services as nodes, dependencies as edges)
        • Metrics cards (4 progress bars with ratings)
        • Service detail panel (APIs, database, recommendations)
        • Traceability table (hidden in metadata)
```

---

## Technology Stack

| Layer | Technology | Purpose |
|---|---|---|
| **Frontend** | React 18 + TypeScript | UI framework |
| | Vite | Build tool & dev server |
| | TailwindCSS | Styling |
| | React Force Graph | Graph visualization |
| **Backend** | FastAPI | REST API framework |
| | Python 3.12+ | Core language |
| | Pydantic | Data validation |
| | python-multipart | File upload handling |
| **NLP** | spaCy (en_core_web_sm) | POS tagging, NER |
| | sentence-transformers | Semantic embeddings |
| | (all-MiniLM-L6-v2) | Text similarity |
| **Parsing** | python-docx | DOCX files |
| | PyPDF2 | PDF extraction |
| **Storage** | JSON files | File-based persistence |
| | (data/ directory) | No database yet |
| **Export** | Jinja2 | Template rendering |
| | Markdown | Document export |

---

## Current Limitations

### 1. Hardcoded Domain Patterns
- **Issue:** 12 predefined domains with static keywords
- **Impact:** Not adaptable to healthcare, finance, gaming, etc.
- **Example:** E-commerce always generates 7-12 services

### 2. No LLM Integration (Despite Groq API Key)
- **Status:** `GROQ_API_KEY` is configured but **never used**
- **Missed Opportunity:** Could intelligently detect domains
- **Current:** Pure keyword matching

### 3. Rule-Based Dependencies
- **Issue:** 12 hardcoded if-then rules
- **Impact:** Inflexible, requires code changes to add new patterns
- **Example:** `if "auth" in text → all services → identity`

### 4. Opaque Metrics
- **Issue:** Users see "Coupling: 67" with no explanation
- **Impact:** Can't understand WHY or HOW to improve
- **Missing:** Breakdown of factors contributing to score

### 5. No User Control
- **Issue:** Can't specify "I want 5 services" or edit domains
- **Impact:** Tool feels like black box
- **Needed:** Interactive refinement

---

## Key Files Reference

| File | Lines of Code | Purpose |
|---|---|---|
| `backend/app/api/analysis.py` | ~180 | Upload endpoint, orchestration |
| `backend/app/services/nlp_engine.py` | ~360 | Domain patterns, spaCy, embeddings |
| `backend/app/services/analyzer_v2.py` | ~640 | Core analysis logic, metrics |
| `backend/app/services/parser.py` | ~120 | Document parsing (PDF, DOCX) |
| `backend/app/services/exporter.py` | ~180 | Export to JSON/MD/Mermaid/PlantUML |
| `backend/app/models/analysis.py` | ~80 | Data models (Pydantic) |
| `frontend/src/App.tsx` | ~250 | Main React component |
| `frontend/src/components/GraphCanvas.tsx` | ~340 | Force-directed graph |
| `frontend/src/components/MetricsGrid.tsx` | ~140 | Metrics cards display |

---

## Recommended Next Steps

1. **Reduce to 5-6 core domains** (Phase 1) - Quick win
2. **Add metrics breakdown UI** (Phase 2) - Explain scores
3. **Integrate Groq API** for smart domain detection
4. **Make dependency rules explicit** and transparent
5. **Add user control** (merge/split services, edit dependencies)

---

**Architecture Type:** Monolithic backend with modular service layers, file-based storage, React SPA frontend.

**Scalability:** Currently single-instance only. No database, no caching, no horizontal scaling.

**Deployment:** Runs locally on localhost:8000 (backend) + localhost:5173 (frontend).
