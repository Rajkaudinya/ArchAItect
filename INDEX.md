# 📚 ArchAItect Documentation Index

## 🚀 **START HERE** (Read First!)
1. **[START_HERE.md](START_HERE.md)** 🎯
   - Quick start guide
   - How to run the system (3 methods)
   - Testing checklist
   - Troubleshooting
   - **← BEGIN WITH THIS FILE!**

2. **[FIXES_APPLIED.md](FIXES_APPLIED.md)** ✅
   - What was fixed
   - Why it was fixed
   - How to verify fixes work

## 📖 Core Documentation

### Setup & Running
- **[HOW_TO_RUN.md](HOW_TO_RUN.md)** - Complete setup instructions
- **[setup.ps1](setup.ps1)** - Automated setup script (legacy)
- **[start-all.ps1](start-all.ps1)** ⚡ - **NEW: Start everything with one command**
- **[start-backend.ps1](start-backend.ps1)** - Start backend only
- **[start-frontend.ps1](start-frontend.ps1)** - Start frontend only

### Understanding the System
- **[README.md](README.md)** - Project overview
- **[PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)** - Comprehensive project details
- **[WORKFLOW_GUIDE.md](WORKFLOW_GUIDE.md)** 📊 - **NEW: Visual workflow diagrams**
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - Technical architecture
- **[COMPARISON.md](COMPARISON.md)** - Compare with similar tools
- **[QUICKSTART.md](QUICKSTART.md)** - Quick overview
- **[IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md)** - What's implemented

### Advanced Topics
- **[PRODUCTION_GUIDE.md](PRODUCTION_GUIDE.md)** - Deployment guide (Docker, K8s, Cloud)
- **[HACKATHON_GUIDE.md](HACKATHON_GUIDE.md)** - Hackathon presentation tips

## 🧪 Test Documents (Ready to Upload!)

### 1. Simple Test Case
**[test_requirements_simple.md](test_requirements_simple.md)** ✅
- **Use Case**: Food Delivery Platform
- **Domains**: 7 (User, Restaurant, Order, Payment, Delivery, Notifications, Reviews)
- **Expected Services**: 8-12 microservices
- **Analysis Time**: ~45 seconds
- **Best for**: Quick testing, first-time users

### 2. Complex Test Case
**[ecommerce_requirements.md](ecommerce_requirements.md)** ✅
- **Use Case**: E-Commerce Platform
- **Domains**: 12 (User, Product, Order, Payment, Shipping, Inventory, etc.)
- **Functional Requirements**: 80+
- **Non-Functional Requirements**: 20+
- **Expected Services**: 10-15 microservices
- **Analysis Time**: ~60 seconds
- **Best for**: Comprehensive testing, stress testing

### 3. Your Own Requirements
**[sample_requirements.md](sample_requirements.md)**
- Template for creating custom requirements
- Follow this format for best results

## 🎯 Quick Reference Cards

### Starting the System
```powershell
# EASIEST - Start everything
.\start-all.ps1

# Or start separately:
.\start-backend.ps1   # Terminal 1
.\start-frontend.ps1  # Terminal 2
```

### Testing the System
1. **Open**: http://localhost:3001
2. **Create Project**: Click "New Blueprint"
3. **Upload**: Drag `test_requirements_simple.md`
4. **Wait**: 30-60 seconds
5. **View**: Generated microservices! 🎉

### Verify Backend is Working
```powershell
curl http://localhost:8000/health
# Should return: {"status": "healthy"}
```

### View API Documentation
Open in browser: http://localhost:8000/docs

## 📁 File Structure Reference

```
C:\ArchAItect\
│
├── 📚 Documentation (Read these)
│   ├── START_HERE.md               ← 🎯 START WITH THIS!
│   ├── FIXES_APPLIED.md            ← What was fixed
│   ├── WORKFLOW_GUIDE.md           ← Visual guides
│   ├── HOW_TO_RUN.md               ← Setup instructions
│   ├── PROJECT_SUMMARY.md          ← Project overview
│   ├── PRODUCTION_GUIDE.md         ← Deployment guide
│   ├── README.md
│   ├── QUICKSTART.md
│   ├── ARCHITECTURE.md
│   ├── COMPARISON.md
│   ├── IMPLEMENTATION_SUMMARY.md
│   └── HACKATHON_GUIDE.md
│
├── 🚀 Start Scripts (Run these)
│   ├── start-all.ps1               ← ⚡ EASIEST - Run this!
│   ├── start-backend.ps1           ← Start backend only
│   ├── start-frontend.ps1          ← Start frontend only
│   └── setup.ps1                   ← Legacy setup script
│
├── 🧪 Test Documents (Upload these)
│   ├── test_requirements_simple.md ← ✅ Food Delivery (Quick)
│   ├── ecommerce_requirements.md   ← ✅ E-Commerce (Complex)
│   └── sample_requirements.md      ← Template
│
├── backend/                        ← Backend code
│   ├── app.py                      ← Main entry point (use this!)
│   ├── requirements.txt            ← Python dependencies
│   ├── venv/                       ← Virtual environment
│   ├── data/                       ← Projects & analysis results
│   └── app/
│       ├── main.py                 ← FastAPI app
│       ├── config.py               ← Configuration
│       ├── api/                    ← API endpoints
│       ├── models/                 ← Data models
│       └── services/               ← Business logic
│
└── frontend/                       ← Frontend code
    ├── src/
    │   ├── App.tsx                 ← Main React component
    │   ├── types.ts                ← TypeScript types
    │   └── components/             ← UI components
    ├── package.json                ← Node dependencies
    └── index.html                  ← Entry HTML
```

## 🎓 Learning Path

### For First-Time Users:
1. Read **START_HERE.md** (5 minutes)
2. Run `.\start-all.ps1` (2 minutes)
3. Open http://localhost:3001
4. Upload **test_requirements_simple.md**
5. Explore generated architecture!

### For Developers:
1. Read **PROJECT_SUMMARY.md** (comprehensive overview)
2. Read **ARCHITECTURE.md** (technical details)
3. Read **HOW_TO_RUN.md** (development setup)
4. Explore code in `backend/app/` and `frontend/src/`

### For DevOps/Deployment:
1. Read **PRODUCTION_GUIDE.md** (Docker, K8s, Cloud)
2. Review `backend/app/config.py` (configuration options)
3. Check `.env` file (environment variables)

### For Testing/QA:
1. Read **FIXES_APPLIED.md** (what to test)
2. Read **WORKFLOW_GUIDE.md** (expected behavior)
3. Test with both documents:
   - `test_requirements_simple.md`
   - `ecommerce_requirements.md`

## 🔍 Common Questions

### "How do I start the system?"
→ Run `.\start-all.ps1` OR see **START_HERE.md**

### "Create Workspace button not working?"
→ Check **FIXES_APPLIED.md** - Section "Troubleshooting"

### "What documents can I test with?"
→ Use `test_requirements_simple.md` (simple) or `ecommerce_requirements.md` (complex)

### "How do I deploy to production?"
→ Read **PRODUCTION_GUIDE.md**

### "What APIs are available?"
→ Open http://localhost:8000/docs (after starting backend)

### "How do I add features?"
→ Read **ARCHITECTURE.md** and **PROJECT_SUMMARY.md**

## ✅ Success Checklist

- [ ] Read **START_HERE.md**
- [ ] Run `.\start-all.ps1`
- [ ] Backend running: http://localhost:8000/health
- [ ] Frontend running: http://localhost:3001
- [ ] Created a project
- [ ] Uploaded **test_requirements_simple.md**
- [ ] Saw microservices generated
- [ ] Viewed metrics dashboard
- [ ] Explored topology graph
- [ ] Exported architecture as JSON

## 🆘 Need Help?

### Check these in order:
1. **START_HERE.md** - Quick fixes
2. **FIXES_APPLIED.md** - Known issues and solutions
3. **HOW_TO_RUN.md** - Detailed setup
4. **WORKFLOW_GUIDE.md** - How system should behave
5. Backend logs: `backend/logs/app_*.log`
6. Browser console (F12) - Check for frontend errors

### Common Errors:
- **"Port 8000 already in use"**: Kill existing backend process
- **"spaCy model not found"**: System works without it (fallback mode)
- **"CORS error"**: Check backend allows `http://localhost:3001`
- **"Upload failed"**: Check file size < 10MB, type is .txt/.md/.pdf/.docx

## 📊 Expected Results

### After uploading test_requirements_simple.md:
- ✅ **8-12 microservices** generated
- ✅ **40-80 API endpoints** total
- ✅ **Metrics**: Scalability 75-85%, Coupling 20-30%
- ✅ **Graph**: Shows service dependencies
- ✅ **Details**: Each service has database, APIs, scaling tips

### After uploading ecommerce_requirements.md:
- ✅ **10-15 microservices** generated
- ✅ **60-100 API endpoints** total
- ✅ **Metrics**: Scalability 80-90%, Coupling 15-25%
- ✅ **Complex graph**: More services and dependencies

---

## 🎉 **YOU'RE READY!**

**Quick Start Command:**
```powershell
.\start-all.ps1
```

**Then open**: http://localhost:3001

**Upload**: test_requirements_simple.md

**See the magic!** ✨

---

**Last Updated**: May 28, 2026  
**Status**: ✅ All Systems Ready  
**Version**: 2.0 (Production Ready)
