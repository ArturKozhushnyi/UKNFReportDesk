# 🏦 UKNF Report Desk

> Comprehensive platform for managing financial reports submitted to the Polish Financial Supervision Authority (Urząd Komisji Nadzoru Finansowego)

[![License: GPL v2](https://img.shields.io/badge/License-GPL%20v2-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.11-blue)](https://www.python.org/)
[![React](https://img.shields.io/badge/React-18.2-blue)](https://react.dev/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.2-blue)](https://www.typescriptlang.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-green)](https://fastapi.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-blue)](https://www.postgresql.org/)

---

## 🚀 Quick Start

```bash
# Clone and start
git clone <repository>
cd UKNFReportDesk
docker-compose up -d

# Access at http://localhost:3000
# Login: admin@example.com / admin
```

**➡️ [Full Quick Start Guide](QUICK_START.md)**

---

## 📋 System Overview

### 🎯 Core Features

- ✅ **Report Management** - Submit, validate, and track financial reports
- ✅ **Communication System** - Multi-party conversations with attachments
- ✅ **User Authentication** - Session-based auth with RBAC
- ✅ **Entity Management** - Banking entity database
- ✅ **File Repository** - Document storage with versioning
- ✅ **Real-Time Dashboard** - Live status updates

### 🏗️ Architecture

**Microservices:** 4 services (3 backend + 1 frontend)  
**Database Tables:** 29 tables  
**API Endpoints:** 60+  
**Total Code:** ~24,000 lines

```
Frontend (React/TS) ─┬─→ Administration Service (FastAPI)
                     ├─→ Auth Service (FastAPI)
                     └─→ Communication Service (FastAPI)
                              ↓
                         PostgreSQL + Redis
```

---

## 🎨 Technology Stack

### Backend

- **FastAPI** - Modern Python web framework
- **SQLAlchemy** - ORM and Core for database
- **PostgreSQL** - Primary database
- **Redis** - Session storage
- **Passlib** - Password hashing
- **HTTPX** - Inter-service communication

### Frontend

- **React 18** - UI framework
- **TypeScript** - Type safety
- **Vite** - Build tool & dev server
- **TanStack Query** - Data fetching
- **Zustand** - State management
- **Tailwind CSS** - Styling
- **React Router 6** - Routing

### Infrastructure

- **Docker** - Containerization
- **Docker Compose** - Multi-container orchestration
- **Nginx** - Reverse proxy & static serving

---

## 📊 Services

| Service | Port | Purpose | Status |
|---------|------|---------|--------|
| **Frontend** | 3000 | React UI | ✅ Ready |
| **Administration** | 8000 | Entity & user management | ✅ Ready |
| **Auth** | 8001 | Authentication | ✅ Ready |
| **Communication** | 8002 | Chat & reporting | ✅ Ready |
| **PostgreSQL** | 5432 | Database | ✅ Ready |
| **Redis** | 6379 | Sessions | ✅ Ready |

---

## 🗂️ Project Structure

```
UKNFReportDesk/
├── frontend/                    # React TypeScript UI
│   ├── src/
│   │   ├── pages/              # Dashboard, Login
│   │   ├── layouts/            # Main layout
│   │   ├── services/           # API clients
│   │   └── stores/             # State management
│   └── Dockerfile
├── administration-service/      # Entity & user management
│   ├── main.py                 # 6 endpoints
│   └── Dockerfile
├── auth-service/               # Authentication
│   ├── main.py                 # 6 endpoints
│   └── Dockerfile
├── comunication/               # Chat & reporting
│   ├── app/
│   │   ├── routers/
│   │   │   └── chat.py         # 32 endpoints
│   │   ├── schemas/
│   │   │   ├── chat.py
│   │   │   └── reporting.py
│   │   └── services/
│   │       └── validator.py
│   └── main.py
├── migrations/                 # Database migrations (12 files)
│   ├── 001_initial_schema.sql
│   ├── 009_chat_schema.sql
│   └── 011_reporting_schema.sql
├── docker-compose.yaml
└── docs/                       # Comprehensive documentation
```

---

## 📚 Documentation

### Main Guides

| Document | Description | Size |
|----------|-------------|------|
| **[QUICK_START.md](QUICK_START.md)** | 5-minute setup guide | Quick reference |
| **[PROJECT_OVERVIEW.md](PROJECT_OVERVIEW.md)** | Complete system overview | 24 KB |
| **[FRONTEND_IMPLEMENTATION.md](FRONTEND_IMPLEMENTATION.md)** | React frontend guide | 18 KB |
| **[MICROSERVICES_ARCHITECTURE.md](MICROSERVICES_ARCHITECTURE.md)** | Architecture details | 25 KB |

### API Documentation

| Document | Description | Size |
|----------|-------------|------|
| **[CHAT_API_DOCUMENTATION.md](CHAT_API_DOCUMENTATION.md)** | Chat API reference | 25 KB |
| **[CHAT_SYSTEM.md](CHAT_SYSTEM.md)** | Chat database schema | 15 KB |

### Implementation Details

| Document | Description |
|----------|-------------|
| **[CHAT_IMPLEMENTATION_SUMMARY.md](CHAT_IMPLEMENTATION_SUMMARY.md)** | Chat implementation |
| **[PESEL_MASKING.md](PESEL_MASKING.md)** | Privacy implementation |

---

## 🎯 Use Cases

### For Banking Entities

1. Submit quarterly/annual reports
2. Track validation status
3. View validation errors
4. Submit corrections
5. Communicate with UKNF staff
6. Receive deadline reminders

### For UKNF Staff

1. Review submitted reports
2. Track validation progress
3. Communicate with entities
4. Manage cases and conversations
5. Generate reminder campaigns
6. Identify non-filers
7. Archive old reports

### For Administrators

1. Manage users and permissions
2. Configure report types
3. Set up reporting periods
4. Monitor system health
5. Generate analytics
6. Manage entity database

---

## 🔐 Security Features

- **Authentication**: Session-based with Redis
- **Authorization**: Role-based access control (RBAC)
- **Password Hashing**: sha256_crypt
- **PESEL Masking**: Privacy-compliant (`*******2345`)
- **Session Expiry**: 24-hour TTL
- **HTTPS Ready**: Nginx SSL configuration available
- **CORS**: Properly configured
- **SQL Injection**: Prevented via SQLAlchemy ORM

---

## 🧪 Testing

### Available Tests

```bash
# Backend tests
python test_auth_service.py
python test_pesel_masking.py
python test_authorization_integration.py

# Frontend tests (when implemented)
cd frontend
npm run test
```

### Test Coverage

- ✅ Authentication flows
- ✅ Authorization checks
- ✅ PESEL masking
- ✅ Password hashing
- ⬜ API endpoint tests
- ⬜ Frontend component tests
- ⬜ E2E tests

---

## 📈 Project Metrics

### Development Progress

**Overall Completion:** ~80%

| Component | Status | Completion |
|-----------|--------|------------|
| Database Schema | ✅ Complete | 100% |
| Backend APIs | 🔄 In Progress | 75% |
| Frontend UI | 🔄 In Progress | 40% |
| Documentation | ✅ Complete | 100% |
| Testing | 🔄 In Progress | 30% |
| Deployment | ✅ Ready | 100% |

### Code Statistics

- **Python**: 4,000+ lines
- **TypeScript/React**: 1,260+ lines  
- **SQL**: 3,500+ lines
- **Documentation**: 15,000+ lines
- **Total**: 24,000+ lines

---

## 🛠️ Development Workflow

### Backend Development

```bash
# Edit Python code
vim comunication/app/routers/chat.py

# Restart service
docker-compose restart communication-service

# View logs
docker-compose logs -f communication-service
```

### Frontend Development

```bash
cd frontend

# Hot reload development
npm run dev

# Changes appear instantly at localhost:3000
```

### Database Changes

```bash
# Create new migration
vim migrations/012_new_feature.sql

# Restart database (applies migrations)
docker-compose restart db

# Or manually apply
docker exec -it local_postgres psql -U myuser -d mydatabase -f /docker-entrypoint-initdb.d/012_new_feature.sql
```

---

## 🌟 Highlights

### What Makes This Special

1. **Production-Ready Architecture**
   - Microservices with clear separation
   - Docker containerization
   - Horizontal scalability

2. **Comprehensive RBAC**
   - Fine-grained permissions
   - Group-based access
   - Resource-level control

3. **Full-Featured Chat System**
   - 32 endpoints
   - Threading support
   - Read receipts
   - Emoji reactions
   - File attachments

4. **Modern Frontend**
   - React 18 with TypeScript
   - Role-based UI
   - Real-time updates
   - Responsive design

5. **Complete Documentation**
   - 15,000+ lines of guides
   - API references
   - Architecture diagrams
   - Quick start guides

---

## 📞 Getting Help

### Documentation

Start with these files:
1. **[QUICK_START.md](QUICK_START.md)** - Get running in 5 minutes
2. **[PROJECT_OVERVIEW.md](PROJECT_OVERVIEW.md)** - Understand the system
3. **[FRONTEND_IMPLEMENTATION.md](FRONTEND_IMPLEMENTATION.md)** - Frontend details

### Interactive API Docs

- Admin Service: http://localhost:8000/docs
- Auth Service: http://localhost:8001/docs
- Communication Service: http://localhost:8002/docs

### Logs

```bash
docker-compose logs -f [service-name]
```

---

## 🤝 Contributing

Contributions welcome! Please:

1. Read documentation
2. Follow existing code patterns
3. Write tests for new features
4. Update documentation
5. Submit pull requests

---

## 📄 License

**GNU General Public License v2.0**

This program is free software; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation; either version 2 of the License, or (at your option) any later version.

See [LICENSE](LICENSE) for full text.

---

## 🎉 Credits

Built for the **Polish Financial Supervision Authority (UKNF)** to modernize the financial reporting process.

**Technologies Used:**
- FastAPI, React, PostgreSQL, Redis, Docker
- SQLAlchemy, TanStack Query, Tailwind CSS
- And many other open-source libraries

---

## 📬 Contact

For questions, issues, or contributions, please open an issue on GitHub or contact the development team.

---

**🚀 Ready to revolutionize financial reporting! 🚀**

