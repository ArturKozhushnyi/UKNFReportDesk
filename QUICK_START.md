# 🚀 UKNF Report Desk - Quick Start Guide

## Prerequisites

- Docker & Docker Compose
- Node.js 18+ and npm (for frontend development)
- Git

---

## ⚡ 5-Minute Setup

### Option 1: Full Docker (Production-like)

```bash
# 1. Navigate to project
cd UKNFReportDesk

# 2. Start everything
docker-compose up -d

# 3. Wait for services to be ready (~30 seconds)
docker-compose ps

# 4. Access the application
open http://localhost:3000
```

**Login Credentials:**
- Email: `admin@example.com`
- Password: `admin`

**Services Running:**
- Frontend: http://localhost:3000
- Admin API: http://localhost:8000/docs
- Auth API: http://localhost:8001/docs
- Communication API: http://localhost:8002/docs
- PostgreSQL: localhost:5432
- Redis: localhost:6379

---

### Option 2: Development Mode (Frontend Hot Reload)

```bash
# 1. Start backend services only
docker-compose up -d administration-service auth-service communication-service db redis

# 2. Install frontend dependencies
cd frontend
npm install

# 3. Start frontend dev server
npm run dev

# 4. Access the application
open http://localhost:3000
```

**Benefits:**
- Hot Module Replacement (HMR)
- Instant frontend updates
- React DevTools support
- Faster development cycle

---

## 📊 Verify Installation

### Check All Services

```bash
# Service health
curl http://localhost:8000/healthz  # Admin
curl http://localhost:8001/healthz  # Auth
curl http://localhost:8002/healthz  # Communication

# Docker status
docker-compose ps

# Expected output:
# administration-service   Up
# auth-service            Up
# communication-service   Up
# frontend                Up
# local_postgres          Up
# local_redis             Up
```

### Check Database

```bash
# Connect to PostgreSQL
docker exec -it local_postgres psql -U myuser -d mydatabase

# List tables
\dt

# Check migrations
SELECT table_name FROM information_schema.tables 
WHERE table_schema = 'public' 
ORDER BY table_name;

# Exit
\q
```

### Expected Tables

You should see **29 tables**:
- SUBJECTS, USERS, GROUPS, USERS_GROUPS
- RESOURCES, RESOURCES_ALLOW_LIST
- CONVERSATIONS, MESSAGES, etc. (8 chat tables)
- REPORTS, VALIDATION_RUNS, etc. (12 reporting tables)

---

## 🎯 First Steps in the UI

### 1. Login

1. Navigate to http://localhost:3000
2. You'll see the login page
3. Enter credentials:
   - Email: `admin@example.com`
   - Password: `admin`
4. Click "Login"

### 2. Explore Dashboard

After login, you'll see the **Communication Dashboard** with:

- **Top Stats**: Reports, Messages, Cases, Notifications
- **Reports Snapshot**: Status summary and recent reports
- **Messages Overview**: Unread count and quick actions
- **Cases Overview**: Open/pending/resolved counts
- **Notifications**: System alerts
- **File Repository**: Quick search and browse
- **Bulletin Board**: Announcements

### 3. Navigate Modules

Use the left sidebar to explore:

**Communication Module:**
- Reports → Full report registry (placeholder)
- Cases → Case management (placeholder)
- Messages → Message threads (placeholder)
- Announcements → Bulletin board (placeholder)
- Library → File repository (placeholder)

**Auth & Authorization Module:**
- (Staff/Admin only)

**Administrative Module:**
- (Staff/Admin only)

---

## 🔧 Common Tasks

### View API Documentation

Each service has interactive Swagger UI:

- Admin: http://localhost:8000/docs
- Auth: http://localhost:8001/docs
- Communication: http://localhost:8002/docs

Try endpoints directly in the browser!

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f frontend
docker-compose logs -f communication-service
docker-compose logs -f auth-service
```

### Restart Services

```bash
# Restart all
docker-compose restart

# Restart specific service
docker-compose restart frontend
```

### Rebuild After Code Changes

```bash
# Rebuild specific service
docker-compose up -d --build communication-service

# Rebuild all
docker-compose up -d --build
```

### Stop Everything

```bash
docker-compose down

# Remove volumes (deletes database data)
docker-compose down -v
```

---

## 🐛 Troubleshooting

### Frontend Not Loading

**Check:**
1. Is container running? `docker ps | grep frontend`
2. Check logs: `docker-compose logs frontend`
3. Try accessing directly: http://localhost:3000

**Solution:**
```bash
docker-compose restart frontend
```

### Backend API Errors

**Check:**
1. Database connection: `docker-compose logs db | grep error`
2. Service logs: `docker-compose logs communication-service`

**Solution:**
```bash
# Restart services
docker-compose restart

# Or rebuild
docker-compose up -d --build
```

### CORS Issues

**Symptom:** Browser console shows CORS errors

**Solution:**
The nginx.conf already handles CORS. If issues persist:
1. Check Vite proxy config (vite.config.ts)
2. Verify backend ports (8000, 8001, 8002)
3. Restart frontend service

### Database Migration Issues

**Check migrations:**
```bash
docker-compose logs db | grep -i error
```

**Reapply migrations:**
```bash
docker-compose down -v
docker-compose up -d
```

**Note:** This will DELETE all data!

### Port Conflicts

If ports are already in use:

**Edit docker-compose.yaml:**
```yaml
ports:
  - "3001:80"      # Frontend (change 3000 → 3001)
  - "8003:8000"    # Admin (change 8000 → 8003)
```

---

## 📖 Next Steps

### For Developers

1. **Read Documentation**
   - Start with [PROJECT_OVERVIEW.md](PROJECT_OVERVIEW.md)
   - Review [MICROSERVICES_ARCHITECTURE.md](MICROSERVICES_ARCHITECTURE.md)
   - Check [FRONTEND_IMPLEMENTATION.md](FRONTEND_IMPLEMENTATION.md)

2. **Explore Code**
   - Backend: `comunication/app/routers/chat.py`
   - Frontend: `frontend/src/pages/CommunicationDashboard.tsx`
   - API Client: `frontend/src/services/api.ts`

3. **Test APIs**
   - Use Swagger UI at `/docs` endpoints
   - Try creating conversations
   - Test message sending

4. **Customize Frontend**
   - Modify dashboard widgets
   - Add new pages
   - Customize styling

### For End Users

1. **Login** with your credentials
2. **Explore Dashboard** - familiarize with layout
3. **Submit Report** - use "Submit New Report" button
4. **Check Messages** - view unread messages
5. **Browse Library** - access file repository

---

## 🎓 Learning Resources

### React + TypeScript

- [React Docs](https://react.dev)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/)
- [Vite Guide](https://vitejs.dev/guide/)

### TanStack Query

- [Official Docs](https://tanstack.com/query/latest)
- [Video Tutorial](https://www.youtube.com/watch?v=8K1N3fE-cDs)

### Tailwind CSS

- [Official Docs](https://tailwindcss.com/docs)
- [Component Examples](https://tailwindui.com)

### FastAPI

- [Official Docs](https://fastapi.tiangolo.com)
- [SQLAlchemy Core](https://docs.sqlalchemy.org/en/20/core/)

---

## 📞 Support

### Getting Help

1. Check logs: `docker-compose logs [service]`
2. Review documentation in project root
3. Check API docs at `/docs` endpoints
4. Inspect browser console for errors
5. Check GitHub issues (if repository exists)

### Common Questions

**Q: How do I add a new user?**
A: Use Auth Service: `POST /register` or via admin panel

**Q: How do I reset the database?**
A: `docker-compose down -v && docker-compose up -d`

**Q: How do I add a new report type?**
A: Insert into `REPORT_TYPES` table via SQL or API

**Q: How do I change the admin password?**
A: Login and use password change API endpoint

---

## 🎁 Demo Data

### Pre-Seeded Data (from migrations)

**Users:**
- Admin: `admin@example.com` / `admin`

**Subjects:**
- UKNF (Polish Financial Supervision Authority)
- Bank Pekao SA

**Groups:**
- administrator (with all permissions)

**Report Statuses:**
- 8 statuses pre-defined in REPORT_STATUS_DICT

---

## 🚦 System Requirements

### Development

- **OS**: Linux, macOS, Windows (with WSL2)
- **RAM**: 4GB minimum, 8GB recommended
- **Disk**: 5GB free space
- **CPU**: 2+ cores recommended

### Production

- **RAM**: 8GB minimum, 16GB recommended
- **Disk**: 20GB+ for data storage
- **CPU**: 4+ cores
- **Network**: Stable internet connection

---

## ✅ Final Checklist

Before you start developing:

- [ ] Docker and Docker Compose installed
- [ ] Node.js 18+ installed
- [ ] Ports available: 3000, 5432, 6379, 8000-8002
- [ ] All services start successfully
- [ ] Can login to frontend
- [ ] Dashboard loads data
- [ ] API docs accessible

---

## 🎊 You're Ready!

Your UKNF Report Desk is fully set up and running!

**Access Points:**
- 🌐 **Frontend**: http://localhost:3000
- 📊 **Admin API**: http://localhost:8000/docs
- 🔐 **Auth API**: http://localhost:8001/docs
- 💬 **Communication API**: http://localhost:8002/docs

**Login:**
- 📧 Email: admin@example.com
- 🔑 Password: admin

**Happy Coding! 🚀**

---

For detailed documentation, see:
- [PROJECT_OVERVIEW.md](PROJECT_OVERVIEW.md) - Complete system overview
- [FRONTEND_IMPLEMENTATION.md](FRONTEND_IMPLEMENTATION.md) - Frontend details
- [MICROSERVICES_ARCHITECTURE.md](MICROSERVICES_ARCHITECTURE.md) - Architecture guide

