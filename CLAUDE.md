# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

Cookbook is a modern recipe management application with FastAPI backend and React/TypeScript frontend. It supports two deployment modes:

1. **Development Mode (Standalone)**: No authentication, own database, fast local development
2. **Integrated Mode (Subapp)**: Integrates with haochen.lu, shares JWT auth and database

Recipes are stored as Markdown files with YAML frontmatter, providing human-readable and version-controllable recipe storage.

### Deployment Modes

The app uses `APP_MODE` environment variable to switch between modes:

- **Development mode** (`APP_MODE=development`): Default for local development, no authentication required
- **Integrated mode** (`APP_MODE=integrated`): Production deployment as haochen.lu subapp, requires JWT authentication

Key files for dual-mode support:
- `backend/app/config.py`: Mode configuration and settings
- `backend/app/dependencies.py`: Conditional authentication
- `backend/app/database.py`: Schema prefix for integrated mode
- `frontend/src/config.ts`: Frontend mode configuration

See [DEPLOYMENT_MODES.md](DEPLOYMENT_MODES.md) for complete details.

## Development Workflow

### Starting the Development Environment

**ALWAYS use `./dev.sh` for development operations.** The dev.sh script manages Docker containers for the full stack:

```bash
# Primary development workflow
./dev.sh start    # Start all services (backend, frontend, db, redis)
./dev.sh stop     # Stop all services
./dev.sh restart  # Restart all services
./dev.sh logs [service] [-f]  # View logs (optional service name and -f to follow)
```

**Manual Docker commands (if needed):**
```bash
# Start all services
docker compose -f docker-compose.dev.yml up -d

# Stop all services
docker compose -f docker-compose.dev.yml down

# View logs for specific service
docker compose -f docker-compose.dev.yml logs -f backend
docker compose -f docker-compose.dev.yml logs -f frontend
```

**Local development (without Docker):**
```bash
# Backend
cd backend
pip install -e .
alembic upgrade head
uvicorn app.main:app --reload --port 8000

# Frontend
cd frontend
npm install
npm run dev
```

Once started:
- Frontend: http://localhost:3000 (Vite dev server with HMR)
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs (FastAPI auto-generated)
- Database: postgresql://postgres:password@localhost:5432/cookbook
- Redis: redis://localhost:6379/0

### Running Tests and Linting

**Backend testing:**
```bash
./dev.sh test  # Run all tests

# Via Docker (alternative)
docker compose -f docker-compose.dev.yml exec backend python -m pytest
docker compose -f docker-compose.dev.yml exec backend python -m pytest tests/unit/
docker compose -f docker-compose.dev.yml exec backend python -m pytest tests/integration/

# Local
cd backend
pytest
pytest --cov=app tests/
```

**Frontend testing:**
```bash
# Via dev.sh
./dev.sh test

# Manual
cd frontend
npm run test              # Unit tests with Vitest
npm run test:coverage     # Generate coverage report
```

**Backend linting/formatting:**
```bash
./dev.sh lint  # Run all linters

# Manual commands
ruff check --fix --unsafe-fixes --preview
ruff format
mypy app/ tests/
```

**Frontend linting/formatting:**
```bash
cd frontend
npm run lint              # ESLint checking
npm run lint:fix          # ESLint with auto-fix
npm run format            # Prettier formatting
```

**Pre-commit hooks:**
```bash
./dev.sh setup-precommit  # Install pre-commit hooks
./dev.sh precommit        # Run pre-commit manually
```

### Database Migrations

```bash
./dev.sh migrate                    # Apply pending migrations
./dev.sh migration "Add new field"  # Create new migration

# Manual commands
docker compose -f docker-compose.dev.yml exec backend alembic revision --autogenerate -m "description"
docker compose -f docker-compose.dev.yml exec backend alembic upgrade head
docker compose -f docker-compose.dev.yml exec backend alembic history
```

Migrations use Alembic. Files are in `backend/alembic/versions/`.

### Container Access

```bash
./dev.sh shell backend   # Open bash in backend container
./dev.sh shell frontend  # Open bash in frontend container
```

## Architecture

### Backend Structure (`backend/app/`)

```
app/
├── main.py              # FastAPI app, CORS, lifespan, routes
├── config.py            # Pydantic settings from env vars
├── database.py          # SQLAlchemy async engine setup
├── api/
│   └── recipes.py       # All recipe endpoints (CRUD, search, upload, export, editor)
├── crud/
│   └── recipe.py        # Database operations for recipes
├── models/
│   └── recipe.py        # SQLAlchemy Recipe model
├── schemas/
│   ├── recipe.py        # Pydantic request/response models
│   └── recipe_schema.py # JSON Schema for frontmatter validation
├── core/
│   ├── markdown.py      # Parse/generate markdown recipes, validate
│   ├── migration.py     # Django recipe migration utilities
│   └── redis.py         # Redis connection management
└── cli.py               # Typer CLI for migrations and utilities
```

**Key Architectural Patterns:**
- Async-first: All database operations use `AsyncSession`
- FastAPI dependency injection for database sessions (`Depends(get_session)`)
- Pydantic models for validation and serialization
- All imports at top of file (never inline imports)

### Frontend Structure (`frontend/src/`)

```
src/
├── App.tsx              # React Router setup
├── main.tsx             # React entry point
├── components/
│   ├── Layout.tsx       # Header, footer, nav
│   ├── RecipeCard.tsx   # Recipe list item display
│   ├── RecipeEditor.tsx # CodeMirror-based markdown editor
│   └── ...
├── pages/
│   ├── HomePage.tsx     # Featured and recent recipes
│   ├── EditorPage.tsx   # Recipe creation page
│   ├── RecipeListPage.tsx
│   ├── RecipeDetailPage.tsx
│   └── SearchPage.tsx
├── hooks/
│   └── useRecipes.ts    # React Query hooks for API
├── services/
│   └── api.ts           # Axios API client
└── utils/
    └── editorExtensions.ts  # CodeMirror extensions for validation/autocomplete
```

### Docker Build System

The project uses a unified Dockerfile with multi-stage builds:

- `backend/Dockerfile`: Single file for dev and prod via `ARG BUILD_TYPE`
  - `BUILD_TYPE=development`: Includes watchfiles, git, runs with --reload
  - `BUILD_TYPE=production`: Non-root user, no dev tools
- Build context is project root (`.`) to access both `backend/` and `.git/`
- `docker-compose.dev.yml` uses `BUILD_TYPE: development`

### Recipe Format and Validation

Recipes use Markdown with YAML frontmatter:

**Frontmatter Schema** (`backend/app/schemas/recipe_schema.py`):
- Required: `name`
- Enums: `difficulty` (easy/medium/hard)
- Time patterns: `prep_time`, `cook_time` (e.g., "15 minutes", "1 hour 30 minutes")
- Arrays: `tags`, `notes`, `tips`
- Booleans: `public`, `featured`

**Validation Flow:**
1. Client-side: Ajv validates against JSON Schema
2. Server-side: `validate_markdown_recipe()` checks YAML + required fields
3. Parser: `MarkdownRecipeParser.parse_recipe()` converts to `RecipeCreate`

### Live Recipe Editor

The `/editor` page uses CodeMirror 6 with custom extensions:

**Features:**
- YAML frontmatter parsing with syntax highlighting
- Autocomplete for field names (from schema)
- Autocomplete for values (enum + dynamic from API)
- Real-time validation with inline error markers
- Debounced API validation calls

**API Endpoints for Editor:**
- `GET /api/recipes/editor/schema` - JSON Schema + field descriptions
- `GET /api/recipes/editor/autocomplete` - Dynamic cuisines, categories, tags
- `POST /api/recipes/validate` - Server-side validation

## Common Tasks

### Adding a New Recipe Field

1. Update `backend/app/models/recipe.py` (SQLAlchemy model)
2. Create migration: `./dev.sh migration "Add field_name"`
3. Update `backend/app/schemas/recipe.py` (Pydantic models)
4. Update `backend/app/schemas/recipe_schema.py` (JSON Schema)
5. Update `backend/app/core/markdown.py` parser if needed

### Adding a New API Endpoint

Add to `backend/app/api/recipes.py`:
- Use `@router.get/post/put/delete` decorators
- Depend on `db: AsyncSession = Depends(get_session)` for database
- Import CRUD operations from `app.crud.recipe`
- Return Pydantic response models

### Modifying the Editor

Edit `frontend/src/utils/editorExtensions.ts`:
- `createAutocomplete()`: Add new field autocomplete
- `createValidator()`: Add custom validation logic
- `parseFrontmatter()`: Modify YAML parsing if needed

## Deployment

This app is designed to run as a subapp in haochen.lu:
- Backend can mount under `/cookbook` prefix
- Shares parent app's database and Redis
- Frontend served statically or as separate service

## Important Conventions

### Python Code Style
- Always use `from __future__ import annotations`
- All imports at top of file (never inline)
- Type hints required on all functions
- Use `|` for union types
- Prefer `import xxx.yyy` for third-party, `from xxx import yyy` for intra-package
- When running ruff: `ruff check --fix --unsafe-fixes --preview`
- Functional tests (`def test_something`) over class-based tests

### Git Commits
- Simple commit messages (what changed, not why)
- Always ensure pre-commit passes before committing
- Never commit with `--no-verify` unless explicitly requested
- Never use `git commit --amend` unless explicitly requested

### File Operations
- Never create `.md` files unless explicitly required
- Always prefer editing existing files over creating new ones
- Avoid formal/marketing tone in code/docs (no "comprehensive", "key features", etc.)

## Testing the Application

Once dev environment is running (`./dev.sh start`):

```bash
# Test backend endpoints
curl http://localhost:8000/docs  # View OpenAPI docs
curl http://localhost:8000/api/recipes/editor/schema
curl http://localhost:8000/api/recipes/editor/autocomplete

# Access frontend
open http://localhost:3000
open http://localhost:3000/editor  # Test recipe editor

# Run test suites
./dev.sh test
```
