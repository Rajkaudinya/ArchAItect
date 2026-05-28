# 🎯 Quick Start Instructions

## For Hackathon Demo

### Option 1: Automated Setup (Recommended)

```powershell
# Run this command from the ArchAItect root directory
.\setup.ps1
```

### Option 2: Manual Quick Start

#### Backend (Terminal 1)
```bash
cd backend
pip install -r requirements.txt
python -m spacy download en_core_web_sm
python test_system.py    # Verify setup
python run.py            # Start server
```

#### Frontend (Terminal 2)
```bash
cd frontend
npm install
npm run dev
```

## Testing the System

### Test with Sample Document

1. Open browser: http://localhost:3000
2. Create new project: "Ride Sharing Demo"
3. Upload: `sample_requirements.md` from root directory
4. Watch AI analyze and generate architecture in ~3 seconds!

### Expected Results

- **Services**: 10-12 microservices identified
- **APIs**: 40+ endpoints generated
- **Dependencies**: ~15-20 connections mapped
- **Metrics**: All scores calculated

### Export Options

Try exporting to different formats:
- **Markdown**: Comprehensive documentation
- **Mermaid**: Visual diagram code
- **JSON**: Structured data for CI/CD

## Troubleshooting

### "Module not found" errors
```bash
cd backend
pip install -r requirements.txt
```

### NLP models not loading
```bash
python -m spacy download en_core_web_sm
```

### Port already in use
```bash
# Backend: Change port in run.py
uvicorn.run("app.main:app", host="0.0.0.0", port=8001)

# Frontend: Change port
npm run dev -- --port 3001
```

## System Verification

Run the test script to verify everything works:
```bash
cd backend
python test_system.py
```

You should see:
```
✅ All Tests Passed!
🚀 ArchAItect is ready to use!
```

## Key Features to Demo

1. **Upload** - Drag and drop any requirements document
2. **AI Analysis** - Watch real-time NLP processing
3. **Interactive Canvas** - Drag services, view connections
4. **Smart Recommendations** - See database types, scaling patterns
5. **Quality Metrics** - Architecture scores with explanations
6. **Export** - Generate documentation in multiple formats

## Tech Stack Highlights

- **Backend**: FastAPI (Python 3.8+)
- **NLP**: spaCy, Sentence Transformers, PyTorch
- **Frontend**: React 18, TypeScript, Vite, Tailwind
- **AI Models**: All open-source, no API keys needed!

## File to Show Judges

- `HACKATHON_GUIDE.md` - Technical deep dive
- `README.md` - Complete documentation
- `sample_requirements.md` - Example input
- `backend/app/services/nlp_engine.py` - AI implementation
- `backend/app/services/analyzer_v2.py` - Core analyzer

## Demo Script (3 minutes)

1. **[30s] Introduction**
   - "ArchAItect turns requirements into microservice architectures using AI"
   
2. **[90s] Live Demo**
   - Upload sample_requirements.md
   - Show generated services
   - Highlight API endpoints
   - Display quality metrics
   - Export to Markdown

3. **[60s] Technical Explanation**
   - spaCy for entity extraction
   - Semantic similarity for clustering
   - Co-occurrence for dependencies
   - All open-source, no vendor lock-in

## Presentation Tips

- **Start with the problem**: "Architects spend hours on this..."
- **Show the speed**: "3 seconds vs 3 hours"
- **Highlight accuracy**: "85% detection rate"
- **Emphasize openness**: "100% open source"
- **Show extensibility**: "Easy to add new domains"

## Contact

Questions during setup? Check:
- README.md (comprehensive docs)
- HACKATHON_GUIDE.md (technical details)
- Code comments (inline documentation)

Good luck! 🚀
