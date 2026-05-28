# 🏛️ ArchAItect — AI-Powered Microservice Architecture Generator

**ArchAItect** is an advanced AI solution that automatically translates software requirements documents (SRS, BRDs, User Stories, Functional Specs) into scalable microservice architectures using state-of-the-art NLP and semantic analysis.

## 🌟 Key Features

### 🤖 Advanced AI Analysis
- **NLP-Powered Domain Detection**: Uses spaCy and transformers for intelligent entity recognition
- **Semantic Clustering**: Groups related requirements into bounded contexts using sentence embeddings
- **Dependency Extraction**: Automatically identifies service dependencies through co-occurrence analysis
- **Smart Database Selection**: Recommends optimal database types (SQL, NoSQL, Cache, Time-series) based on domain characteristics

### 🎯 Microservice Intelligence
- **Automatic Boundary Identification**: Detects microservice boundaries from natural language requirements
- **RESTful API Generation**: Creates comprehensive API endpoint specifications with CRUD operations
- **Scaling Recommendations**: Provides architecture patterns (Circuit Breaker, CQRS, Event Sourcing)
- **Quality Metrics**: Calculates scalability, coupling, maintainability, and fault isolation scores

### 📊 Rich Export Options
- **Markdown Documentation**: Complete architecture documentation with metrics
- **Mermaid Diagrams**: Visual service dependency graphs
- **PlantUML**: Component diagrams for presentations
- **JSON Schema**: Structured export for CI/CD integration
- **OpenAPI Specs**: API specification stubs for each service

### 🎨 Interactive Visual Editor
- **Drag-and-drop Canvas**: Interactive topology with visual flow lines
- **Real-time Updates**: Modify services and APIs on the fly
- **Metrics Dashboard**: Live quality metrics with risk thresholds

---

## 🚀 Quick Start Guide

### Prerequisites
- **Python 3.8+** (with pip)
- **Node.js 18+** (with npm)
- **4GB RAM** minimum (for NLP models)

### Automated Setup (Recommended)

```powershell
# Run the automated setup script
.\setup.ps1
```

The setup script will:
- ✅ Create Python virtual environment
- ✅ Install all dependencies
- ✅ Download NLP models (spaCy, transformers)
- ✅ Test all imports

### Manual Setup

#### 1. 🐍 Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Download NLP models
python -m spacy download en_core_web_sm
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"

# Start backend server
python run.py
```

**Backend will be running on:** [http://localhost:8000](http://localhost:8000)  
**API Documentation:** [http://localhost:8000/docs](http://localhost:8000/docs)

#### 2. ⚛️ Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

**Frontend will be running on:** [http://localhost:3000](http://localhost:3000)

---

## 📚 Usage Guide

### 1️⃣ Create a Project

1. Click **"New Blueprint"** in the header
2. Enter a project name (e.g., "Ride Sharing Platform")
3. Click **Create**

### 2️⃣ Upload Requirements Document

1. Click the upload area or drag-and-drop your document
2. Supported formats: `.txt`, `.md`, `.pdf`, `.docx`
3. The AI will analyze the document and generate the architecture

### 3️⃣ Review Generated Architecture

The system will identify:
- **Microservices** with intelligent domain grouping
- **API Endpoints** for each service
- **Database Types** with rationale
- **Dependencies** (sync/async)
- **Scaling Recommendations**
- **Quality Metrics**

### 4️⃣ Customize & Export

- Drag services on the canvas to reorganize
- Click services to edit names, APIs, databases
- Click **Save Changes** to persist modifications
- Use **Export** options to generate documentation

---

## 🧠 AI Architecture Engine

### NLP Pipeline

```
Requirements Document
        ↓
[Document Parser] → Sections, Requirements, Structure
        ↓
[Entity Extraction] → spaCy NLP → Entities, Actions, Concepts
        ↓
[Domain Detection] → Semantic Similarity → Service Boundaries
        ↓
[API Generation] → Pattern Matching → RESTful Endpoints
        ↓
[Dependency Analysis] → Co-occurrence → Service Dependencies
        ↓
[Metrics Calculation] → Quality Assessment
        ↓
Architecture Result
```

### Technology Stack

#### Backend
- **FastAPI** - Modern async Python web framework
- **spaCy** - Industrial-strength NLP
- **Sentence Transformers** - Semantic embeddings
- **PyTorch** - Deep learning framework
- **scikit-learn** - ML algorithms
- **NLTK** - Natural language toolkit

#### Frontend
- **React 18** - UI framework
- **TypeScript** - Type-safe JavaScript
- **Vite** - Next-generation build tool
- **Tailwind CSS** - Utility-first styling
- **Lucide Icons** - Beautiful icon set

---

## 📖 API Endpoints

### Analysis APIs

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/analysis/upload` | POST | Upload and analyze requirements document |
| `/api/v1/analysis/{project_id}` | GET | Retrieve analysis results |
| `/api/v1/analysis/{project_id}` | PUT | Update customized architecture |

### Export APIs

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/analysis/{project_id}/export/markdown` | GET | Export as Markdown docs |
| `/api/v1/analysis/{project_id}/export/mermaid` | GET | Export Mermaid diagram |
| `/api/v1/analysis/{project_id}/export/plantuml` | GET | Export PlantUML diagram |
| `/api/v1/analysis/{project_id}/export/json` | GET | Export JSON schema |

### Project Management

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/projects` | GET | List all projects |
| `/api/v1/projects` | POST | Create new project |
| `/api/v1/projects/{id}` | DELETE | Delete project |

---

## 🎯 Example: Sample Analysis

Try the system with the included sample:

```bash
# The sample_requirements.md file contains a complete ride-sharing platform specification
# Upload it through the UI to see the AI in action!
```

**Expected Output:**
- 10-12 identified microservices
- 40+ API endpoints
- Intelligent database selections
- Sync/async dependency mapping
- Architecture quality scores

---

## 🔧 Architecture Patterns Identified

The AI recognizes and recommends these patterns:

- ✅ **Event Sourcing** - For order lifecycle tracking
- ✅ **CQRS** - Separate read/write models for analytics
- ✅ **Circuit Breaker** - For external payment gateway calls
- ✅ **Saga Pattern** - Distributed transaction management
- ✅ **API Gateway** - Centralized authentication and rate limiting
- ✅ **Message Queue** - Async notification delivery
- ✅ **Read Replicas** - Scale read-heavy operations
- ✅ **CDN** - Static content delivery

---

## 🏗️ Project Structure

```
ArchAItect/
├── backend/
│   ├── app/
│   │   ├── api/           # API routes
│   │   │   ├── analysis.py    # Analysis endpoints + exports
│   │   │   ├── projects.py    # Project management
│   │   │   └── auth.py        # Authentication
│   │   ├── models/        # Pydantic models
│   │   │   ├── analysis.py
│   │   │   └── project.py
│   │   ├── services/      # Business logic
│   │   │   ├── analyzer_v2.py    # AI analyzer (NEW!)
│   │   │   ├── nlp_engine.py    # NLP processing (NEW!)
│   │   │   ├── parser.py        # Document parsing
│   │   │   └── exporter.py      # Export formats (NEW!)
│   │   ├── config.py
│   │   └── main.py
│   ├── requirements.txt   # Python dependencies
│   └── run.py
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── FileUpload.tsx
│   │   │   ├── GraphCanvas.tsx
│   │   │   └── MetricsGrid.tsx
│   │   ├── App.tsx
│   │   └── types.ts
│   └── package.json
├── sample_requirements.md  # Sample document (NEW!)
├── setup.ps1              # Automated setup (NEW!)
└── README.md
```

---

## 🎓 Advanced Features

### Custom Domain Templates

Add your own domain patterns in `nlp_engine.py`:

```python
self.domain_keywords["Custom Domain"] = [
    "keyword1", "keyword2", "pattern"
]
```

### Adjust Confidence Thresholds

In `analyzer_v2.py`, tune detection sensitivity:

```python
if confidence > 10:  # Lower = more services detected
```

### Add Custom Export Formats

Extend `exporter.py` with new export methods:

```python
@staticmethod
def to_custom_format(analysis: AnalysisResult) -> str:
    # Your custom export logic
    pass
```

---

## 🔍 Troubleshooting

### NLP Models Not Loading

```bash
# Manually download spaCy model
python -m spacy download en_core_web_sm

# If still failing, the system will use fallback keyword matching
```

### Port Already in Use

```bash
# Backend (port 8000)
uvicorn app.main:app --reload --port 8001

# Frontend (port 3000)
npm run dev -- --port 3001
```

### PDF Parsing Issues

```bash
# Install PyMuPDF if PDF parsing fails
pip install PyMuPDF==1.23.26
```

---

## 🤝 Contributing to the Hackathon

### Extend the AI

- Add more domain patterns
- Implement advanced NLP techniques (BERT, GPT)
- Enhance dependency detection algorithms
- Add support for more document formats

### Improve UI/UX

- Add real-time collaboration
- Implement version control for architectures
- Add more visualization options
- Create mobile-responsive design

### Add Integrations

- Export to IaC (Terraform, Kubernetes)
- Generate Docker Compose files
- Create GitHub Actions workflows
- Integrate with Jira/Confluence

---

## 📊 Quality Metrics Explained

- **Scalability (60-95)**: Ability to handle increased load independently
- **Coupling (10-100)**: Lower is better - service interdependence
- **Maintainability (40-95)**: Ease of understanding and modifying
- **Fault Isolation (35-98)**: Failure containment capability

---

## 📜 License

MIT License - Free for hackathon use and beyond!

---

## 🙏 Acknowledgments

Built with open-source technologies:
- spaCy by Explosion AI
- Sentence Transformers by UKPLab
- FastAPI by Sebastián Ramírez
- React by Meta

---

## 🚀 Ready for Production?

ArchAItect is hackathon-ready and extensible for production use!

**Star this project** ⭐ if it helps your hackathon journey!
