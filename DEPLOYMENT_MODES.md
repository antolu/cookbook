# Deployment Modes: Standalone vs Integrated

Cookbook is designed to work in two modes:
1. **Standalone Mode** - For development and testing
2. **Integrated Mode** - As a subapp within haochen.lu

## Architecture Pattern

```
┌─────────────────────────────────────────────────────────────┐
│ STANDALONE MODE (Development)                                │
│                                                               │
│  Cookbook Frontend (localhost:3000)                          │
│           ↓                                                   │
│  Cookbook Backend (localhost:8000)                           │
│           ↓                                                   │
│  Cookbook DB + Redis                                         │
│                                                               │
│  Auth: Cookbook's own JWT system                             │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ INTEGRATED MODE (Production)                                 │
│                                                               │
│  haochen.lu Frontend (/)                                     │
│       ↓                                                       │
│  nginx Reverse Proxy                                         │
│       ├─→ /cookbook → Cookbook Frontend                      │
│       ├─→ /api/cookbook → Cookbook Backend                   │
│       └─→ / → haochen.lu Backend                             │
│                                                               │
│  Shared Resources:                                            │
│    - PostgreSQL (shared or separate schema)                  │
│    - Redis (different DB numbers)                            │
│    - SECRET_KEY (JWT validation)                             │
│                                                               │
│  Auth: Inherited from haochen.lu                             │
└─────────────────────────────────────────────────────────────┘
```

## Backend Configuration

### Environment Variables

**Standalone (.env):**
```bash
# App settings
ENVIRONMENT=development
APP_MODE=standalone

# Auth - own keys
SECRET_KEY=cookbook-dev-secret-key-change-in-prod
SESSION_SECRET_KEY=cookbook-session-secret

# Database - own database
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/cookbook
REDIS_URL=redis://localhost:6379/0

# CORS - allow frontend
CORS_ORIGINS=http://localhost:3000,http://localhost
```

**Integrated (.env):**
```bash
# App settings
ENVIRONMENT=production
APP_MODE=integrated

# Auth - SHARED with haochen.lu (CRITICAL!)
SECRET_KEY=${HAOCHEN_SECRET_KEY}  # Same as parent!
SESSION_SECRET_KEY=${HAOCHEN_SESSION_SECRET}

# Database - shared or separate schema
DATABASE_URL=postgresql+asyncpg://postgres:password@db:5432/portfolio
# OR with schema:
# DATABASE_URL=postgresql+asyncpg://postgres:password@db:5432/portfolio?options=-csearch_path%3Dcookbook

# Redis - different DB number
REDIS_URL=redis://redis:6379/1  # haochen.lu uses 0

# CORS - parent domain
CORS_ORIGINS=https://haochen.lu,https://www.haochen.lu

# Subapp settings
SUBAPP_PREFIX=/cookbook
API_PREFIX=/api/cookbook
```

### Conditional Auth Setup

**backend/app/config.py:**
```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    environment: str = "development"
    app_mode: str = "standalone"  # or "integrated"

    secret_key: str
    session_secret_key: str

    # Subapp settings (only used in integrated mode)
    subapp_prefix: str = ""
    api_prefix: str = "/api"

    @property
    def is_integrated(self) -> bool:
        return self.app_mode == "integrated"
```

**backend/app/users.py:**
```python
from app.config import settings

# JWT strategy with shared or standalone secret
def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(
        secret=settings.secret_key,  # Same key used by haochen.lu in integrated mode
        lifetime_seconds=3600
    )

# In integrated mode, this validates tokens issued by haochen.lu
# In standalone mode, this validates tokens issued by cookbook
auth_backend = AuthenticationBackend(
    name="jwt",
    transport=bearer_transport,
    get_strategy=get_jwt_strategy,
)
```

**backend/app/dependencies.py:**
```python
from app.config import settings
from app.users import current_active_user, current_superuser

# These work in both modes:
# - Standalone: validates JWT issued by cookbook
# - Integrated: validates JWT issued by haochen.lu (same secret!)
get_current_user = current_active_user
get_current_admin_user = current_superuser

async def get_current_user_optional(
    request: Request,
    db: AsyncSession = Depends(get_session),
) -> User | None:
    """Get current user from JWT token, or None if not authenticated."""
    auth_header = request.headers.get("authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return None

    try:
        token = auth_header.split(" ")[1]
        # Uses settings.secret_key - works for both modes!
        payload = jwt.decode(token, settings.secret_key, algorithms=["HS256"])
        user_id = payload.get("sub")

        # In integrated mode, this fetches user from shared users table
        # In standalone mode, this fetches from cookbook's users table
        return await get_user_by_id(db, user_id)
    except Exception:
        return None
```

## Frontend Configuration

### Environment Variables

**Standalone (.env):**
```bash
VITE_API_URL=http://localhost:8000/api
VITE_APP_MODE=standalone
```

**Integrated (.env.production):**
```bash
VITE_API_URL=/api/cookbook  # Relative to parent domain
VITE_APP_MODE=integrated
VITE_PARENT_AUTH=true  # Use parent's auth store
```

### Conditional Auth Store

**frontend/src/config.ts:**
```typescript
export const config = {
  apiUrl: import.meta.env.VITE_API_URL || 'http://localhost:8000/api',
  appMode: import.meta.env.VITE_APP_MODE || 'standalone',
  isIntegrated: import.meta.env.VITE_APP_MODE === 'integrated',
  useParentAuth: import.meta.env.VITE_PARENT_AUTH === 'true',
}
```

**frontend/src/stores/authStore.ts:**
```typescript
import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import { config } from '../config'

// In integrated mode, try to use parent's auth store
const getAuthStore = () => {
  if (config.isIntegrated && window.parent !== window) {
    // Running in iframe or subapp context
    try {
      // Access parent's auth store
      const parentAuthStore = (window.parent as any).__authStore
      if (parentAuthStore) {
        return parentAuthStore
      }
    } catch (e) {
      console.warn('Cannot access parent auth store, using own')
    }
  }

  // Fallback: use own auth store
  return create<AuthState>()(
    persist(
      (set, get) => ({
        // ... auth store implementation
      }),
      { name: 'cookbook-auth-store' }
    )
  )
}

export const useAuthStore = getAuthStore()
```

**Alternative: Auth Context Provider**
```typescript
// frontend/src/contexts/AuthContext.tsx
import { createContext, useContext, useEffect, useState } from 'react'
import { config } from '../config'

interface AuthContextValue {
  user: User | null
  isAuthenticated: boolean
  isAdmin: boolean
  login: (credentials: any) => Promise<void>
  logout: () => Promise<void>
}

const AuthContext = createContext<AuthContextValue | null>(null)

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [authState, setAuthState] = useState<AuthContextValue>({
    user: null,
    isAuthenticated: false,
    isAdmin: false,
    login: async () => {},
    logout: async () => {},
  })

  useEffect(() => {
    // In integrated mode, listen to parent's auth events
    if (config.isIntegrated) {
      const handleAuthChange = (event: MessageEvent) => {
        if (event.data.type === 'AUTH_CHANGE') {
          setAuthState(event.data.payload)
        }
      }

      window.addEventListener('message', handleAuthChange)

      // Request initial auth state from parent
      window.parent.postMessage({ type: 'REQUEST_AUTH_STATE' }, '*')

      return () => window.removeEventListener('message', handleAuthChange)
    } else {
      // Standalone mode: use own auth store
      const unsubscribe = useAuthStore.subscribe(
        (state) => setAuthState({
          user: state.user,
          isAuthenticated: state.isAuthenticated,
          isAdmin: state.user?.is_admin || false,
          login: state.login,
          logout: state.logout,
        })
      )
      return unsubscribe
    }
  }, [])

  return (
    <AuthContext.Provider value={authState}>
      {children}
    </AuthContext.Provider>
  )
}

export const useAuth = () => {
  const context = useContext(AuthContext)
  if (!context) throw new Error('useAuth must be used within AuthProvider')
  return context
}
```

## Docker Compose

### Standalone (docker-compose.dev.yml)

Already set up - runs everything independently:
- Own PostgreSQL database
- Own Redis instance
- Own auth system
- Accessible at localhost:3000

### Integrated (added to haochen.lu's docker-compose.yml)

```yaml
services:
  # ... existing haochen.lu services

  cookbook-backend:
    image: antonlu/cookbook-backend:latest
    environment:
      - ENVIRONMENT=production
      - APP_MODE=integrated
      - SECRET_KEY=${SECRET_KEY}  # SHARED!
      - SESSION_SECRET_KEY=${SESSION_SECRET_KEY}  # SHARED!
      - DATABASE_URL=postgresql+asyncpg://postgres:${POSTGRES_PASSWORD}@db:5432/portfolio
      - REDIS_URL=redis://redis:6379/1  # Different DB number
      - SUBAPP_PREFIX=/cookbook
      - API_PREFIX=/api/cookbook
      - CORS_ORIGINS=${CORS_ORIGINS}
    depends_on:
      - db
      - redis
    networks:
      - arcadia-network

  cookbook-frontend:
    image: antonlu/cookbook-frontend:latest
    environment:
      - VITE_API_URL=/api/cookbook
      - VITE_APP_MODE=integrated
      - VITE_PARENT_AUTH=true
    depends_on:
      - cookbook-backend
    networks:
      - arcadia-network

  # Update nginx config to proxy /cookbook routes
  nginx:
    volumes:
      - ./nginx/cookbook.conf:/etc/nginx/conf.d/cookbook.conf:ro
```

**nginx/cookbook.conf:**
```nginx
# Cookbook Frontend
location /cookbook {
    proxy_pass http://cookbook-frontend:3000/;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
}

# Cookbook API
location /api/cookbook {
    proxy_pass http://cookbook-backend:8000/api/;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header Authorization $http_authorization;  # Forward JWT token
}
```

## Database Considerations

### Option 1: Shared Database, Separate Tables
- Both apps use `portfolio` database
- Cookbook has its own tables: `recipes`, `cookbook_users` (or reuse `users`)
- Requires coordination on table names

### Option 2: Shared Database, Separate Schema
```sql
-- Create cookbook schema
CREATE SCHEMA cookbook;

-- Cookbook tables live in cookbook schema
CREATE TABLE cookbook.recipes (...);

-- haochen.lu tables live in public schema
CREATE TABLE public.photos (...);
```

```python
# backend/app/database.py
if settings.is_integrated:
    # Use schema prefix in integrated mode
    DATABASE_URL = f"{settings.database_url}?options=-csearch_path%3Dcookbook"
```

### Option 3: Completely Separate Database
- Cookbook: `cookbook` database
- haochen.lu: `portfolio` database
- Simpler, but can't share users table easily

**Recommendation: Option 2 (Separate Schema)** - Clean separation while sharing infrastructure.

## Testing Both Modes

### Test Standalone Mode
```bash
cd cookbook
./dev.sh start
# Visit http://localhost:3000
# Create a recipe with standalone auth
```

### Test Integrated Mode
```bash
cd haochen.lu
# Add cookbook services to docker-compose.yml
docker compose up -d

# Register subapp via admin panel or database:
psql -d portfolio -c "
  INSERT INTO subapps (name, slug, url, icon, color, requires_auth, admin_only)
  VALUES ('Cookbook', 'cookbook', '/cookbook', '🍳', '#FF6B35', false, false);
"

# Visit http://localhost/cookbook
# JWT from haochen.lu login works for cookbook endpoints
```

## Key Takeaways

✅ **Shared SECRET_KEY** - This is what makes integrated mode work
✅ **Conditional Auth** - Use parent's auth in integrated, own in standalone
✅ **Environment-based Config** - APP_MODE determines behavior
✅ **Works Both Ways** - No code changes needed, just environment variables
✅ **Development = Standalone** - Fast iteration without parent app
✅ **Production = Integrated** - Seamless user experience across subapps

---

## Implementation Summary

### What Was Implemented

The dual-mode architecture has been fully implemented with the following changes:

#### Backend Changes

1. **Config System** (`backend/app/config.py`)
   - Added `app_mode` field (development/integrated)
   - Added `subapp_prefix` and `api_prefix` for integrated routing
   - Added `is_integrated` and `is_development` properties

2. **User Model** (`backend/app/models/user.py`)
   - Created fastapi-users compatible User model
   - Shares structure with haochen.lu (UUID-based, email, username, is_superuser, is_admin)
   - Uses same table name (`users`) for schema sharing

3. **Authentication** (`backend/app/users.py` and `backend/app/dependencies.py`)
   - JWT strategy with configurable SECRET_KEY
   - `get_current_user_optional()`: Returns None in dev, validates JWT in integrated
   - `get_current_user()`: Raises 401 in dev, requires auth in integrated
   - `get_current_admin_user()`: Checks is_superuser/is_admin

4. **Recipe Model** (`backend/app/models/recipe.py`)
   - Added `author_id` field (UUID, nullable, foreign key to users.id)
   - SET NULL on delete to preserve recipes if user deleted

5. **Recipe API** (`backend/app/api/recipes.py`)
   - **Development mode**: All operations allowed without authentication
   - **Integrated mode**: Create/update/delete require authentication
   - Author ownership checks: Users can only modify their own recipes (or admins)
   - `author_id` automatically set from authenticated user

6. **Database** (`backend/app/database.py`)
   - Automatic schema prefix in integrated mode: `?options=-csearch_path%3Dcookbook`
   - No changes needed for development mode

7. **Main App** (`backend/app/main.py`)
   - API routes use `api_prefix` from settings (defaults to `/api`)

8. **Migration**
   - Created migration `b187b6d002ed` adding:
     - `users` table with all fastapi-users fields
     - `author_id` column to recipes table
     - Foreign key constraint

#### Frontend Changes

1. **Config** (`frontend/src/config.ts`)
   - Centralized configuration with `appMode`, `isIntegrated`, `isDevelopment`
   - Reads from `VITE_APP_MODE` environment variable

2. **API Client** (`frontend/src/services/api.ts`)
   - Conditional JWT token injection (integrated mode only)
   - Graceful 401 handling (redirect to login in integrated, log in dev)

#### Configuration Files

1. **Environment** (`.env.example`)
   - Comprehensive examples for both modes
   - Clear comments on which settings apply to which mode
   - Integration examples with haochen.lu

2. **Docker Compose** (`docker-compose.dev.yml`)
   - Added `APP_MODE=development` environment variable
   - Added `API_PREFIX=/api` environment variable

### Testing

Development mode tested and working:
- Recipe creation without authentication: ✅
- Recipe listing: ✅
- No author_id field in development mode: ✅

### Integration with haochen.lu

To integrate Cookbook into haochen.lu:

1. **Environment Variables**:
   ```bash
   APP_MODE=integrated
   SECRET_KEY=${HAOCHEN_SECRET_KEY}  # MUST match!
   SESSION_SECRET_KEY=${HAOCHEN_SESSION_SECRET}
   DATABASE_URL=postgresql+asyncpg://postgres:password@db:5432/portfolio?options=-csearch_path%3Dcookbook
   REDIS_URL=redis://redis:6379/1  # Different DB number
   API_PREFIX=/api/cookbook
   SUBAPP_PREFIX=/cookbook
   ```

2. **Database Setup**:
   ```sql
   -- Create cookbook schema in haochen.lu database
   CREATE SCHEMA cookbook;

   -- Run migrations in cookbook schema
   -- The schema prefix is automatically added by database.py
   ```

3. **Nginx Configuration**:
   ```nginx
   # Cookbook API
   location /api/cookbook {
       proxy_pass http://cookbook-backend:8000/api/;
       proxy_set_header Authorization $http_authorization;
   }

   # Cookbook Frontend
   location /cookbook {
       proxy_pass http://cookbook-frontend:3000/;
   }
   ```

4. **SubApp Registration**:
   ```sql
   INSERT INTO subapps (name, slug, url, icon, color, requires_auth, admin_only)
   VALUES ('Cookbook', 'cookbook', '/cookbook', '🍳', '#FF6B35', false, false);
   ```

### Architecture Benefits

- **Zero Code Duplication**: Same codebase works in both modes
- **Local Development**: No dependency on parent app
- **Gradual Migration**: Can deploy standalone first, integrate later
- **Isolated Testing**: Development mode fully functional without auth complexity
