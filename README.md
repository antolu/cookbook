# Cookbook - Modern Recipe Management System

A modernized recipe management application built with FastAPI backend and React frontend, designed as a subapp for the haochen.lu portfolio ecosystem.

## Features

- 🍳 **Recipe Management**: Create, edit, and organize recipes with rich metadata
- 📝 **Markdown Format**: Recipes stored as structured Markdown with YAML frontmatter
- 🔍 **Advanced Search**: Filter by cuisine, difficulty, cooking time, ingredients
- 📱 **Responsive Design**: Modern React frontend with Tailwind CSS
- 🐳 **Containerized**: Docker development and production environments
 - 🔄 Legacy import utilities removed (legacy formats are not supported)
- 📊 **Rich Metadata**: Prep time, cook time, difficulty, tags, and more

## Tech Stack

### Backend
- **FastAPI** - Modern async Python web framework
- **SQLAlchemy** - Async ORM with PostgreSQL
- **Alembic** - Database migrations
- **Redis** - Caching and session storage
- **Python 3.11+** - Latest Python features

### Frontend
- **React 18** - Modern React with hooks
- **TypeScript** - Type-safe JavaScript
- **Vite** - Fast build tool and dev server
- **Tailwind CSS** - Utility-first CSS framework
- **React Query** - Server state management

### Development
- **Docker** - Containerized development and deployment
- **ruff** - Fast Python linter and formatter
- **Vitest** - Fast unit testing for frontend
- **pytest** - Python testing framework

## Quick Start

### Prerequisites
- Docker and Docker Compose
- Node.js 18+ (for local frontend development)
- Python 3.11+ (for local backend development)

### Development Environment

1. **Clone and setup**:
   ```bash
   git clone <repository-url>
   cd cookbook
   cp .env.example .env
   ```

2. **Start development environment**:
   ```bash
   ./dev.sh start
   ```

    This will start:
    - Frontend (proxied via nginx): http://localhost:6002
    - Backend API (proxied at /api): http://localhost:6002/api
    - API Documentation: http://localhost:6002/api/docs
    - Database: PostgreSQL on host port 5436 (dev compose)
    - Redis: Redis on port 6379

3. **Run database migrations**:
   ```bash
   ./dev.sh migrate
   ```

4. **View logs**:
   ```bash
   ./dev.sh logs          # All services
   ./dev.sh logs backend  # Backend only
   ./dev.sh logs frontend # Frontend only
   ```

5. **Stop environment**:
   ```bash
   ./dev.sh stop
   ```

### Other Development Commands

```bash
# Run tests
./dev.sh test

# Run linting and formatting
./dev.sh lint

# Build frontend for production
./dev.sh build

# Open shell in containers
./dev.sh shell backend
./dev.sh shell frontend

# Create database migration
./dev.sh migration "Add new recipe fields"
```

## Recipe Format

Recipes are stored as Markdown files with YAML frontmatter:

```markdown
---
name: "Chocolate Chip Cookies"
description: "Classic crispy-chewy chocolate chip cookies"
servings: "24 cookies"
prep_time: "15 minutes"
cook_time: "12 minutes"
temperature: 375
difficulty: "easy"
category: "dessert"
cuisine: "american"
tags: ["cookies", "baking", "chocolate"]
notes: ["Store in airtight container"]
tips: ["For chewier cookies, slightly underbake"]
public: true
featured: false
---

## Description

Classic chocolate chip cookies that are crispy on the outside...

## Ingredients

- 2¼ cups all-purpose flour
- 1 tsp baking soda
- 1 cup butter, softened
- ¾ cup granulated sugar
- 2 cups chocolate chips

## Instructions

1. Preheat oven to 375°F (190°C).
2. Mix flour and baking soda in a bowl.
3. Cream butter and sugars until light and fluffy.
4. Beat in eggs and vanilla.
5. Gradually add flour mixture.
6. Stir in chocolate chips.
7. Bake 9-11 minutes until golden brown.

## Notes

- For chewier cookies, slightly underbake
- Store in airtight container for up to 1 week
```

## Legacy data imports

Legacy import utilities have been removed from the main codebase. If you need
to convert old data, create a small one‑off script that exports the legacy
data to the Markdown/frontmatter format used by this project and import it
separately. This keeps the runtime focused on the current app and avoids
shipping legacy compatibility code.

## API Usage

The FastAPI backend provides a RESTful API:

### Recipe Endpoints

```bash
# Get all recipes
GET /api/recipes/

# Search recipes
GET /api/recipes/search?q=chocolate&difficulty=easy

# Get single recipe
GET /api/recipes/{id_or_slug}

# Create recipe (admin)
POST /api/recipes/

# Update recipe (admin)
PUT /api/recipes/{id}

# Delete recipe (admin)
DELETE /api/recipes/{id}

# Upload recipe file
POST /api/recipes/upload

# Export recipe
GET /api/recipes/{id}/export/markdown
GET /api/recipes/{id}/export/json
```

### Metadata Endpoints

```bash
# Get categories
GET /api/recipes/categories

# Get cuisines
GET /api/recipes/cuisines

# Get tags
GET /api/recipes/tags

# Get featured recipes
GET /api/recipes/featured

# Get recent recipes
GET /api/recipes/recent
```

## Deployment

Cookbook supports two deployment modes:

### Development Mode (Standalone)
- No authentication required
- Own database and Redis instance
- Fast local development
- Default mode when using `./dev.sh start`

### Integrated Mode (Subapp in haochen.lu)
- Shares JWT authentication with parent app
- Uses parent's database (separate `cookbook` schema)
- Recipe creation/editing requires authentication
- Users can only edit their own recipes (or admins can edit all)

See [DEPLOYMENT_MODES.md](DEPLOYMENT_MODES.md) for complete integration guide.

### Quick Integration into haochen.lu

1. **Environment Configuration**:
   ```bash
   APP_MODE=integrated
   SECRET_KEY=${HAOCHEN_SECRET_KEY}  # Must match parent!
   DATABASE_URL=postgresql+asyncpg://postgres:password@db:5432/portfolio?options=-csearch_path%3Dcookbook
   REDIS_URL=redis://redis:6379/1
   API_PREFIX=/api/cookbook
   ```

2. **Database Setup**:
   ```sql
   CREATE SCHEMA cookbook;
   ```

3. **Register as subapp**:
   ```sql
   INSERT INTO subapps (name, slug, url, icon, color, requires_auth, admin_only)
   VALUES ('Cookbook', 'cookbook', '/cookbook', '🍳', '#FF6B35', false, false);
   ```

## Configuration

### Environment Variables

Create a `.env` file with:

```bash
# Environment
ENVIRONMENT=development

# Database
POSTGRES_DB=cookbook
POSTGRES_USER=postgres
POSTGRES_PASSWORD=password

# Security
SECRET_KEY=your-secret-key
SESSION_SECRET_KEY=your-session-secret
ADMIN_PASSWORD=admin

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost

# File uploads
MAX_FILE_SIZE=52428800  # 50MB
```

## Contributing

1. **Code Style**: Uses ruff for Python, ESLint for TypeScript
2. **Type Safety**: Full type hints in Python, TypeScript frontend
3. **Testing**: pytest for backend, Vitest for frontend
4. **Commits**: Conventional commits preferred

### Development Workflow

```bash
# Setup development environment
./dev.sh start

# Make changes and test
./dev.sh test
./dev.sh lint

# Create migration if models changed
./dev.sh migration "Describe changes"

# Test in production mode
./dev.sh prod
```

## License

MIT License - see LICENSE file for details.

## Architecture

This cookbook application follows modern development practices:

- **Async-first**: FastAPI with async/await throughout
- **Type-safe**: Full TypeScript frontend, Python type hints
- **Container-native**: Docker for development and production
- **API-driven**: Clean separation between backend and frontend
- **Markdown-based**: Human-readable recipe format
- **Search-optimized**: Full-text search with PostgreSQL
- **Mobile-friendly**: Responsive design with Tailwind CSS

The application is designed to integrate seamlessly with the haochen.lu portfolio as a subapp, sharing authentication and database infrastructure while maintaining its own focused functionality.
