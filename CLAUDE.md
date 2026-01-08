# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**PropFair** is a Colombian real estate intelligence platform that aggregates rental listings from Finca Raiz, Metrocuadrado, and Cien Cuadras, enriched with ML-powered fair pricing analysis using XGBoost and SHAP explainability.

**Current Status:** Initial monorepo scaffolding complete. Implementing Slice 1 (Bogotá apartments core loop).

## Repository Structure

This is a **Turborepo monorepo** with pnpm workspaces:

```
/
├── apps/
│   ├── api/          # FastAPI backend (Python 3.12)
│   └── web/          # Next.js 15 frontend (TypeScript)
├── packages/
│   ├── db/           # Prisma schema (PostgreSQL + PostGIS)
│   ├── ml/           # XGBoost models, SHAP (Python 3.12)
│   └── scrapers/     # Scrapy spiders (Python 3.12)
├── infra/
│   └── docker/       # Docker Compose for local development
└── docs/
    └── plans/        # Implementation plans and design docs
```

## Development Commands

### Root-level (Turborepo)

```bash
# Install dependencies
pnpm install

# Start all development servers
pnpm dev

# Build all packages
pnpm build

# Lint all packages
pnpm lint

# Run all tests
pnpm test

# Type check all packages
pnpm typecheck
```

### Backend (apps/api)

```bash
cd apps/api

# Create Python virtual environment
python3.12 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -e ".[dev]"

# Run development server
uvicorn propfair_api.main:app --reload --host 0.0.0.0 --port 8000

# Run tests
pytest

# Run tests with coverage
pytest --cov=src/

# Lint
ruff check .

# Type check
mypy src/
```

### Scrapers (packages/scrapers)

```bash
cd packages/scrapers

# Install dependencies
pip install -e ".[dev]"

# Run Finca Raiz spider
scrapy crawl fincaraiz -o output.json

# Run tests
pytest

# Lint
ruff check .
```

### ML Package (packages/ml)

```bash
cd packages/ml

# Install dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Lint
ruff check .
```

### Frontend (apps/web)

```bash
cd apps/web

# Install dependencies
pnpm install

# Run development server
pnpm dev

# Build for production
pnpm build

# Start production server
pnpm start

# Lint
pnpm lint

# Type check
pnpm typecheck
```

### Database (packages/db)

```bash
cd packages/db

# Generate Prisma client
pnpm db:generate

# Push schema to database
pnpm db:push

# Run migrations
pnpm db:migrate

# Open Prisma Studio
pnpm db:studio
```

### Local Infrastructure

```bash
# Start PostgreSQL + Redis
cd infra/docker
docker-compose up -d

# Stop services
docker-compose down

# View logs
docker-compose logs -f
```

## Architecture Highlights

### Data Flow

1. **Scrapy spiders** fetch listings from Colombian real estate sites
2. **Pipelines** validate, deduplicate, and store in **PostgreSQL + PostGIS**
3. **FastAPI** serves listings via REST API
4. **XGBoost model** predicts fair prices with **SHAP explainability**
5. **Next.js 15** app displays listings with **Deck.gl** interactive maps

### Tech Stack

- **Backend:** FastAPI (async), SQLAlchemy, Pydantic
- **Frontend:** Next.js 15 (App Router), TypeScript, Tailwind CSS, shadcn/ui
- **Map:** Deck.gl, MapLibre GL JS
- **Database:** PostgreSQL 16 + PostGIS extension
- **Cache:** Redis 7
- **ML:** XGBoost, SHAP, pandas, scikit-learn
- **Scraping:** Scrapy, Playwright
- **Auth:** JWT with refresh tokens (planned: Supabase Auth)
- **Build:** Turborepo, pnpm
- **Deployment:** Railway (planned)

### Key Design Patterns

**Vertical Slice Development:**
The project follows vertical slice methodology. See `docs/plans/2026-01-07-slice-1-bogota-apartments.md` for the current implementation plan. Each slice delivers end-to-end functionality.

**Test-Driven Development:**
All implementation tasks follow TDD:
1. Write failing test
2. Verify test fails
3. Implement feature
4. Verify test passes
5. Commit

**Monorepo Package Organization:**
- `apps/` contains deployable applications
- `packages/` contains shared libraries
- Python packages use `pyproject.toml` with `src/` layout
- TypeScript packages use workspace protocol (`workspace:*`)

### Database Schema

See `packages/db/prisma/schema.prisma` for full schema. Key models:

- **Listing:** Core property data (price, beds, baths, location, coordinates)
- **PriceHistory:** Track price changes over time
- **User:** User accounts
- **Favorite:** User-listing bookmarks

Geospatial data uses PostGIS with latitude/longitude fields.

### API Structure

FastAPI uses router-based organization:

```
/api/v1
├── /listings     # Search, get listing details
├── /analysis     # Fair price predictions (ML)
├── /auth         # Login, register, token refresh
└── /user         # Profile, favorites, alerts
```

All endpoints are async. Database sessions use dependency injection.

### Frontend Architecture

Next.js 15 App Router with:
- **Server Components** for static content
- **Client Components** (`"use client"`) for interactive UI
- **API client** in `lib/api.ts` for backend communication
- **shadcn/ui** components in `components/ui/`
- **Map components** in `components/map/` using Deck.gl

### ML Pipeline

1. **Feature Engineering:** `packages/ml/src/propfair_ml/features.py`
2. **Model Training:** `packages/ml/src/propfair_ml/model.py` (XGBoost)
3. **Explainability:** SHAP TreeExplainer for feature importance
4. **Prediction Output:** Fair price estimate + top 5 contributing factors

## Working with Git

This repository uses **git worktrees** for parallel development. Worktrees are stored in `.worktrees/` and excluded from git via `.gitignore`.

When working on implementation plans:
- Check `docs/plans/` for current slice plan
- Use `superpowers:executing-plans` skill when implementing from a plan
- Use `frontend-design` skill for all UI component work

## Environment Variables

Copy `.env.example` to `.env` for local development:

```bash
cp .env.example .env
```

Required for local development:
- `DATABASE_URL` - PostgreSQL connection string
- `REDIS_URL` - Redis connection string
- `NEXT_PUBLIC_API_URL` - Backend API URL (http://localhost:8000)

## Important Notes

### Python Virtual Environments

Each Python package (`apps/api`, `packages/ml`, `packages/scrapers`) should have its own virtual environment when developing locally, though they share dependencies.

### Prisma Client Generation

After modifying `packages/db/prisma/schema.prisma`, always run:
```bash
cd packages/db && pnpm db:generate
```

### Map Tiles

The project uses free CartoDB Positron basemap tiles. No API key required for development.

### Colombian Context

**Estrato (1-6):** Colombian socioeconomic stratification system. Critical feature for ML model as it strongly correlates with pricing.

**Currency:** Colombian Peso (COP). Display prices with proper thousand separators (e.g., $2.500.000).

**Target Sites:**
- Finca Raiz (fincaraiz.com.co) - Largest portal
- Metrocuadrado (metrocuadrado.com)
- Cien Cuadras (ciencuadras.com)

## Design Documents

Full architecture and planning documents:
- **Design Document:** `docs/plans/2026-01-07-propfair-design.md`
- **Slice 1 Plan:** `docs/plans/2026-01-07-slice-1-bogota-apartments.md`

These documents contain detailed technical decisions, feature specifications, and phased implementation strategy.
