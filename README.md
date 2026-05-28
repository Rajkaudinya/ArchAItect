# 🏛️ ArchAItect — AI-Powered Microservice Architecture Generator

ArchAItect is a state-of-the-art solution mapping platform that automatically translates requirements documents (SRS, BRDs, User Stories, and Functional Specs) into scalable microservice topologies, database boundaries, API definitions, and interactive dependency canvases.

---

## 🚀 Quick Start Guide

### 1. 🐍 Booting up the FastAPI Backend
Ensure Python 3.8+ is installed on your system.

```bash
# Navigate to the backend directory
cd backend

# Install python dependencies
pip install -r requirements.txt

# Start the uvicorn development server
python run.py
```
* **Swagger Interactive Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)
* **Root Endpoint**: [http://localhost:8000/](http://localhost:8000/)

---

### 2. ⚛️ Booting up the React + Vite Frontend
Ensure Node.js 18+ is installed.

```bash
# Navigate to the frontend directory
cd frontend

# Install packages
npm install

# Start Vite hot-reloading dev server
npm run dev
```
* **Active Platform Port**: [http://localhost:3000/](http://localhost:3000/)

---

## 📌 Architecture Design System Features

### 1. Ingestion Engine
Handles drag-and-drop parsing of `.txt`, `.md`, `.docx`, and `.pdf` files. Translates natural language nouns and verbs into clean software scopes.

### 2. Microservice Isolation & Bounded Contexts
Applies advanced heuristic pattern parsing of software intent to suggest standalone microservice boundaries, databases (Postgres SQL transactions vs MongoDB NoSQL identity contexts), and circuit breaker patterns.

### 3. SVG Topology Dependency Map
Draggable, visual flow lines mapping REST request routes. Click any card on the topology to modify REST paths, rename contexts, add custom CRUD API definitions, and persist updates.

### 4. Telemetry Index Scoring
Monitors **Scalability**, **Coupling Complexity**, **Maintainability**, and **Fault Isolation** metrics with risk thresholds.
