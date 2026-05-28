# 📊 ArchAItect System Workflow - Visual Guide

## 🎯 Complete User Journey

```
┌─────────────────────────────────────────────────────────────────┐
│                    USER OPENS BROWSER                           │
│                  http://localhost:3001                          │
└──────────────────────┬──────────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────────┐
│            STEP 1: CREATE PROJECT (WORKSPACE)                   │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  1. Click "New Blueprint" or "Launch Design Blueprint"   │  │
│  │  2. Enter Project Name: "Food Delivery Platform"         │  │
│  │  3. Enter Description (optional)                         │  │
│  │  4. Click "Create Workspace"                             │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
│  Frontend Request:                                              │
│  POST /api/v1/projects                                          │
│  {                                                              │
│    "name": "Food Delivery Platform",                           │
│    "description": "Test project"                               │
│  }                                                              │
│                                                                 │
│  Backend Response:                                              │
│  {                                                              │
│    "id": "project-abc123xyz",                                  │
│    "name": "Food Delivery Platform",                           │
│    "description": "Test project",                              │
│    "created_at": "2026-05-28T12:34:56",                        │
│    "updated_at": "2026-05-28T12:34:56",                        │
│    "version": 1                                                │
│  }                                                              │
└──────────────────────┬──────────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────────┐
│        STEP 2: UPLOAD REQUIREMENTS DOCUMENT                     │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  1. Drag & drop test_requirements_simple.md              │  │
│  │     OR click upload area and select file                 │  │
│  │  2. See "Uploading..." progress indicator                │  │
│  │  3. Wait 30-60 seconds for analysis                      │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
│  Frontend Request:                                              │
│  POST /api/v1/analysis/upload                                   │
│  Content-Type: multipart/form-data                              │
│  - project_id: "project-abc123xyz"                             │
│  - file: [test_requirements_simple.md binary data]             │
│                                                                 │
│  Backend Processing:                                            │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │  1. Validate file (size < 10MB, allowed type)           │  │
│  │  2. Parse document (extract text, structure)            │  │
│  │  3. Run NLP analysis:                                    │  │
│  │     - Extract entities (User, Order, Payment, etc.)     │  │
│  │     - Extract actions (create, update, delete, etc.)    │  │
│  │     - Extract concepts (authentication, payment, etc.)  │  │
│  │  4. Identify domains (User Management, Order, etc.)     │  │
│  │  5. Generate microservices:                             │  │
│  │     - Service name, description                         │  │
│  │     - Recommended database                              │  │
│  │     - REST API endpoints (5-10 per service)             │  │
│  │     - Scaling recommendations                           │  │
│  │  6. Analyze dependencies between services               │  │
│  │  7. Calculate metrics (cohesion, coupling, etc.)        │  │
│  │  8. Save analysis to data/analysis_project-abc123xyz.json│ │
│  └─────────────────────────────────────────────────────────┘  │
│                                                                 │
│  Backend Response:                                              │
│  {                                                              │
│    "project_id": "project-abc123xyz",                          │
│    "raw_filename": "test_requirements_simple.md",              │
│    "raw_content_preview": "# Food Delivery Platform...",       │
│    "microservices": [                                          │
│      {                                                         │
│        "id": "identity-service",                               │
│        "name": "Identity Service",                             │
│        "description": "Manages user authentication...",        │
│        "domain": "User Management & Authentication",           │
│        "database": "PostgreSQL",                               │
│        "database_reasoning": "ACID compliance needed...",      │
│        "apis": [                                               │
│          {                                                     │
│            "path": "/api/v1/auth/register",                    │
│            "method": "POST",                                   │
│            "description": "Register new user"                  │
│          },                                                    │
│          ...more APIs...                                       │
│        ],                                                      │
│        "scaling_recommendations": [                            │
│          "Implement horizontal scaling",                       │
│          "Use Redis for session caching"                       │
│        ]                                                       │
│      },                                                        │
│      ...more services (8-12 total)...                          │
│    ],                                                          │
│    "dependencies": [                                           │
│      {                                                         │
│        "source": "order-management-service",                   │
│        "target": "identity-service",                           │
│        "type": "sync",                                         │
│        "description": "Validate user authentication"           │
│      },                                                        │
│      ...more dependencies...                                   │
│    ],                                                          │
│    "metrics": {                                                │
│      "scalability": 82.5,                                      │
│      "coupling": 25.3,                                         │
│      "maintainability": 78.9,                                  │
│      "fault_isolation": 81.2                                   │
│    },                                                          │
│    "raw_feedback": ""                                          │
│  }                                                              │
└──────────────────────┬──────────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────────┐
│          STEP 3: VIEW GENERATED ARCHITECTURE                    │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                     METRICS DASHBOARD                    │  │
│  │  ┌────────────┬────────────┬────────────┬────────────┐  │  │
│  │  │Scalability │  Coupling  │Maintain-   │   Fault    │  │  │
│  │  │   82.5%    │   25.3%    │ability     │ Isolation  │  │  │
│  │  │            │            │  78.9%     │   81.2%    │  │  │
│  │  └────────────┴────────────┴────────────┴────────────┘  │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              INTERACTIVE TOPOLOGY GRAPH                  │  │
│  │                                                          │  │
│  │     ┌────────────┐         ┌────────────┐              │  │
│  │     │ Identity   │────────▶│   Order    │              │  │
│  │     │  Service   │         │ Management │              │  │
│  │     └────────────┘         └────────────┘              │  │
│  │            │                     │                      │  │
│  │            │                     │                      │  │
│  │            ▼                     ▼                      │  │
│  │     ┌────────────┐         ┌────────────┐              │  │
│  │     │ Notific-   │         │  Payment   │              │  │
│  │     │   ation    │         │  Service   │              │  │
│  │     └────────────┘         └────────────┘              │  │
│  │                                                          │  │
│  │  [Click any service to see details]                     │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │           MICROSERVICE DETAILS (Click to View)          │  │
│  │                                                          │  │
│  │  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │  │
│  │  📦 Identity Service                                     │  │
│  │  Domain: User Management & Authentication               │  │
│  │  Database: PostgreSQL (ACID compliance needed)          │  │
│  │  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │  │
│  │                                                          │  │
│  │  🔌 APIs:                                                │  │
│  │   • POST   /api/v1/auth/register    Register user       │  │
│  │   • POST   /api/v1/auth/login       User login          │  │
│  │   • POST   /api/v1/auth/logout      User logout         │  │
│  │   • GET    /api/v1/users/{id}       Get user details    │  │
│  │   • PUT    /api/v1/users/{id}       Update profile      │  │
│  │   • POST   /api/v1/auth/refresh     Refresh JWT token   │  │
│  │   • POST   /api/v1/auth/reset       Reset password      │  │
│  │                                                          │  │
│  │  📈 Scaling Recommendations:                            │  │
│  │   • Implement horizontal scaling for auth endpoints     │  │
│  │   • Use Redis for session caching                       │  │
│  │   • Implement rate limiting for login attempts          │  │
│  │  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │  │
│  └──────────────────────────────────────────────────────────┘  │
└──────────────────────┬──────────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────────┐
│               STEP 4: EXPORT ARCHITECTURE                       │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Click "Export" button - Choose format:                 │  │
│  │  • JSON - Complete architecture specification           │  │
│  │  • Protobuf - Service definitions                       │  │
│  │  • OpenAPI - API documentation                          │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
│  Frontend Request:                                              │
│  POST /api/v1/analysis/export                                   │
│  {                                                              │
│    "project_id": "project-abc123xyz",                          │
│    "format": "json"                                            │
│  }                                                              │
│                                                                 │
│  Backend Response:                                              │
│  Downloads file: architecture_food-delivery-platform.json       │
└─────────────────────────────────────────────────────────────────┘

## 🔄 API Flow Sequence

### 1. Create Project
```
Frontend          Backend           Database
   │                 │                 │
   │─POST /projects─▶│                 │
   │  {name, desc}   │                 │
   │                 │──Save project──▶│
   │                 │                 │
   │                 │◀────Success────│
   │◀──Project obj──│                 │
   │  {id, name...}  │                 │
```

### 2. Upload & Analyze
```
Frontend          Backend           NLP Engine       Database
   │                 │                 │                 │
   │─POST /upload───▶│                 │                 │
   │  {file data}    │                 │                 │
   │                 │──Parse doc─────▶│                 │
   │                 │                 │                 │
   │                 │◀──Entities──────│                 │
   │                 │  Actions, etc.  │                 │
   │                 │                 │                 │
   │                 │──Generate───────┤                 │
   │                 │  microservices  │                 │
   │                 │                 │                 │
   │                 │──Save analysis─────────────────▶│
   │                 │                 │                 │
   │◀──Analysis─────│                 │                 │
   │  result JSON    │                 │                 │
```

### 3. Get Analysis
```
Frontend          Backend           Database
   │                 │                 │
   │─GET /analysis──▶│                 │
   │  /{project_id}  │                 │
   │                 │──Load analysis─▶│
   │                 │                 │
   │                 │◀──JSON file────│
   │◀──Full result──│                 │
   │  with services  │                 │
```

## 📁 File Locations

### Backend Files Created:
```
backend/data/
├── projects.json                              # All projects
└── analysis_project-abc123xyz.json            # Analysis result
```

### Log Files:
```
backend/logs/
└── app_2026-05-28.log                        # Daily logs
```

## 🎨 UI Components

### Main Dashboard
- **Header**: Project name, Export button
- **Sidebar**: Project list, New Blueprint button
- **Main Area**: 
  - File Upload panel (drag & drop)
  - Metrics dashboard (4 cards)
  - Topology graph (D3.js visualization)
  - Service details (expandable cards)

### Color Coding
- 🟢 **Green**: High scalability, good scores
- 🟡 **Yellow**: Medium coupling (20-40%)
- 🔴 **Red**: High coupling (>40%), errors
- 🔵 **Blue**: Primary actions, links
- ⚪ **Gray**: Neutral, disabled states

## ⚡ Performance Notes

### Backend:
- **Response Time**: < 200ms for health checks
- **Analysis Time**: 30-60 seconds for typical documents
- **File Size Limit**: 10MB per upload
- **Concurrent Requests**: Supports multiple projects

### Frontend:
- **Load Time**: < 2 seconds on localhost
- **Graph Rendering**: Instant for < 20 services
- **Real-time Updates**: WebSocket ready (future enhancement)

## 🔐 Security Features

### Implemented:
- ✅ File size validation (10MB limit)
- ✅ File type validation (.txt, .md, .pdf, .docx only)
- ✅ Input sanitization (project names, descriptions)
- ✅ CORS configured for localhost:3001
- ✅ Request timeout protection (30 seconds)
- ✅ Global exception handling

### Future Enhancements:
- 🔜 Authentication (JWT)
- 🔜 Rate limiting (60 requests/minute)
- 🔜 File content scanning
- 🔜 SQL injection protection
- 🔜 XSS prevention

## 📊 Sample Output

### For test_requirements_simple.md:
**Expected Services**: 8-12
**Expected APIs**: 40-80 endpoints total
**Analysis Time**: ~45 seconds
**Metrics**: 
- Scalability: 75-85%
- Coupling: 20-30%
- Maintainability: 70-80%
- Fault Isolation: 75-85%

### For ecommerce_requirements.md:
**Expected Services**: 10-15
**Expected APIs**: 60-100 endpoints total
**Analysis Time**: ~60 seconds
**Metrics**: 
- Scalability: 80-90%
- Coupling: 15-25%
- Maintainability: 75-85%
- Fault Isolation: 80-90%

---

**Ready to test?** Run `.\start-all.ps1` and follow the steps above! 🚀
