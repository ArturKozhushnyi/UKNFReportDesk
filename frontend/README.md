# UKNF Report Desk - Frontend

Modern React TypeScript frontend for the UKNF Report Desk system.

## Features

- **Role-Based Access Control**: Different views for external users, internal staff, and administrators
- **Module-Based Navigation**: Organized by Communication, Authentication, and Administrative modules
- **Real-Time Updates**: React Query for data synchronization
- **Responsive Design**: Mobile-first with Tailwind CSS
- **Type-Safe**: Full TypeScript implementation

## Architecture

### Tech Stack

- **React 18** - UI framework
- **TypeScript** - Type safety
- **Vite** - Build tool and dev server
- **React Router 6** - Routing with breadcrumbs
- **TanStack Query** - Data fetching and caching
- **Zustand** - State management
- **Tailwind CSS** - Styling
- **Lucide React** - Icons
- **Axios** - HTTP client

### Project Structure

```
frontend/
├── src/
│   ├── components/        # Reusable UI components
│   ├── pages/            # Page components
│   │   ├── CommunicationDashboard.tsx
│   │   └── LoginPage.tsx
│   ├── layouts/          # Layout components
│   │   └── MainLayout.tsx
│   ├── guards/           # Route guards
│   │   └── AuthGuard.tsx
│   ├── services/         # API clients
│   │   └── api.ts
│   ├── stores/           # State management
│   │   └── authStore.ts
│   ├── types/            # TypeScript definitions
│   │   └── index.ts
│   ├── hooks/            # Custom React hooks
│   ├── utils/            # Utility functions
│   ├── styles/           # Global styles
│   │   └── index.css
│   ├── App.tsx           # Main app component
│   └── main.tsx          # Entry point
├── package.json
├── tsconfig.json
├── vite.config.ts
├── tailwind.config.js
└── README.md
```

## Installation

### Prerequisites

- Node.js 18+ and npm/yarn/pnpm
- Backend services running (auth-service, communication-service)

### Setup

```bash
cd frontend

# Install dependencies
npm install

# Or with yarn
yarn install

# Or with pnpm
pnpm install
```

## Development

### Start Dev Server

```bash
npm run dev
```

The application will be available at **http://localhost:3000**

### Environment

The Vite dev server is configured to proxy API requests:
- `/api/*` → `http://localhost:8002` (communication-service)
- `/auth/*` → `http://localhost:8001` (auth-service)

### Build for Production

```bash
npm run build
```

Output will be in `dist/` directory.

### Preview Production Build

```bash
npm run preview
```

## API Integration

### Backend Services

The frontend connects to three microservices:

1. **Auth Service** (port 8001)
   - POST `/auth/authn` - Login
   - POST `/auth/register` - Register
   - POST `/auth/authz` - Check authorization
   - POST `/auth/logout` - Logout

2. **Communication Service** (port 8002)
   - `/api/chat/*` - Chat/messaging endpoints
   - `/api/reporting/*` - Reporting endpoints (when implemented)

3. **Administration Service** (port 8000)
   - `/subjects/*` - Subject/entity management
   - `/users/*` - User management

### API Client (`src/services/api.ts`)

Centralized API client with:
- Axios interceptors for auth tokens
- Automatic token refresh
- Error handling (401 redirects to login)
- Type-safe request/response

**Example Usage:**

```typescript
import { commAPI } from '../services/api';

// Get dashboard stats
const stats = await commAPI.getDashboardStats();

// Get reports
const reports = await commAPI.getReports({
  page: 1,
  page_size: 20,
  status: 'SUCCESS',
});

// Send message
await commAPI.sendMessage(conversationId, {
  sender_user_id: userId,
  body: 'Hello!',
  visibility: 'public',
});
```

## User Roles

### External User
- View own subject's reports
- Send messages
- View public conversations
- Access file library (own files)

### Internal User (UKNF Staff)
- All external user permissions
- View all reports
- Access internal messages
- Manage cases and conversations
- Access authentication module

### Administrator
- Full system access
- User management
- Role and permission management
- Entity database management
- System configuration

## Pages & Routes

### Public Routes
- `/login` - Login page

### Protected Routes
- `/` - Communication Dashboard (home)

### Communication Module
- `/communication` - Module home
- `/communication/reports` - Reports registry
- `/communication/reports/:id` - Report details
- `/communication/cases` - Cases list
- `/communication/messages` - Message threads
- `/communication/announcements` - Announcements
- `/communication/library` - File repository

### Authentication & Authorization Module
- `/auth-module/authentication` - Authentication management
- `/auth-module/requests` - Access requests
- `/auth-module/authorization` - Authorization rules
- `/auth-module/contact` - Contact form

### Administrative Module
- `/admin/users` - User management
- `/admin/password-policy` - Password policy
- `/admin/roles` - Roles & permissions
- `/admin/entities` - Entities database
- `/admin/entity-updater` - Entity data updater

## Components

### Communication Dashboard Widgets

1. **Reports Snapshot**
   - Status summary (accepted, in validation, rejected)
   - Recent reports list
   - Quick links to details

2. **Messages Overview**
   - Unread message count
   - Recent threads
   - Quick compose action

3. **Cases Overview**
   - Open/pending/resolved counts
   - Quick case creation

4. **Notifications Feed**
   - System notifications
   - Alert priorities

5. **File Repository**
   - Quick search
   - Category filters
   - Version indicators
   - Permission badges

6. **Bulletin Board**
   - System announcements
   - Important updates

### Layout Features

- **Main Navigation**: Module-based menu with collapsible sidebar
- **Breadcrumbs**: Dynamic breadcrumb trail
- **User Menu**: Profile and logout
- **Role-Based Visibility**: Menu items filtered by user role

## State Management

### Auth Store (`useAuthStore`)

Zustand store with persistence for:
- User information
- Session ID
- User role
- Authentication status

**Usage:**

```typescript
import { useAuthStore } from '../stores/authStore';

const { user, role, isAuthenticated, login, logout } = useAuthStore();
```

### React Query

Data fetching and caching:
- Automatic background refetch
- Cache invalidation
- Loading and error states
- Optimistic updates

**Usage:**

```typescript
const { data, isLoading, error } = useQuery({
  queryKey: ['dashboard-stats'],
  queryFn: () => commAPI.getDashboardStats(),
});
```

## Styling

### Tailwind CSS

Utility-first CSS framework with custom UKNF theme colors:
- Primary: `uknf-blue` (#003DA5)
- Light: `uknf-blue-light` (#0051C8)
- Dark: `uknf-blue-dark` (#002976)

### Icons

**Lucide React** for consistent iconography:
- FileText, MessageSquare, Users, Shield, Settings
- Semantic and accessible

## Testing

```bash
npm run test
```

Uses Vitest for unit and integration tests.

## Development Tips

### Hot Module Replacement

Vite provides instant HMR for fast development:
- Changes reflect immediately
- State preservation during updates

### Type Checking

```bash
# Run TypeScript compiler
npx tsc --noEmit
```

### Linting

```bash
npm run lint
```

## Backend Connection

### Development Setup

1. Start all backend services:
```bash
cd ..
docker-compose up -d
```

2. Verify services are running:
   - Auth: http://localhost:8001/docs
   - Communication: http://localhost:8002/docs
   - Administration: http://localhost:8000/docs

3. Start frontend:
```bash
cd frontend
npm run dev
```

4. Access application:
   - Frontend: http://localhost:3000
   - Login with: admin@example.com / admin

### Production Deployment

Build the frontend:
```bash
npm run build
```

Serve the `dist/` directory with Nginx, Apache, or any static file server.

**Example Nginx config:**

```nginx
server {
    listen 80;
    server_name uknf-report-desk.local;
    root /var/www/uknf-report-desk/frontend/dist;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location /api {
        proxy_pass http://localhost:8002;
    }

    location /auth {
        proxy_pass http://localhost:8001;
    }
}
```

## Troubleshooting

### CORS Issues

If you encounter CORS errors, ensure backend services have CORS enabled:

```python
# In FastAPI main.py
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### API Connection Issues

Check Vite proxy configuration in `vite.config.ts` and ensure:
- Backend services are running
- Ports match (8001, 8002, 8000)
- Network connectivity

### Build Errors

Clear node_modules and reinstall:
```bash
rm -rf node_modules package-lock.json
npm install
```

## Future Enhancements

- [ ] Real-time notifications (WebSocket)
- [ ] File upload drag-and-drop
- [ ] Advanced filtering and search
- [ ] Export to PDF/Excel
- [ ] Dark mode
- [ ] Multi-language support (Polish/English)
- [ ] Accessibility improvements (WCAG 2.1)
- [ ] Progressive Web App (PWA)
- [ ] End-to-end tests (Playwright/Cypress)

## Related Documentation

- [Microservices Architecture](../MICROSERVICES_ARCHITECTURE.md)
- [Chat API Documentation](../CHAT_API_DOCUMENTATION.md)
- [Backend README](../README.md)

## License

GNU General Public License v2.0 - See LICENSE file in project root.

