"""
Quick test script to verify ArchAItect setup and functionality
"""
import sys
import os

print("🧪 ArchAItect System Test\n")
print("=" * 60)

# Test 1: Import core dependencies
print("\n1️⃣ Testing Core Dependencies...")
try:
    import fastapi
    print("   ✅ FastAPI:", fastapi.__version__)
except ImportError as e:
    print("   ❌ FastAPI not installed:", e)
    sys.exit(1)

try:
    import uvicorn
    print("   ✅ Uvicorn installed")
except ImportError as e:
    print("   ❌ Uvicorn not installed:", e)
    sys.exit(1)

try:
    from pydantic import BaseModel
    print("   ✅ Pydantic installed")
except ImportError as e:
    print("   ❌ Pydantic not installed:", e)
    sys.exit(1)

# Test 2: Import NLP dependencies
print("\n2️⃣ Testing NLP Dependencies...")
nlp_available = True

try:
    import spacy
    print("   ✅ spaCy:", spacy.__version__)
    
    # Try loading model
    try:
        nlp = spacy.load("en_core_web_sm")
        print("   ✅ spaCy model 'en_core_web_sm' loaded")
    except:
        print("   ⚠️  spaCy model not found. Run: python -m spacy download en_core_web_sm")
        nlp_available = False
except ImportError:
    print("   ⚠️  spaCy not installed. Fallback mode will be used.")
    nlp_available = False

try:
    from sentence_transformers import SentenceTransformer
    print("   ✅ Sentence Transformers installed")
    
    # Test model loading (this will download on first run)
    print("   🔄 Loading embedding model (may take a moment on first run)...")
    model = SentenceTransformer('all-MiniLM-L6-v2')
    print("   ✅ Embedding model loaded successfully")
except ImportError:
    print("   ⚠️  Sentence Transformers not installed. Fallback mode will be used.")
    nlp_available = False
except Exception as e:
    print(f"   ⚠️  Could not load embedding model: {e}")
    nlp_available = False

try:
    import torch
    print("   ✅ PyTorch:", torch.__version__)
except ImportError:
    print("   ⚠️  PyTorch not installed. Fallback mode will be used.")
    nlp_available = False

# Test 3: Import application modules
print("\n3️⃣ Testing Application Modules...")
try:
    from app.services.parser import DocumentParser
    print("   ✅ DocumentParser imported")
except ImportError as e:
    print("   ❌ DocumentParser import failed:", e)
    sys.exit(1)

try:
    from app.services.nlp_engine import NLPEngine
    print("   ✅ NLPEngine imported")
except ImportError as e:
    print("   ❌ NLPEngine import failed:", e)
    sys.exit(1)

try:
    from app.services.analyzer_v2 import get_analyzer
    print("   ✅ Analyzer imported")
except ImportError as e:
    print("   ❌ Analyzer import failed:", e)
    sys.exit(1)

try:
    from app.services.exporter import ArchitectureExporter
    print("   ✅ Exporter imported")
except ImportError as e:
    print("   ❌ Exporter import failed:", e)
    sys.exit(1)

try:
    from app.models.analysis import AnalysisResult
    print("   ✅ Models imported")
except ImportError as e:
    print("   ❌ Models import failed:", e)
    sys.exit(1)

# Test 4: Quick functional test
print("\n4️⃣ Running Functional Test...")
try:
    analyzer = get_analyzer()
    test_req = "Users can login and register. The system processes payments through Stripe."
    
    print("   🔄 Analyzing test requirements...")
    result = analyzer.analyze_requirements(test_req, "test-project", "test.txt", {})
    
    print(f"   ✅ Analysis complete!")
    print(f"      - Services detected: {len(result.microservices)}")
    print(f"      - Dependencies found: {len(result.dependencies)}")
    print(f"      - Scalability score: {result.metrics.scalability}/100")
    
    if len(result.microservices) >= 2:
        print("   ✅ Service detection working correctly")
    else:
        print("   ⚠️  Expected more services to be detected")
        
except Exception as e:
    print(f"   ❌ Functional test failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 5: Export functionality
print("\n5️⃣ Testing Export Functionality...")
try:
    markdown = ArchitectureExporter.to_markdown(result)
    print(f"   ✅ Markdown export: {len(markdown)} chars")
    
    mermaid = ArchitectureExporter.to_mermaid(result)
    print(f"   ✅ Mermaid export: {len(mermaid)} chars")
    
    json_schema = ArchitectureExporter.to_json_schema(result)
    print(f"   ✅ JSON schema export: {len(json_schema)} keys")
    
except Exception as e:
    print(f"   ❌ Export test failed: {e}")
    sys.exit(1)

# Summary
print("\n" + "=" * 60)
print("✅ All Tests Passed!")
print("\nSystem Status:")
print(f"   - Core APIs: ✅ Ready")
print(f"   - NLP Engine: {'✅ Enabled' if nlp_available else '⚠️  Fallback Mode'}")
print(f"   - Export: ✅ Working")

print("\n🚀 ArchAItect is ready to use!")
print("\nNext steps:")
print("   1. Start backend: python run.py")
print("   2. Visit: http://localhost:8000/docs")
print("   3. Start frontend: cd ../frontend && npm run dev")
print("=" * 60)
