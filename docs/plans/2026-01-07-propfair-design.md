# PropFair - Colombian Real Estate Intelligence Platform

## Design Document

**Date:** 2026-01-07
**Status:** Approved

---

## 1. Vision & Value Proposition

**PropFair** is a Colombian real estate intelligence platform that aggregates rental listings from Finca Raiz, Metrocuadrado, and Cien Cuadras, enriched with ML-powered fair pricing analysis.

**Core Value:** Users don't just find rentals - they understand if they're getting a fair deal and *why*, through explainable AI that shows comparable properties, neighborhood trends, and price drivers.

**User Journey:**
1. Browse/search listings via map or filters (free)
2. See basic listing info and location (free)
3. Unlock detailed fair-price analysis with explainability (premium)
4. Save favorites, set alerts, share via WhatsApp (account required)
5. Receive notifications when prices drop or new matches appear

**Business Model:**
- Free tier: Full browsing, basic map, listing details
- Premium tier: ML price analysis, explainability ("why is this overpriced?"), neighborhood intelligence heat maps, priority alerts

**Portfolio Showcase:**
- Data engineering: Near real-time distributed scraping, ETL pipelines
- ML/AI: Ensemble models with SHAP explainability
- Full-stack: Modern Next.js 16 PWA with rich map interactions
- Product thinking: Freemium model, multi-channel notifications, ops dashboard

---

## 2. High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              CLIENTS                                        │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │   Next.js   │  │     PWA     │  │   Admin     │  │  WhatsApp   │        │
│  │   Web App   │  │   Mobile    │  │  Dashboard  │  │    Bot      │        │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘        │
└─────────┼────────────────┼────────────────┼────────────────┼────────────────┘
          │                │                │                │
          └────────────────┴────────────────┴────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           API GATEWAY (FastAPI)                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │  Listings   │  │     ML      │  │    User     │  │   Alerts    │        │
│  │   Service   │  │   Service   │  │   Service   │  │   Service   │        │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘        │
└─────────┼────────────────┼────────────────┼────────────────┼────────────────┘
          │                │                │                │
          ▼                ▼                ▼                ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                            DATA LAYER                                       │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │ PostgreSQL  │  │    Redis    │  │   MLflow    │  │ Cloudflare  │        │
│  │  + PostGIS  │  │    Cache    │  │   Models    │  │   R2        │        │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘        │
└─────────────────────────────────────────────────────────────────────────────┘
          ▲
          │
┌─────────────────────────────────────────────────────────────────────────────┐
│                        SCRAPING PIPELINE                                    │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │   Celery    │  │   Scrapy    │  │ Playwright  │  │  Dedup &    │        │
│  │    Beat     │  │   Spiders   │  │   Workers   │  │  Transform  │        │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘        │
└─────────────────────────────────────────────────────────────────────────────┘
```

**Key Design Decisions:**
- **Monorepo** - Single repo with `apps/` (web, admin) and `packages/` (shared code)
- **Service boundaries** - Logical separation within FastAPI, not microservices (simpler for solo dev)
- **Event-driven alerts** - Redis pub/sub triggers notification workers

---

## 3. Tech Stack (Free Tier Optimized)

| Component | Choice | Notes |
|-----------|--------|-------|
| **PostgreSQL + PostGIS** | Supabase (500MB free) or Railway ($5 credit/month) | Supabase has PostGIS built-in |
| **Redis** | Upstash (10K commands/day free) | Generous for development |
| **Object Storage** | Cloudflare R2 (10GB free, no egress fees) | Better than S3 for free tier |
| **ML Model Storage** | Git LFS + Cloudflare R2 | Skip MLflow server, use lightweight tracking |
| **Orchestration** | Celery + Redis Beat | Airflow is heavy; Celery runs free on Railway |
| **Hosting** | Railway ($5 free credit/month) | Covers multiple services |
| **Email** | Resend (3K emails/month free) | Modern, great DX |
| **WhatsApp** | Twilio (free trial credits) | Or defer until revenue |
| **Push Notifications** | Firebase Cloud Messaging (free) | Unlimited |
| **Analytics** | PostHog Cloud (1M events/month free) | Or Plausible |
| **CI/CD** | GitHub Actions (2K mins/month free) | Plenty for solo dev |
| **Auth** | Supabase Auth (free tier) | OAuth, magic links, JWT |

---

## 4. Scraping Infrastructure

**Target Sites:**
- **Finca Raiz** (fincaraiz.com.co) - Largest Colombian real estate portal
- **Metrocuadrado** (metrocuadrado.com) - Part of El Tiempo media group
- **Cien Cuadras** (ciencuadras.com) - Bancolombia's real estate platform

**Spider Architecture:**
```
┌─────────────────────────────────────────────────────────────────┐
│                     CELERY BEAT SCHEDULER                       │
│         (triggers spiders every 30-60 mins per source)          │
└─────────────────────────┬───────────────────────────────────────┘
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│                      SCRAPY SPIDERS                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐             │
│  │ FincaRaiz   │  │Metrocuadrado│  │ CienCuadras │             │
│  │   Spider    │  │   Spider    │  │   Spider    │             │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘             │
└─────────┼────────────────┼────────────────┼─────────────────────┘
          │                │                │
          ▼                ▼                ▼
┌─────────────────────────────────────────────────────────────────┐
│                   PLAYWRIGHT POOL                               │
│         (for JS-rendered pages, rotating proxies)               │
└─────────────────────────┬───────────────────────────────────────┘
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│                  PROCESSING PIPELINE                            │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐        │
│  │  Dedup   │→ │ Normalize│→ │ Geocode  │→ │  Store   │        │
│  │ (hash)   │  │ (schema) │  │ (coords) │  │  (DB)    │        │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘        │
└─────────────────────────────────────────────────────────────────┘
```

**Key Features:**
- **Deduplication** - Content hash detects duplicates across sources
- **Normalization** - Unified schema regardless of source
- **Geocoding** - Nominatim (free, OpenStreetMap-based) for coordinates
- **Change detection** - Track price changes, status updates
- **Respectful scraping** - Rate limiting, random delays
- **Near real-time** - Continuous scraping, new listings within an hour

---

## 5. Data Schema

**Core Fields:**
- Title, description, source URL
- Price, bedrooms, bathrooms, parking
- Location (address, neighborhood, city)
- Area (m²), images

**Additional Fields (from site analysis):**

| Field | Source(s) | ML Value |
|-------|-----------|----------|
| **Estrato (1-6)** | All three | Critical - socioeconomic classification affects pricing significantly |
| **Administration fees** | All three | Important for true monthly cost |
| **Private area vs constructed area** | FincaRaiz, Cien Cuadras | Both matter for price/m² calculations |
| **Construction year / antiquity** | All three | Age impacts value |
| **Property condition** | All three | "Para estrenar" (new), "Renovado" (renovated), etc. |
| **Floor number / total floors** | FincaRaiz | Higher floors often premium |
| **Property tags** | Metrocuadrado | "Negociable", "Con vista", "Disponible ahora" |
| **Virtual tour availability** | Cien Cuadras | 360°, Matterport - signals quality listing |
| **Agent/company info** | All three | Trust signals, response patterns |
| **USD price conversion** | FincaRaiz | Useful for international users |
| **Market reference price** | Cien Cuadras | Great for validating ML model |
| **Coordinates (lat/lng)** | All three | Exact geolocation available |

---

## 6. ML Pipeline - Fair Price Analysis

**Problem Statement:**
Given a rental listing, predict the fair market price and explain why it's overpriced, underpriced, or fair.

**Feature Categories:**

```
┌─────────────────────────────────────────────────────────────────┐
│                     FEATURE ENGINEERING                         │
├─────────────────┬─────────────────┬─────────────────────────────┤
│   STRUCTURAL    │    LOCATION     │        CONTEXTUAL           │
├─────────────────┼─────────────────┼─────────────────────────────┤
│ • Area (m²)     │ • Estrato       │ • Days on market            │
│ • Bedrooms      │ • Neighborhood  │ • Photos count              │
│ • Bathrooms     │ • Distance to   │ • Has virtual tour          │
│ • Parking       │   TransMilenio  │ • Agent vs owner            │
│ • Floor level   │ • Distance to   │ • Price history             │
│ • Building age  │   malls/parks   │ • Description length        │
│ • Condition     │ • Crime index   │ • Amenities count           │
│ • Admin fees    │ • Walk score    │ • Source site               │
└─────────────────┴─────────────────┴─────────────────────────────┘
```

**Ensemble Architecture:**

```
                    ┌─────────────────┐
                    │  Input Features │
                    └────────┬────────┘
                             │
        ┌────────────────────┼────────────────────┐
        ▼                    ▼                    ▼
┌───────────────┐   ┌───────────────┐   ┌───────────────┐
│   XGBoost     │   │   LightGBM    │   │   Neural Net  │
│  (tabular)    │   │  (tabular)    │   │ (embeddings)  │
└───────┬───────┘   └───────┬───────┘   └───────┬───────┘
        │                   │                   │
        └───────────────────┼───────────────────┘
                            ▼
                  ┌─────────────────┐
                  │  Meta-Learner   │
                  │ (Ridge/Linear)  │
                  └────────┬────────┘
                           ▼
                  ┌─────────────────┐
                  │ Predicted Price │
                  └────────┬────────┘
                           ▼
                  ┌─────────────────┐
                  │  SHAP Values    │
                  │ (explainability)│
                  └─────────────────┘
```

**Output to User:**
- **Fair price estimate:** $2,100,000 COP/month
- **Actual price:** $2,500,000 COP/month
- **Verdict:** 19% overpriced
- **Top reasons:** "Similar apartments in this estrato average $2.0M" / "No parking adds ~$200K premium elsewhere" / "Building age (15 years) typically reduces value"

---

## 7. Backend API (FastAPI)

**API Structure:**

```
/api
├── /v1
│   ├── /auth
│   │   ├── POST   /register
│   │   ├── POST   /login
│   │   ├── POST   /refresh
│   │   └── POST   /forgot-password
│   │
│   ├── /listings
│   │   ├── GET    /                    # Search with filters
│   │   ├── GET    /{id}                # Single listing
│   │   ├── GET    /{id}/history        # Price history
│   │   └── GET    /geo                 # Geospatial query (bbox/polygon)
│   │
│   ├── /analysis (Premium)
│   │   ├── GET    /listings/{id}/fair-price
│   │   ├── GET    /listings/{id}/comparable
│   │   └── GET    /neighborhoods/{id}/insights
│   │
│   ├── /user
│   │   ├── GET    /me
│   │   ├── PUT    /me
│   │   ├── GET    /favorites
│   │   ├── POST   /favorites/{listing_id}
│   │   ├── DELETE /favorites/{listing_id}
│   │   ├── GET    /alerts
│   │   ├── POST   /alerts
│   │   └── DELETE /alerts/{id}
│   │
│   ├── /maps
│   │   ├── GET    /heatmap/prices      # Price density
│   │   ├── GET    /heatmap/deals       # Under/overpriced density
│   │   └── GET    /neighborhoods       # Boundary polygons + stats
│   │
│   └── /webhooks
│       └── POST   /stripe              # Payment events
│
└── /admin
    ├── /scrapers                       # Status, trigger, logs
    ├── /ml                             # Model metrics, retrain
    ├── /users                          # User management
    └── /metrics                        # Business analytics
```

**Key Design Decisions:**

| Decision | Rationale |
|----------|-----------|
| **JWT auth with refresh tokens** | Stateless, works with PWA |
| **Versioned API (/v1)** | Future-proofs for breaking changes |
| **Geospatial endpoints separate** | PostGIS queries are expensive, cache differently |
| **Premium endpoints gated** | Middleware checks subscription status |
| **Async everywhere** | FastAPI async handlers for high concurrency |
| **Rate limiting** | Redis-based, per-user and per-IP tiers |

---

## 8. Frontend (Next.js 16 PWA)

**App Structure:**

```
apps/web/
├── app/
│   ├── [locale]/                    # i18n (es, en)
│   │   ├── page.tsx                 # Landing / hero
│   │   ├── search/
│   │   │   └── page.tsx             # Search results + map
│   │   ├── listing/
│   │   │   └── [id]/page.tsx        # Listing detail
│   │   ├── neighborhoods/
│   │   │   └── [id]/page.tsx        # Neighborhood insights
│   │   ├── pricing/page.tsx         # Premium plans
│   │   ├── dashboard/               # User area (protected)
│   │   │   ├── favorites/
│   │   │   ├── alerts/
│   │   │   └── settings/
│   │   └── auth/
│   │       ├── login/
│   │       └── register/
│   └── api/                         # API routes (minimal, proxy to FastAPI)
├── components/
│   ├── map/
│   │   ├── MapContainer.tsx         # Deck.gl wrapper
│   │   ├── ListingsLayer.tsx        # Property pins
│   │   ├── HeatmapLayer.tsx         # Price heat map
│   │   ├── DrawControl.tsx          # Area selection tool
│   │   └── NeighborhoodLayer.tsx    # Boundary polygons
│   ├── listings/
│   │   ├── ListingCard.tsx
│   │   ├── ListingGrid.tsx
│   │   ├── ListingFilters.tsx
│   │   └── PriceAnalysis.tsx        # SHAP visualization
│   └── ui/                          # shadcn/ui components
└── lib/
    ├── api.ts                       # API client
    ├── i18n.ts                      # Translations
    └── hooks/                       # Custom hooks
```

**Map Modes:**

| Mode | Description | Implementation |
|------|-------------|----------------|
| **Search-first** | Filter → results on map | Default view, Deck.gl ScatterplotLayer |
| **Map-first** | Draw polygon → fetch listings inside | DrawControl + PostGIS `ST_Within` query |
| **Neighborhood intelligence** | Heat maps + boundaries | HeatmapLayer + GeoJsonLayer with stats |

**PWA Features:**
- Service worker for offline listing cache
- Push notifications via Firebase
- Add to home screen prompt
- Background sync for favorites

**UI/UX Highlights:**
- Dark/light mode
- Skeleton loaders for perceived performance
- Infinite scroll on search results
- Split-pane view (list | map) with resizable divider
- Mobile: bottom sheet for listing details over map
- i18n: Spanish (default) + English

---

## 9. Notifications System

**Notification Types:**

| Trigger | Channels | Priority |
|---------|----------|----------|
| **Price drop** on favorited listing | Push, In-app, Email, WhatsApp | High |
| **New listing** matching saved search | Push, In-app, Email | Medium |
| **Listing removed** (favorited) | In-app, Email | Low |
| **Fair price alert** - overpriced listing becomes fair | Push, In-app | High |
| **Weekly digest** - new listings summary | Email | Low |

**Architecture:**

```
┌─────────────────────────────────────────────────────────────────┐
│                    EVENT PRODUCERS                              │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐             │
│  │   Scraper   │  │  ML Model   │  │    User     │             │
│  │ (new/change)│  │ (price eval)│  │  (actions)  │             │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘             │
└─────────┼────────────────┼────────────────┼─────────────────────┘
          │                │                │
          └────────────────┼────────────────┘
                           ▼
                  ┌─────────────────┐
                  │   Redis Pub/Sub │
                  │   (event bus)   │
                  └────────┬────────┘
                           │
          ┌────────────────┼────────────────┐
          ▼                ▼                ▼
┌─────────────────────────────────────────────────────────────────┐
│                  NOTIFICATION WORKERS (Celery)                  │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐             │
│  │   Matcher   │  │  Formatter  │  │  Dispatcher │             │
│  │ (who cares?)│  │ (templates) │  │ (channels)  │             │
│  └─────────────┘  └─────────────┘  └─────────────┘             │
└─────────────────────────────────────────────────────────────────┘
                           │
        ┌──────────────────┼──────────────────┐
        ▼                  ▼                  ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│   Firebase   │  │    Resend    │  │   Twilio     │  │   In-App     │
│     Push     │  │    Email     │  │  WhatsApp    │  │  (WebSocket) │
└──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘
```

**User Preferences:**

```typescript
interface NotificationPreferences {
  channels: {
    push: boolean;
    email: boolean;
    whatsapp: boolean;
    inApp: boolean;
  };
  frequency: 'instant' | 'daily_digest' | 'weekly_digest';
  quietHours: { start: string; end: string }; // e.g., "22:00" - "08:00"
  priceDropThreshold: number; // e.g., 5 = notify if drops 5%+
}
```

**Smart Batching:**
- Instant notifications for high-priority (price drops)
- Daily digest at 8am for medium-priority
- Weekly summary on Sundays for digest subscribers
- Respect quiet hours - queue and deliver after

---

## 10. Admin Dashboard

**Dashboard Structure:**

```
apps/admin/
├── app/
│   ├── page.tsx                     # Overview / KPIs
│   ├── scrapers/
│   │   ├── page.tsx                 # All spiders status
│   │   └── [spider]/page.tsx        # Individual spider logs/metrics
│   ├── ml/
│   │   ├── page.tsx                 # Model performance
│   │   └── experiments/page.tsx     # A/B tests, model comparison
│   ├── users/
│   │   ├── page.tsx                 # User list, search
│   │   └── [id]/page.tsx            # Individual user detail
│   ├── listings/
│   │   └── page.tsx                 # Content moderation, duplicates
│   ├── analytics/
│   │   ├── business/page.tsx        # Revenue, conversions
│   │   └── product/page.tsx         # Feature usage, funnels
│   └── settings/
│       └── page.tsx                 # System config
```

**Key Screens:**

| Screen | Metrics & Actions |
|--------|-------------------|
| **Overview** | Active users (24h), listings count, scraper health, revenue MTD, conversion rate |
| **Scrapers** | Success rate, items/hour, last run, errors, manual trigger, pause/resume |
| **ML Models** | MAE, RMSE, prediction distribution, drift detection, retrain button |
| **Users** | Signups, premium conversions, churn, cohort analysis |
| **Business** | MRR, trial→paid rate, LTV, popular searches, top neighborhoods |
| **A/B Tests** | Active experiments, results, statistical significance |

**Alerting (to admin):**
- Scraper failure → Slack/Email
- ML drift detected → Email
- Error rate spike → Slack
- Revenue milestone → Email

---

## 11. Infrastructure & Deployment

**Monorepo Structure:**

```
propfair/
├── apps/
│   ├── web/                    # Next.js 16 public app
│   ├── admin/                  # Next.js 16 admin dashboard
│   └── api/                    # FastAPI backend
├── packages/
│   ├── db/                     # Prisma schema, migrations
│   ├── ml/                     # ML models, training scripts
│   ├── scrapers/               # Scrapy spiders
│   ├── shared/                 # Shared types, utils
│   └── ui/                     # Shared UI components (shadcn)
├── infra/
│   ├── docker/
│   │   ├── docker-compose.yml  # Local development
│   │   ├── Dockerfile.api
│   │   ├── Dockerfile.web
│   │   └── Dockerfile.worker
│   └── railway/
│       └── railway.toml        # Railway config
├── .github/
│   └── workflows/
│       ├── ci.yml              # Test, lint, type-check
│       ├── deploy-staging.yml
│       └── deploy-prod.yml
├── turbo.json                  # Turborepo config
└── package.json
```

**Railway Services:**

```
┌─────────────────────────────────────────────────────────────────┐
│                      RAILWAY PROJECT                            │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐            │
│  │   web   │  │  admin  │  │   api   │  │ worker  │            │
│  │ Next.js │  │ Next.js │  │ FastAPI │  │ Celery  │            │
│  └─────────┘  └─────────┘  └─────────┘  └─────────┘            │
│                                                                 │
│  ┌─────────────────────┐  ┌─────────────────────┐              │
│  │     PostgreSQL      │  │       Redis         │              │
│  │   (with PostGIS)    │  │  (cache + broker)   │              │
│  └─────────────────────┘  └─────────────────────┘              │
└─────────────────────────────────────────────────────────────────┘

External (free tiers):
├── Supabase Auth
├── Cloudflare R2 (images, ML artifacts)
├── Resend (email)
├── Firebase (push notifications)
└── Twilio (WhatsApp - deferred)
```

**CI/CD Pipeline (GitHub Actions):**

```yaml
# On PR:
- Lint (ESLint, Ruff)
- Type check (TypeScript, mypy)
- Unit tests
- Build check

# On merge to main:
- All above
- Deploy to staging
- Run E2E tests against staging
- Manual approval gate

# On release tag:
- Deploy to production
- Notify Slack
```

**Environment Strategy:**
- `local` - Docker Compose, seeded test data
- `staging` - Railway, real scraped data (subset), test payments
- `production` - Railway, full data, live payments

---

## 12. Vertical Slice Plan (Phasing)

### Slice 1: Bogotá Apartments - Core Loop
*Goal: One complete flow, end-to-end demonstrable*

**Scope:**
- Single source: Finca Raiz only
- Single city: Bogotá
- Single property type: Apartments for rent
- Basic ML: XGBoost only (no ensemble yet)
- Map: Search-first mode only
- Auth: Email/password only
- Notifications: Email only
- No premium/payments yet

**Deliverables:**
- Scraper running, ~10K listings
- Basic fair-price model with SHAP
- Search + map UI
- Listing detail with price analysis
- User accounts + favorites
- Deployed on Railway

### Slice 2: Full ML + Second Source
- Add Metrocuadrado scraper
- Implement full ensemble (XGBoost + LightGBM + NN)
- Deduplication across sources
- Map-first mode (draw to search)
- Price history tracking
- Saved searches with email alerts

### Slice 3: Premium + Payments
- Stripe integration (or MercadoPago for Colombia)
- Premium tier gating
- Full SHAP explainability UI
- Neighborhood intelligence heat maps
- Push notifications (Firebase)

### Slice 4: Scale + Polish
- Add Cien Cuadras (third source)
- Expand to Medellín, Cali
- Houses (not just apartments)
- WhatsApp notifications
- Admin dashboard
- PWA optimization
- i18n (English)

### Slice 5: Growth Features
- A/B testing framework
- Advanced analytics
- Sale properties (not just rent)
- Full Colombia coverage

---

## Appendix: Key Decisions Summary

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Data acquisition | Web scraping | Full control, demonstrates data engineering |
| ML approach | Ensemble + SHAP | Sophisticated yet explainable |
| Frontend | Next.js 16 + Deck.gl | Modern, performant, rich maps |
| Backend | FastAPI (Python) | Same language as ML, async-native |
| Database | PostgreSQL + PostGIS | Geospatial queries, proven |
| Hosting | Railway | Simple, free tier friendly |
| Auth | Supabase Auth | Free, handles OAuth/JWT |
| Notifications | Multi-channel | Email, push, in-app, WhatsApp |
| Business model | Freemium | ML insights gated |
| Phasing | Vertical slice | Demonstrable faster |
