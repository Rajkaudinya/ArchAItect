# ArchAItect - Complete Setup and Run Guide

This guide provides step-by-step instructions to set up and run both the backend and frontend of the ArchAItect platform.

---

## 📋 Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.9+** (for backend)
- **Node.js 16+** and **npm** (for frontend)
- **Git** (for version control)
- **Code Editor** (VS Code recommended)

---

## 🔧 Backend Setup and Run

### Step 1: Navigate to Backend Directory

```powershell
cd C:\ArchAItect\backend
```

### Step 2: Create Python Virtual Environment

```powershell
# Create virtual environment
python -m venv venv

# Activate virtual environment (PowerShell)
.\venv\Scripts\Activate.ps1

# If you get execution policy error, run:
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned

# For Command Prompt, use:
# venv\Scripts\activate.bat
```

You should see `(venv)` prefix in your terminal prompt indicating the virtual environment is active.

### Step 3: Install Python Dependencies

```powershell
# Upgrade pip to latest version
python -m pip install --upgrade pip

# Install all required packages
pip install -r requirements.txt
```

### Step 4: Download Required NLP Models

The backend uses spaCy for NLP. Download the required model:

```powershell
# Download spaCy English language model
python -m spacy download en_core_web_sm
```
### if it fails run 
```pip install https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-3.7.1/en_core_web_sm-3.7.1-py3-none-any.whl
```

### Step 5: Configure Environment Variables

Ensure your `.env` file exists in the backend directory with the following configuration:

```env
# Groq API Configuration (for advanced AI features)
GROQ_API_KEY=your_groq_api_key_here

# JWT Secret Key
JWT_SECRET=super-secret-key-for-archaitect-development-123456

# Server Configuration
HOST=127.0.0.1
PORT=8000
```

> **Note**: The `.env` file is already configured. If you need a new Groq API key, get one from [https://console.groq.com/](https://console.groq.com/)

### Step 6: Run the Backend Server

```powershell
# Make sure you're in the backend directory with venv activated
python app.py
```

You should see output like:

```
======================================================================
🚀 Starting ArchAItect Core AI Engine Server...
======================================================================
📍 Server Address: http://127.0.0.1:8000
📚 API Documentation: http://127.0.0.1:8000/docs
🔑 Groq API Key: Configured ✓
💾 Data Directory: C:\ArchAItect\backend\data
======================================================================

INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8000
```

### Step 7: Verify Backend is Running

Open your browser and visit:
- **API Root**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs (Interactive Swagger UI)
- **Alternative Docs**: http://localhost:8000/redoc

You should see the API documentation with all available endpoints.

### Backend API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Health check |
| POST | `/api/v1/auth/register` | User registration |
| POST | `/api/v1/auth/login` | User login |
| POST | `/api/v1/projects/create` | Create new project |
| GET | `/api/v1/projects/{project_id}` | Get project details |
| POST | `/api/v1/analysis/upload` | Upload requirements document |
| GET | `/api/v1/analysis/{project_id}` | Get analysis results |
| POST | `/api/v1/analysis/export` | Export architecture (IDL, JSON) |

---

## 🎨 Frontend Setup and Run

### Step 1: Open New Terminal for Frontend

Keep the backend terminal running and open a **new terminal** window.

```powershell
cd C:\ArchAItect\frontend
```

### Step 2: Install Node Dependencies

```powershell
# Install all npm packages
npm install
```

This will install:
- React 18
- TypeScript
- Vite (build tool)
- TailwindCSS
- D3.js (for graph visualization)
- Axios (for API calls)

### Step 3: Run the Frontend Development Server

```powershell
npm run dev
```

You should see output like:

```
  VITE v5.x.x  ready in xxx ms

  ➜  Local:   http://localhost:3001/
  ➜  Network: use --host to expose
  ➜  press h + enter to show help
```

### Step 4: Access the Application

Open your browser and navigate to:

**http://localhost:3001**

You should see the ArchAItect application interface with:
- File upload section
- Microservice architecture canvas
- Metrics dashboard

---

## 🧪 Testing the Complete Workflow

### 1. Register/Login

1. Click "Sign Up" or "Login"
2. Create a test account or use existing credentials

### 2. Create a New Project

1. Click "New Project"
2. Enter project name: `E-Commerce Platform`
3. Click "Create"

### 3. Upload Requirements Document

1. Click "Upload Requirements"
2. Select the `ecommerce_requirements.md` file from the project root
3. Wait for analysis to complete (30-60 seconds)

### 4. View Generated Architecture

You should see:
- **Microservices Graph**: Visual representation of services and their dependencies
- **Service Details**: List of microservices with APIs and endpoints
- **Metrics**: Cohesion, coupling, and complexity scores
- **Traceability Matrix**: Requirements mapped to services

### 5. Export Architecture

1. Click "Export" button
2. Choose format:
   - **JSON**: Full architecture specification
   - **Protobuf IDL**: Service definitions
   - **Mermaid**: Diagram markup
   - **OpenAPI**: API specifications

---

## 🛠️ Troubleshooting

### Backend Issues

#### Issue: `ModuleNotFoundError: No module named 'app'`
**Solution**: Ensure you're in the `backend` directory and virtual environment is activated.

```powershell
cd C:\ArchAItect\backend
.\venv\Scripts\Activate.ps1
```

#### Issue: `spacy model 'en_core_web_sm' not found`
**Solution**: Download the spaCy model:

```powershell
python -m spacy download en_core_web_sm
```

#### Issue: Backend won't start - Port 8000 already in use
**Solution**: Kill the process using port 8000:

```powershell
# Find process using port 8000
netstat -ano | findstr :8000

# Kill the process (replace PID with actual process ID)
taskkill /PID <PID> /F
```

#### Issue: GROQ API errors
**Solution**: The system will work without GROQ API (uses local NLP). To get enhanced AI features, get a free API key from [https://console.groq.com/](https://console.groq.com/)

### Frontend Issues

#### Issue: `npm install` fails
**Solution**: Clear npm cache and retry:

```powershell
npm cache clean --force
npm install
```

#### Issue: Frontend can't connect to backend
**Solution**: 
1. Verify backend is running on http://localhost:8000
2. Check CORS settings in `backend/app/main.py`
3. Ensure no firewall is blocking local connections

#### Issue: Port 3001 already in use
**Solution**: Kill the process or use a different port:

```powershell
# Use different port
npm run dev -- --port 3002
```

---

## 🔄 Daily Development Workflow

### Starting Work

```powershell
# Terminal 1 - Backend
cd C:\ArchAItect\backend
.\venv\Scripts\Activate.ps1
python app.py

# Terminal 2 - Frontend
cd C:\ArchAItect\frontend
npm run dev
```

### Stopping Servers

- Press `Ctrl + C` in each terminal to stop the servers

### Deactivating Virtual Environment

```powershell
# In the backend terminal
deactivate
```

---

## 📦 Production Build

### Backend Production

```powershell
cd C:\ArchAItect\backend
.\venv\Scripts\Activate.ps1

# Run with production settings
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Frontend Production

```powershell
cd C:\ArchAItect\frontend

# Create optimized production build
npm run build

# Preview production build locally
npm run preview
```

The production build will be in `frontend/dist/` directory.

---

## 🐳 Docker Deployment (Optional)

### Backend Dockerfile

Create `backend/Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN python -m spacy download en_core_web_sm

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Frontend Dockerfile

Create `frontend/Dockerfile`:

```dockerfile
FROM node:18-alpine as build

WORKDIR /app

COPY package*.json .
RUN npm install

COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
```

### Docker Compose

Create `docker-compose.yml` in project root:

```yaml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - GROQ_API_KEY=${GROQ_API_KEY}
      - JWT_SECRET=${JWT_SECRET}
    volumes:
      - ./backend/data:/app/data

  frontend:
    build: ./frontend
    ports:
      - "3001:80"
    depends_on:
      - backend
```

Run with:

```powershell
docker-compose up -d
```

---

## 📊 Performance Optimization Tips

### Backend Optimization

1. **Enable Response Caching**: Use Redis for frequent queries
2. **Connection Pooling**: Configure database connection pools
3. **Async Processing**: Use Celery for long-running tasks
4. **Load Balancing**: Use Nginx or AWS ALB for multiple instances

### Frontend Optimization

1. **Code Splitting**: Vite automatically handles this
2. **Lazy Loading**: Import components dynamically
3. **CDN**: Host static assets on CDN
4. **Caching**: Configure proper cache headers

---

## 📚 Additional Resources

- **Backend Documentation**: http://localhost:8000/docs
- **FastAPI Docs**: https://fastapi.tiangolo.com/
- **React Docs**: https://react.dev/
- **Vite Docs**: https://vitejs.dev/
- **TailwindCSS**: https://tailwindcss.com/

---

## 🆘 Getting Help

If you encounter issues:

1. Check this documentation first
2. Review error messages in terminal
3. Check browser console for frontend errors (F12)
4. Verify all prerequisites are installed correctly
5. Ensure ports 8000 and 3001 are available

---

## ✅ Quick Reference Commands

### Backend
```powershell
# Activate environment
cd C:\ArchAItect\backend
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Download NLP model (optional - will auto-download on first use)
python -m spacy download en_core_web_sm

# Run server
python app.py
```

### Frontend
```powershell
# Navigate to frontend
cd C:\ArchAItect\frontend

# Install dependencies
npm install

# Run development server
npm run dev

# Build for production
npm run build
```

---

**Last Updated**: May 28, 2026  
**Version**: 1.0

Happy Architecting! 🚀
