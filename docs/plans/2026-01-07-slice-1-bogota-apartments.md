# Slice 1: Bogotá Apartments - Core Loop Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.
> **For Frontend Tasks:** REQUIRED SUB-SKILL: Use frontend-design for all UI components and pages.

**Goal:** Build end-to-end flow for browsing Bogotá apartment rentals with fair-price ML analysis.

**Architecture:** Monorepo with Turborepo. FastAPI backend serves listings and ML predictions. Next.js 15 frontend with Deck.gl maps. Scrapy spider fetches Finca Raiz data. XGBoost model predicts fair prices with SHAP explainability.

**Tech Stack:** Python 3.12, FastAPI, Scrapy, XGBoost, SHAP, PostgreSQL+PostGIS, Redis, Next.js 15, TypeScript, Deck.gl, Tailwind CSS, shadcn/ui, Supabase Auth

---

## Phase 1: Project Scaffolding

### Task 1.1: Initialize Monorepo Structure

**Files:**
- Create: `package.json`
- Create: `turbo.json`
- Create: `pnpm-workspace.yaml`
- Create: `.gitignore`
- Create: `.nvmrc`

**Step 1: Initialize root package.json**

```bash
pnpm init
```

**Step 2: Create turbo.json**

```json
{
  "$schema": "https://turbo.build/schema.json",
  "tasks": {
    "build": {
      "dependsOn": ["^build"],
      "outputs": [".next/**", "!.next/cache/**", "dist/**"]
    },
    "dev": {
      "cache": false,
      "persistent": true
    },
    "lint": {
      "dependsOn": ["^lint"]
    },
    "test": {
      "dependsOn": ["^build"]
    },
    "typecheck": {
      "dependsOn": ["^typecheck"]
    }
  }
}
```

**Step 3: Create pnpm-workspace.yaml**

```yaml
packages:
  - "apps/*"
  - "packages/*"
```

**Step 4: Create .nvmrc**

```
22
```

**Step 5: Create .gitignore**

```gitignore
# Dependencies
node_modules/
.pnpm-store/

# Build outputs
.next/
dist/
build/
*.egg-info/
__pycache__/
.pytest_cache/
.mypy_cache/
.ruff_cache/

# Environment
.env
.env.local
.env.*.local
*.env

# IDE
.idea/
.vscode/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Python virtual env
.venv/
venv/

# Logs
*.log
logs/

# Test coverage
coverage/
htmlcov/
.coverage

# Misc
*.pyc
*.pyo
```

**Step 6: Update package.json with scripts**

```json
{
  "name": "propfair",
  "private": true,
  "scripts": {
    "dev": "turbo dev",
    "build": "turbo build",
    "lint": "turbo lint",
    "test": "turbo test",
    "typecheck": "turbo typecheck"
  },
  "devDependencies": {
    "turbo": "^2.3.0"
  },
  "packageManager": "pnpm@9.15.0"
}
```

**Step 7: Commit**

```bash
git init
git add .
git commit -m "chore: initialize monorepo with turborepo"
```

---

### Task 1.2: Create Directory Structure

**Files:**
- Create: `apps/.gitkeep`
- Create: `packages/.gitkeep`
- Create: `infra/docker/.gitkeep`

**Step 1: Create directories**

```bash
mkdir -p apps packages infra/docker
touch apps/.gitkeep packages/.gitkeep infra/docker/.gitkeep
```

**Step 2: Commit**

```bash
git add .
git commit -m "chore: add apps, packages, infra directories"
```

---

### Task 1.3: Setup Python Backend Package

**Files:**
- Create: `apps/api/pyproject.toml`
- Create: `apps/api/src/propfair_api/__init__.py`
- Create: `apps/api/src/propfair_api/main.py`
- Create: `apps/api/tests/__init__.py`

**Step 1: Create pyproject.toml**

```toml
[project]
name = "propfair-api"
version = "0.1.0"
description = "PropFair API - Colombian Real Estate Intelligence"
requires-python = ">=3.12"
dependencies = [
    "fastapi>=0.115.0",
    "uvicorn[standard]>=0.32.0",
    "pydantic>=2.10.0",
    "pydantic-settings>=2.6.0",
    "sqlalchemy>=2.0.36",
    "alembic>=1.14.0",
    "asyncpg>=0.30.0",
    "geoalchemy2>=0.15.0",
    "redis>=5.2.0",
    "httpx>=0.28.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.3.0",
    "pytest-asyncio>=0.24.0",
    "pytest-cov>=6.0.0",
    "ruff>=0.8.0",
    "mypy>=1.13.0",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["src/propfair_api"]

[tool.ruff]
target-version = "py312"
line-length = 100

[tool.ruff.lint]
select = ["E", "F", "I", "N", "W", "UP", "B", "C4", "SIM"]

[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]

[tool.mypy]
python_version = "3.12"
strict = true
```

**Step 2: Create __init__.py files**

```bash
mkdir -p apps/api/src/propfair_api apps/api/tests
touch apps/api/src/propfair_api/__init__.py
touch apps/api/tests/__init__.py
```

**Step 3: Create main.py with health check**

```python
from fastapi import FastAPI

app = FastAPI(
    title="PropFair API",
    description="Colombian Real Estate Intelligence Platform",
    version="0.1.0",
)


@app.get("/health")
async def health_check() -> dict[str, str]:
    return {"status": "healthy"}
```

**Step 4: Commit**

```bash
git add apps/api/
git commit -m "chore: scaffold FastAPI backend package"
```

---

### Task 1.4: Setup Next.js Web App

**Files:**
- Create: `apps/web/` (via create-next-app)

**Step 1: Create Next.js app**

```bash
cd apps
pnpm create next-app@latest web --typescript --tailwind --eslint --app --src-dir --import-alias "@/*" --use-pnpm
cd ..
```

**Step 2: Update apps/web/package.json name**

Change `"name"` to `"@propfair/web"`.

**Step 3: Commit**

```bash
git add apps/web/
git commit -m "chore: scaffold Next.js web app"
```

---

### Task 1.5: Setup Shared Database Package

**Files:**
- Create: `packages/db/package.json`
- Create: `packages/db/prisma/schema.prisma`
- Create: `packages/db/src/index.ts`

**Step 1: Create package.json**

```json
{
  "name": "@propfair/db",
  "version": "0.1.0",
  "private": true,
  "main": "./src/index.ts",
  "types": "./src/index.ts",
  "scripts": {
    "db:generate": "prisma generate",
    "db:push": "prisma db push",
    "db:migrate": "prisma migrate dev",
    "db:studio": "prisma studio"
  },
  "dependencies": {
    "@prisma/client": "^6.1.0"
  },
  "devDependencies": {
    "prisma": "^6.1.0",
    "typescript": "^5.7.0"
  }
}
```

**Step 2: Create initial schema.prisma**

```prisma
generator client {
  provider        = "prisma-client-js"
  previewFeatures = ["postgresqlExtensions"]
}

datasource db {
  provider   = "postgresql"
  url        = env("DATABASE_URL")
  extensions = [postgis]
}

model Listing {
  id          String   @id @default(cuid())
  externalId  String   @map("external_id")
  source      String
  url         String
  title       String
  description String?

  price           Int
  adminFee        Int?      @map("admin_fee")
  bedrooms        Int
  bathrooms       Int
  parkingSpaces   Int       @map("parking_spaces")
  area            Float
  estrato         Int?
  floor           Int?
  totalFloors     Int?      @map("total_floors")
  buildingAge     Int?      @map("building_age")
  propertyCondition String? @map("property_condition")

  address      String
  neighborhood String
  city         String
  latitude     Float
  longitude    Float

  images       String[]
  amenities    String[]

  firstSeenAt  DateTime  @default(now()) @map("first_seen_at")
  lastSeenAt   DateTime  @default(now()) @map("last_seen_at")
  isActive     Boolean   @default(true) @map("is_active")
  contentHash  String    @map("content_hash")

  createdAt    DateTime  @default(now()) @map("created_at")
  updatedAt    DateTime  @updatedAt @map("updated_at")

  priceHistory  PriceHistory[]
  favorites     Favorite[]

  @@unique([source, externalId])
  @@index([city, neighborhood])
  @@index([price])
  @@index([bedrooms])
  @@index([isActive])
  @@map("listings")
}

model PriceHistory {
  id        String   @id @default(cuid())
  listingId String   @map("listing_id")
  price     Int
  adminFee  Int?     @map("admin_fee")
  recordedAt DateTime @default(now()) @map("recorded_at")

  listing   Listing  @relation(fields: [listingId], references: [id], onDelete: Cascade)

  @@index([listingId, recordedAt])
  @@map("price_history")
}

model User {
  id            String   @id @default(cuid())
  email         String   @unique
  passwordHash  String   @map("password_hash")
  name          String?

  createdAt     DateTime @default(now()) @map("created_at")
  updatedAt     DateTime @updatedAt @map("updated_at")

  favorites     Favorite[]

  @@map("users")
}

model Favorite {
  id        String   @id @default(cuid())
  userId    String   @map("user_id")
  listingId String   @map("listing_id")
  createdAt DateTime @default(now()) @map("created_at")

  user      User     @relation(fields: [userId], references: [id], onDelete: Cascade)
  listing   Listing  @relation(fields: [listingId], references: [id], onDelete: Cascade)

  @@unique([userId, listingId])
  @@map("favorites")
}
```

**Step 3: Create src/index.ts**

```typescript
export * from "@prisma/client";
import { PrismaClient } from "@prisma/client";

const globalForPrisma = globalThis as unknown as {
  prisma: PrismaClient | undefined;
};

export const prisma =
  globalForPrisma.prisma ??
  new PrismaClient({
    log: process.env.NODE_ENV === "development" ? ["query", "error", "warn"] : ["error"],
  });

if (process.env.NODE_ENV !== "production") globalForPrisma.prisma = prisma;
```

**Step 4: Commit**

```bash
git add packages/db/
git commit -m "chore: add database package with Prisma schema"
```

---

### Task 1.6: Setup Docker Compose for Local Development

**Files:**
- Create: `infra/docker/docker-compose.yml`
- Create: `.env.example`

**Step 1: Create docker-compose.yml**

```yaml
services:
  postgres:
    image: postgis/postgis:16-3.4
    container_name: propfair-postgres
    environment:
      POSTGRES_USER: propfair
      POSTGRES_PASSWORD: propfair_dev
      POSTGRES_DB: propfair
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U propfair"]
      interval: 5s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    container_name: propfair-redis
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 5s
      timeout: 5s
      retries: 5

volumes:
  postgres_data:
  redis_data:
```

**Step 2: Create .env.example**

```env
# Database
DATABASE_URL="postgresql://propfair:propfair_dev@localhost:5432/propfair"

# Redis
REDIS_URL="redis://localhost:6379"

# API
API_HOST="0.0.0.0"
API_PORT="8000"
SECRET_KEY="change-me-in-production"

# Frontend
NEXT_PUBLIC_API_URL="http://localhost:8000"
```

**Step 3: Commit**

```bash
git add infra/docker/ .env.example
git commit -m "chore: add Docker Compose for local dev"
```

---

## Phase 2: Scraping Pipeline

### Task 2.1: Setup Scrapy Package

**Files:**
- Create: `packages/scrapers/pyproject.toml`
- Create: `packages/scrapers/src/propfair_scrapers/__init__.py`
- Create: `packages/scrapers/src/propfair_scrapers/settings.py`
- Create: `packages/scrapers/scrapy.cfg`

**Step 1: Create pyproject.toml**

```toml
[project]
name = "propfair-scrapers"
version = "0.1.0"
description = "PropFair Web Scrapers"
requires-python = ">=3.12"
dependencies = [
    "scrapy>=2.12.0",
    "playwright>=1.49.0",
    "scrapy-playwright>=0.0.42",
    "httpx>=0.28.0",
    "python-dotenv>=1.0.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.3.0",
    "pytest-asyncio>=0.24.0",
    "ruff>=0.8.0",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["src/propfair_scrapers"]

[tool.ruff]
target-version = "py312"
line-length = 100
```

**Step 2: Create settings.py**

```python
BOT_NAME = "propfair_scrapers"

SPIDER_MODULES = ["propfair_scrapers.spiders"]
NEWSPIDER_MODULE = "propfair_scrapers.spiders"

ROBOTSTXT_OBEY = True
CONCURRENT_REQUESTS = 8
DOWNLOAD_DELAY = 2
RANDOMIZE_DOWNLOAD_DELAY = True

COOKIES_ENABLED = False

DEFAULT_REQUEST_HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "es-CO,es;q=0.9,en;q=0.8",
}

DOWNLOAD_HANDLERS = {
    "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
    "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
}

TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"

ITEM_PIPELINES = {
    "propfair_scrapers.pipelines.ValidationPipeline": 100,
    "propfair_scrapers.pipelines.DeduplicationPipeline": 200,
    "propfair_scrapers.pipelines.DatabasePipeline": 300,
}

LOG_LEVEL = "INFO"
```

**Step 3: Create __init__.py and scrapy.cfg**

```bash
mkdir -p packages/scrapers/src/propfair_scrapers/spiders
touch packages/scrapers/src/propfair_scrapers/__init__.py
touch packages/scrapers/src/propfair_scrapers/spiders/__init__.py
```

scrapy.cfg:
```ini
[settings]
default = propfair_scrapers.settings

[deploy]
project = propfair_scrapers
```

**Step 4: Commit**

```bash
git add packages/scrapers/
git commit -m "chore: scaffold Scrapy package"
```

---

### Task 2.2: Create Listing Item Schema

**Files:**
- Create: `packages/scrapers/src/propfair_scrapers/items.py`
- Create: `packages/scrapers/tests/test_items.py`

**Step 1: Write the failing test**

```python
import pytest
from propfair_scrapers.items import ListingItem


def test_listing_item_required_fields():
    item = ListingItem(
        external_id="123",
        source="fincaraiz",
        url="https://example.com/123",
        title="Test Apartment",
        price=2000000,
        bedrooms=2,
        bathrooms=1,
        parking_spaces=1,
        area=60.0,
        address="Calle 100",
        neighborhood="Usaquén",
        city="Bogotá",
        latitude=4.6871,
        longitude=-74.0466,
    )
    assert item["external_id"] == "123"
    assert item["source"] == "fincaraiz"


def test_listing_item_optional_fields():
    item = ListingItem(
        external_id="123",
        source="fincaraiz",
        url="https://example.com/123",
        title="Test Apartment",
        price=2000000,
        bedrooms=2,
        bathrooms=1,
        parking_spaces=1,
        area=60.0,
        address="Calle 100",
        neighborhood="Usaquén",
        city="Bogotá",
        latitude=4.6871,
        longitude=-74.0466,
        estrato=4,
        admin_fee=300000,
        description="Nice apartment",
    )
    assert item["estrato"] == 4
    assert item["admin_fee"] == 300000
```

**Step 2: Run test to verify it fails**

```bash
cd packages/scrapers
pytest tests/test_items.py -v
```

Expected: FAIL with "No module named 'propfair_scrapers.items'"

**Step 3: Write items.py**

```python
import scrapy


class ListingItem(scrapy.Item):
    # Required fields
    external_id = scrapy.Field()
    source = scrapy.Field()
    url = scrapy.Field()
    title = scrapy.Field()
    price = scrapy.Field()
    bedrooms = scrapy.Field()
    bathrooms = scrapy.Field()
    parking_spaces = scrapy.Field()
    area = scrapy.Field()
    address = scrapy.Field()
    neighborhood = scrapy.Field()
    city = scrapy.Field()
    latitude = scrapy.Field()
    longitude = scrapy.Field()

    # Optional fields
    description = scrapy.Field()
    admin_fee = scrapy.Field()
    estrato = scrapy.Field()
    floor = scrapy.Field()
    total_floors = scrapy.Field()
    building_age = scrapy.Field()
    property_condition = scrapy.Field()
    images = scrapy.Field()
    amenities = scrapy.Field()
```

**Step 4: Run test to verify it passes**

```bash
pytest tests/test_items.py -v
```

Expected: PASS

**Step 5: Commit**

```bash
git add .
git commit -m "feat(scrapers): add ListingItem schema"
```

---

### Task 2.3: Create Validation Pipeline

**Files:**
- Create: `packages/scrapers/src/propfair_scrapers/pipelines.py`
- Create: `packages/scrapers/tests/test_pipelines.py`

**Step 1: Write the failing test**

```python
import pytest
from scrapy.exceptions import DropItem
from propfair_scrapers.items import ListingItem
from propfair_scrapers.pipelines import ValidationPipeline


@pytest.fixture
def valid_item():
    return ListingItem(
        external_id="123",
        source="fincaraiz",
        url="https://example.com/123",
        title="Test Apartment",
        price=2000000,
        bedrooms=2,
        bathrooms=1,
        parking_spaces=1,
        area=60.0,
        address="Calle 100",
        neighborhood="Usaquén",
        city="Bogotá",
        latitude=4.6871,
        longitude=-74.0466,
    )


def test_validation_pipeline_passes_valid_item(valid_item):
    pipeline = ValidationPipeline()
    result = pipeline.process_item(valid_item, None)
    assert result == valid_item


def test_validation_pipeline_drops_missing_price():
    item = ListingItem(
        external_id="123",
        source="fincaraiz",
        url="https://example.com/123",
        title="Test Apartment",
        bedrooms=2,
        bathrooms=1,
        parking_spaces=1,
        area=60.0,
        address="Calle 100",
        neighborhood="Usaquén",
        city="Bogotá",
        latitude=4.6871,
        longitude=-74.0466,
    )
    pipeline = ValidationPipeline()
    with pytest.raises(DropItem, match="Missing required field: price"):
        pipeline.process_item(item, None)


def test_validation_pipeline_drops_invalid_price(valid_item):
    valid_item["price"] = -100
    pipeline = ValidationPipeline()
    with pytest.raises(DropItem, match="Invalid price"):
        pipeline.process_item(valid_item, None)
```

**Step 2: Run test to verify it fails**

```bash
pytest tests/test_pipelines.py -v
```

Expected: FAIL

**Step 3: Write pipelines.py**

```python
import hashlib
import json
from scrapy.exceptions import DropItem


class ValidationPipeline:
    REQUIRED_FIELDS = [
        "external_id",
        "source",
        "url",
        "title",
        "price",
        "bedrooms",
        "bathrooms",
        "parking_spaces",
        "area",
        "address",
        "neighborhood",
        "city",
        "latitude",
        "longitude",
    ]

    def process_item(self, item, spider):
        for field in self.REQUIRED_FIELDS:
            if field not in item or item[field] is None:
                raise DropItem(f"Missing required field: {field}")

        if item["price"] <= 0:
            raise DropItem(f"Invalid price: {item['price']}")

        if item["area"] <= 0:
            raise DropItem(f"Invalid area: {item['area']}")

        return item


class DeduplicationPipeline:
    def __init__(self):
        self.seen_hashes = set()

    def process_item(self, item, spider):
        content = {
            "external_id": item["external_id"],
            "source": item["source"],
            "price": item["price"],
            "title": item["title"],
        }
        content_hash = hashlib.sha256(
            json.dumps(content, sort_keys=True).encode()
        ).hexdigest()

        if content_hash in self.seen_hashes:
            raise DropItem(f"Duplicate item: {item['external_id']}")

        self.seen_hashes.add(content_hash)
        item["content_hash"] = content_hash
        return item


class DatabasePipeline:
    def process_item(self, item, spider):
        # Will be implemented when DB connection is ready
        return item
```

**Step 4: Run test to verify it passes**

```bash
pytest tests/test_pipelines.py -v
```

Expected: PASS

**Step 5: Commit**

```bash
git add .
git commit -m "feat(scrapers): add validation and deduplication pipelines"
```

---

### Task 2.4: Create Finca Raiz Spider - Basic Structure

**Files:**
- Create: `packages/scrapers/src/propfair_scrapers/spiders/fincaraiz.py`
- Create: `packages/scrapers/tests/test_fincaraiz_spider.py`

**Step 1: Write the failing test**

```python
import pytest
from propfair_scrapers.spiders.fincaraiz import FincaRaizSpider


def test_spider_name():
    spider = FincaRaizSpider()
    assert spider.name == "fincaraiz"


def test_spider_allowed_domains():
    spider = FincaRaizSpider()
    assert "fincaraiz.com.co" in spider.allowed_domains


def test_spider_start_urls():
    spider = FincaRaizSpider()
    assert len(spider.start_urls) > 0
    assert "bogota" in spider.start_urls[0].lower()
```

**Step 2: Run test to verify it fails**

```bash
pytest tests/test_fincaraiz_spider.py -v
```

Expected: FAIL

**Step 3: Write fincaraiz.py**

```python
import scrapy
from propfair_scrapers.items import ListingItem


class FincaRaizSpider(scrapy.Spider):
    name = "fincaraiz"
    allowed_domains = ["fincaraiz.com.co"]
    start_urls = [
        "https://www.fincaraiz.com.co/apartamentos/arriendo/bogota/"
    ]

    custom_settings = {
        "DOWNLOAD_HANDLERS": {
            "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
            "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
        },
    }

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(
                url,
                meta={"playwright": True, "playwright_include_page": True},
                callback=self.parse_listing_page,
            )

    async def parse_listing_page(self, response):
        page = response.meta["playwright_page"]
        await page.close()

        # Extract listing links
        listing_links = response.css("a.card-result-image::attr(href)").getall()

        for link in listing_links:
            yield response.follow(
                link,
                meta={"playwright": True, "playwright_include_page": True},
                callback=self.parse_listing_detail,
            )

        # Pagination
        next_page = response.css("a.pagination-next::attr(href)").get()
        if next_page:
            yield response.follow(
                next_page,
                meta={"playwright": True, "playwright_include_page": True},
                callback=self.parse_listing_page,
            )

    async def parse_listing_detail(self, response):
        page = response.meta["playwright_page"]
        await page.close()

        # Extract external ID from URL
        external_id = response.url.split("/")[-1].split("-")[-1]

        # Price extraction
        price_text = response.css("span.price::text").get()
        price = self._parse_price(price_text) if price_text else None

        # Basic info
        title = response.css("h1.title::text").get()
        description = response.css("div.description p::text").get()

        # Property details
        bedrooms = self._extract_number(response, "habitaciones")
        bathrooms = self._extract_number(response, "baños")
        parking = self._extract_number(response, "garajes")
        area = self._extract_float(response, "área")

        # Location
        neighborhood = response.css("span.neighborhood::text").get()
        address = response.css("span.address::text").get()

        # Coordinates
        lat = response.css("div.map::attr(data-lat)").get()
        lng = response.css("div.map::attr(data-lng)").get()

        # Additional details
        estrato = self._extract_number(response, "estrato")
        admin_fee_text = response.css("span.admin-fee::text").get()
        admin_fee = self._parse_price(admin_fee_text) if admin_fee_text else None

        # Images
        images = response.css("div.gallery img::attr(src)").getall()

        yield ListingItem(
            external_id=external_id,
            source="fincaraiz",
            url=response.url,
            title=title.strip() if title else None,
            description=description.strip() if description else None,
            price=price,
            admin_fee=admin_fee,
            bedrooms=bedrooms,
            bathrooms=bathrooms,
            parking_spaces=parking or 0,
            area=area,
            estrato=estrato,
            address=address.strip() if address else "",
            neighborhood=neighborhood.strip() if neighborhood else "",
            city="Bogotá",
            latitude=float(lat) if lat else 4.6097,
            longitude=float(lng) if lng else -74.0817,
            images=images,
        )

    def _parse_price(self, text: str) -> int | None:
        if not text:
            return None
        # Remove $ and . separators, e.g., "$ 2.500.000" -> 2500000
        cleaned = text.replace("$", "").replace(".", "").replace(",", "").strip()
        try:
            return int(cleaned)
        except ValueError:
            return None

    def _extract_number(self, response, label: str) -> int | None:
        selector = f"span:contains('{label}') + span::text"
        value = response.css(selector).get()
        if value:
            try:
                return int(value.strip())
            except ValueError:
                pass
        return None

    def _extract_float(self, response, label: str) -> float | None:
        selector = f"span:contains('{label}') + span::text"
        value = response.css(selector).get()
        if value:
            cleaned = value.replace("m²", "").replace(",", ".").strip()
            try:
                return float(cleaned)
            except ValueError:
                pass
        return None
```

**Step 4: Run test to verify it passes**

```bash
pytest tests/test_fincaraiz_spider.py -v
```

Expected: PASS

**Step 5: Commit**

```bash
git add .
git commit -m "feat(scrapers): add FincaRaiz spider basic structure"
```

---

## Phase 3: API Endpoints

### Task 3.1: Setup API Configuration

**Files:**
- Create: `apps/api/src/propfair_api/config.py`
- Create: `apps/api/tests/test_config.py`

**Step 1: Write the failing test**

```python
import os
import pytest
from propfair_api.config import Settings


def test_settings_loads_defaults():
    settings = Settings(
        database_url="postgresql://test:test@localhost:5432/test",
        redis_url="redis://localhost:6379",
        secret_key="test-secret",
    )
    assert settings.api_host == "0.0.0.0"
    assert settings.api_port == 8000


def test_settings_requires_database_url():
    with pytest.raises(Exception):
        Settings(redis_url="redis://localhost:6379", secret_key="test")
```

**Step 2: Run test to verify it fails**

```bash
cd apps/api
pytest tests/test_config.py -v
```

Expected: FAIL

**Step 3: Write config.py**

```python
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Database
    database_url: str

    # Redis
    redis_url: str

    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    secret_key: str
    debug: bool = False

    # Auth
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7

    class Config:
        env_file = ".env"


settings = Settings()
```

**Step 4: Run test to verify it passes**

```bash
pytest tests/test_config.py -v
```

Expected: PASS

**Step 5: Commit**

```bash
git add .
git commit -m "feat(api): add configuration with pydantic-settings"
```

---

### Task 3.2: Setup Database Connection

**Files:**
- Create: `apps/api/src/propfair_api/database.py`
- Create: `apps/api/tests/test_database.py`

**Step 1: Write the failing test**

```python
import pytest
from propfair_api.database import get_db_session


def test_get_db_session_returns_generator():
    gen = get_db_session()
    assert hasattr(gen, "__next__")
```

**Step 2: Run test to verify it fails**

```bash
pytest tests/test_database.py -v
```

Expected: FAIL

**Step 3: Write database.py**

```python
from collections.abc import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from propfair_api.config import settings

engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db_session() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

**Step 4: Run test to verify it passes**

```bash
pytest tests/test_database.py -v
```

Expected: PASS

**Step 5: Commit**

```bash
git add .
git commit -m "feat(api): add database session management"
```

---

### Task 3.3: Create Listings Router

**Files:**
- Create: `apps/api/src/propfair_api/routers/__init__.py`
- Create: `apps/api/src/propfair_api/routers/listings.py`
- Create: `apps/api/src/propfair_api/schemas/listing.py`
- Create: `apps/api/tests/test_listings_router.py`

**Step 1: Write the failing test**

```python
import pytest
from fastapi.testclient import TestClient
from propfair_api.main import app


client = TestClient(app)


def test_search_listings_returns_list():
    response = client.get("/api/v1/listings")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert isinstance(data["items"], list)


def test_search_listings_with_filters():
    response = client.get(
        "/api/v1/listings",
        params={
            "min_price": 1000000,
            "max_price": 3000000,
            "bedrooms": 2,
            "city": "Bogotá",
        },
    )
    assert response.status_code == 200
```

**Step 2: Run test to verify it fails**

```bash
pytest tests/test_listings_router.py -v
```

Expected: FAIL

**Step 3: Write schemas/listing.py**

```python
from pydantic import BaseModel
from datetime import datetime


class ListingBase(BaseModel):
    title: str
    description: str | None = None
    price: int
    admin_fee: int | None = None
    bedrooms: int
    bathrooms: int
    parking_spaces: int
    area: float
    estrato: int | None = None
    address: str
    neighborhood: str
    city: str
    latitude: float
    longitude: float


class ListingResponse(ListingBase):
    id: str
    source: str
    url: str
    images: list[str]
    is_active: bool
    first_seen_at: datetime
    last_seen_at: datetime

    class Config:
        from_attributes = True


class ListingSearchParams(BaseModel):
    city: str | None = None
    neighborhood: str | None = None
    min_price: int | None = None
    max_price: int | None = None
    bedrooms: int | None = None
    bathrooms: int | None = None
    min_area: float | None = None
    max_area: float | None = None
    estrato: int | None = None
    page: int = 1
    page_size: int = 20


class PaginatedListings(BaseModel):
    items: list[ListingResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
```

**Step 4: Write routers/listings.py**

```python
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from propfair_api.database import get_db_session
from propfair_api.schemas.listing import (
    ListingResponse,
    ListingSearchParams,
    PaginatedListings,
)

router = APIRouter(prefix="/api/v1/listings", tags=["listings"])


@router.get("", response_model=PaginatedListings)
async def search_listings(
    city: str | None = Query(None),
    neighborhood: str | None = Query(None),
    min_price: int | None = Query(None),
    max_price: int | None = Query(None),
    bedrooms: int | None = Query(None),
    bathrooms: int | None = Query(None),
    min_area: float | None = Query(None),
    max_area: float | None = Query(None),
    estrato: int | None = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db_session),
) -> PaginatedListings:
    # TODO: Implement actual DB query
    return PaginatedListings(
        items=[],
        total=0,
        page=page,
        page_size=page_size,
        total_pages=0,
    )


@router.get("/{listing_id}", response_model=ListingResponse)
async def get_listing(
    listing_id: str,
    db: Session = Depends(get_db_session),
) -> ListingResponse:
    # TODO: Implement actual DB query
    raise NotImplementedError()
```

**Step 5: Update main.py to include router**

```python
from fastapi import FastAPI
from propfair_api.routers import listings

app = FastAPI(
    title="PropFair API",
    description="Colombian Real Estate Intelligence Platform",
    version="0.1.0",
)

app.include_router(listings.router)


@app.get("/health")
async def health_check() -> dict[str, str]:
    return {"status": "healthy"}
```

**Step 6: Create routers/__init__.py**

```python
from propfair_api.routers import listings

__all__ = ["listings"]
```

**Step 7: Run test to verify it passes**

```bash
pytest tests/test_listings_router.py -v
```

Expected: PASS

**Step 8: Commit**

```bash
git add .
git commit -m "feat(api): add listings router with search endpoint"
```

---

## Phase 4: Frontend - Search & Map UI

> **IMPORTANT:** For all tasks in this phase, use the `frontend-design` skill to ensure high design quality and avoid generic AI aesthetics.

### Task 4.1: Setup Base Layout and Theme

**Files:**
- Modify: `apps/web/src/app/layout.tsx`
- Create: `apps/web/src/app/globals.css` (update)
- Create: `apps/web/src/components/ui/` (shadcn setup)

**Step 1: Install shadcn/ui**

```bash
cd apps/web
pnpm dlx shadcn@latest init
```

Select: New York style, Zinc color, CSS variables

**Step 2: Add base components**

```bash
pnpm dlx shadcn@latest add button card input label select slider
```

**Step 3: Update layout.tsx**

```typescript
import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "PropFair - Colombian Real Estate Intelligence",
  description: "Find fair-priced rentals in Colombia with AI-powered analysis",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="es">
      <body className={inter.className}>{children}</body>
    </html>
  );
}
```

**Step 4: Commit**

```bash
git add .
git commit -m "feat(web): setup shadcn/ui and base layout"
```

---

### Task 4.2: Create Search Filters Component

> **Use `frontend-design` skill for this task.**

**Files:**
- Create: `apps/web/src/components/listings/ListingFilters.tsx`
- Create: `apps/web/src/lib/api.ts`

**Step 1: Create API client**

```typescript
// apps/web/src/lib/api.ts
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export interface ListingSearchParams {
  city?: string;
  neighborhood?: string;
  min_price?: number;
  max_price?: number;
  bedrooms?: number;
  bathrooms?: number;
  min_area?: number;
  max_area?: number;
  estrato?: number;
  page?: number;
  page_size?: number;
}

export interface Listing {
  id: string;
  title: string;
  description: string | null;
  price: number;
  admin_fee: number | null;
  bedrooms: number;
  bathrooms: number;
  parking_spaces: number;
  area: number;
  estrato: number | null;
  address: string;
  neighborhood: string;
  city: string;
  latitude: number;
  longitude: number;
  source: string;
  url: string;
  images: string[];
  is_active: boolean;
}

export interface PaginatedListings {
  items: Listing[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export async function searchListings(
  params: ListingSearchParams
): Promise<PaginatedListings> {
  const searchParams = new URLSearchParams();
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null) {
      searchParams.append(key, String(value));
    }
  });

  const response = await fetch(
    `${API_BASE_URL}/api/v1/listings?${searchParams.toString()}`
  );

  if (!response.ok) {
    throw new Error("Failed to fetch listings");
  }

  return response.json();
}
```

**Step 2: Create ListingFilters component**

```typescript
// apps/web/src/components/listings/ListingFilters.tsx
"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { ListingSearchParams } from "@/lib/api";

interface ListingFiltersProps {
  onSearch: (params: ListingSearchParams) => void;
  isLoading?: boolean;
}

export function ListingFilters({ onSearch, isLoading }: ListingFiltersProps) {
  const [filters, setFilters] = useState<ListingSearchParams>({
    city: "Bogotá",
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSearch(filters);
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4 p-4 bg-white rounded-lg shadow">
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="space-y-2">
          <Label htmlFor="min_price">Precio mínimo</Label>
          <Input
            id="min_price"
            type="number"
            placeholder="$ 1.000.000"
            value={filters.min_price || ""}
            onChange={(e) =>
              setFilters({ ...filters, min_price: Number(e.target.value) || undefined })
            }
          />
        </div>

        <div className="space-y-2">
          <Label htmlFor="max_price">Precio máximo</Label>
          <Input
            id="max_price"
            type="number"
            placeholder="$ 5.000.000"
            value={filters.max_price || ""}
            onChange={(e) =>
              setFilters({ ...filters, max_price: Number(e.target.value) || undefined })
            }
          />
        </div>

        <div className="space-y-2">
          <Label htmlFor="bedrooms">Habitaciones</Label>
          <Select
            value={filters.bedrooms?.toString()}
            onValueChange={(value) =>
              setFilters({ ...filters, bedrooms: Number(value) || undefined })
            }
          >
            <SelectTrigger id="bedrooms">
              <SelectValue placeholder="Cualquiera" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="1">1+</SelectItem>
              <SelectItem value="2">2+</SelectItem>
              <SelectItem value="3">3+</SelectItem>
              <SelectItem value="4">4+</SelectItem>
            </SelectContent>
          </Select>
        </div>

        <div className="space-y-2">
          <Label htmlFor="estrato">Estrato</Label>
          <Select
            value={filters.estrato?.toString()}
            onValueChange={(value) =>
              setFilters({ ...filters, estrato: Number(value) || undefined })
            }
          >
            <SelectTrigger id="estrato">
              <SelectValue placeholder="Cualquiera" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="1">1</SelectItem>
              <SelectItem value="2">2</SelectItem>
              <SelectItem value="3">3</SelectItem>
              <SelectItem value="4">4</SelectItem>
              <SelectItem value="5">5</SelectItem>
              <SelectItem value="6">6</SelectItem>
            </SelectContent>
          </Select>
        </div>
      </div>

      <Button type="submit" className="w-full" disabled={isLoading}>
        {isLoading ? "Buscando..." : "Buscar"}
      </Button>
    </form>
  );
}
```

**Step 3: Commit**

```bash
git add .
git commit -m "feat(web): add listing filters component"
```

---

### Task 4.3: Create Map Component with Deck.gl

> **Use `frontend-design` skill for this task.**

**Files:**
- Create: `apps/web/src/components/map/MapContainer.tsx`
- Create: `apps/web/src/components/map/ListingsLayer.tsx`

**Step 1: Install dependencies**

```bash
cd apps/web
pnpm add @deck.gl/core @deck.gl/react @deck.gl/layers maplibre-gl react-map-gl
```

**Step 2: Create MapContainer.tsx**

```typescript
// apps/web/src/components/map/MapContainer.tsx
"use client";

import { useState, useCallback } from "react";
import Map, { NavigationControl, ViewStateChangeEvent } from "react-map-gl/maplibre";
import DeckGL from "@deck.gl/react";
import { ScatterplotLayer } from "@deck.gl/layers";
import type { Listing } from "@/lib/api";
import "maplibre-gl/dist/maplibre-gl.css";

interface MapContainerProps {
  listings: Listing[];
  onListingClick?: (listing: Listing) => void;
  selectedListingId?: string;
}

const INITIAL_VIEW_STATE = {
  latitude: 4.6097,
  longitude: -74.0817,
  zoom: 12,
  pitch: 0,
  bearing: 0,
};

export function MapContainer({
  listings,
  onListingClick,
  selectedListingId,
}: MapContainerProps) {
  const [viewState, setViewState] = useState(INITIAL_VIEW_STATE);

  const handleViewStateChange = useCallback(
    (e: ViewStateChangeEvent) => {
      setViewState(e.viewState);
    },
    []
  );

  const layers = [
    new ScatterplotLayer({
      id: "listings-layer",
      data: listings,
      getPosition: (d: Listing) => [d.longitude, d.latitude],
      getRadius: (d: Listing) => (d.id === selectedListingId ? 150 : 100),
      getFillColor: (d: Listing) => {
        if (d.id === selectedListingId) return [59, 130, 246, 255]; // Blue
        return [16, 185, 129, 200]; // Green
      },
      pickable: true,
      onClick: ({ object }) => {
        if (object && onListingClick) {
          onListingClick(object);
        }
      },
      radiusMinPixels: 8,
      radiusMaxPixels: 20,
    }),
  ];

  return (
    <div className="relative w-full h-full">
      <DeckGL
        viewState={viewState}
        onViewStateChange={handleViewStateChange as any}
        controller={true}
        layers={layers}
      >
        <Map
          mapStyle="https://basemaps.cartocdn.com/gl/positron-gl-style/style.json"
        >
          <NavigationControl position="top-right" />
        </Map>
      </DeckGL>
    </div>
  );
}
```

**Step 3: Commit**

```bash
git add .
git commit -m "feat(web): add map component with Deck.gl"
```

---

### Task 4.4: Create Listing Card Component

> **Use `frontend-design` skill for this task.**

**Files:**
- Create: `apps/web/src/components/listings/ListingCard.tsx`

**Step 1: Create ListingCard.tsx**

```typescript
// apps/web/src/components/listings/ListingCard.tsx
import Image from "next/image";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import type { Listing } from "@/lib/api";
import { Bed, Bath, Car, Maximize } from "lucide-react";

interface ListingCardProps {
  listing: Listing;
  onClick?: () => void;
  isSelected?: boolean;
}

function formatPrice(price: number): string {
  return new Intl.NumberFormat("es-CO", {
    style: "currency",
    currency: "COP",
    maximumFractionDigits: 0,
  }).format(price);
}

export function ListingCard({ listing, onClick, isSelected }: ListingCardProps) {
  return (
    <Card
      className={`cursor-pointer transition-all hover:shadow-lg ${
        isSelected ? "ring-2 ring-blue-500" : ""
      }`}
      onClick={onClick}
    >
      <div className="relative h-48 w-full">
        {listing.images[0] ? (
          <Image
            src={listing.images[0]}
            alt={listing.title}
            fill
            className="object-cover rounded-t-lg"
          />
        ) : (
          <div className="h-full w-full bg-gray-200 rounded-t-lg flex items-center justify-center">
            <span className="text-gray-400">Sin imagen</span>
          </div>
        )}
        {listing.estrato && (
          <Badge className="absolute top-2 right-2">
            Estrato {listing.estrato}
          </Badge>
        )}
      </div>
      <CardContent className="p-4">
        <div className="space-y-2">
          <h3 className="font-semibold text-lg line-clamp-1">{listing.title}</h3>
          <p className="text-sm text-gray-500 line-clamp-1">
            {listing.neighborhood}, {listing.city}
          </p>
          <p className="text-xl font-bold text-green-600">
            {formatPrice(listing.price)}
            <span className="text-sm font-normal text-gray-500">/mes</span>
          </p>
          {listing.admin_fee && (
            <p className="text-sm text-gray-500">
              Admin: {formatPrice(listing.admin_fee)}
            </p>
          )}
          <div className="flex items-center gap-4 text-sm text-gray-600 pt-2">
            <span className="flex items-center gap-1">
              <Bed className="h-4 w-4" />
              {listing.bedrooms}
            </span>
            <span className="flex items-center gap-1">
              <Bath className="h-4 w-4" />
              {listing.bathrooms}
            </span>
            <span className="flex items-center gap-1">
              <Car className="h-4 w-4" />
              {listing.parking_spaces}
            </span>
            <span className="flex items-center gap-1">
              <Maximize className="h-4 w-4" />
              {listing.area}m²
            </span>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
```

**Step 2: Install lucide-react and badge component**

```bash
pnpm add lucide-react
pnpm dlx shadcn@latest add badge
```

**Step 3: Commit**

```bash
git add .
git commit -m "feat(web): add listing card component"
```

---

### Task 4.5: Create Search Page

> **Use `frontend-design` skill for this task.**

**Files:**
- Create: `apps/web/src/app/search/page.tsx`

**Step 1: Create search page**

```typescript
// apps/web/src/app/search/page.tsx
"use client";

import { useState, useCallback } from "react";
import { ListingFilters } from "@/components/listings/ListingFilters";
import { ListingCard } from "@/components/listings/ListingCard";
import { MapContainer } from "@/components/map/MapContainer";
import { searchListings, type Listing, type ListingSearchParams } from "@/lib/api";

export default function SearchPage() {
  const [listings, setListings] = useState<Listing[]>([]);
  const [selectedListing, setSelectedListing] = useState<Listing | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [total, setTotal] = useState(0);

  const handleSearch = useCallback(async (params: ListingSearchParams) => {
    setIsLoading(true);
    try {
      const result = await searchListings(params);
      setListings(result.items);
      setTotal(result.total);
    } catch (error) {
      console.error("Search failed:", error);
    } finally {
      setIsLoading(false);
    }
  }, []);

  const handleListingClick = useCallback((listing: Listing) => {
    setSelectedListing(listing);
  }, []);

  return (
    <div className="h-screen flex flex-col">
      {/* Header */}
      <header className="bg-white border-b px-4 py-3">
        <h1 className="text-xl font-bold text-gray-900">PropFair</h1>
      </header>

      {/* Filters */}
      <div className="bg-gray-50 border-b">
        <div className="max-w-screen-2xl mx-auto">
          <ListingFilters onSearch={handleSearch} isLoading={isLoading} />
        </div>
      </div>

      {/* Main content */}
      <div className="flex-1 flex overflow-hidden">
        {/* Listings panel */}
        <div className="w-1/2 overflow-y-auto p-4 space-y-4">
          <p className="text-sm text-gray-500">
            {total} apartamentos encontrados
          </p>
          <div className="grid gap-4">
            {listings.map((listing) => (
              <ListingCard
                key={listing.id}
                listing={listing}
                onClick={() => handleListingClick(listing)}
                isSelected={selectedListing?.id === listing.id}
              />
            ))}
          </div>
          {listings.length === 0 && !isLoading && (
            <div className="text-center py-12 text-gray-500">
              Usa los filtros para buscar apartamentos
            </div>
          )}
        </div>

        {/* Map panel */}
        <div className="w-1/2 relative">
          <MapContainer
            listings={listings}
            onListingClick={handleListingClick}
            selectedListingId={selectedListing?.id}
          />
        </div>
      </div>
    </div>
  );
}
```

**Step 2: Commit**

```bash
git add .
git commit -m "feat(web): add search page with split view"
```

---

## Phase 5: ML Fair Price Model

### Task 5.1: Setup ML Package

**Files:**
- Create: `packages/ml/pyproject.toml`
- Create: `packages/ml/src/propfair_ml/__init__.py`
- Create: `packages/ml/src/propfair_ml/features.py`

**Step 1: Create pyproject.toml**

```toml
[project]
name = "propfair-ml"
version = "0.1.0"
description = "PropFair ML Models"
requires-python = ">=3.12"
dependencies = [
    "pandas>=2.2.0",
    "numpy>=2.0.0",
    "scikit-learn>=1.6.0",
    "xgboost>=2.1.0",
    "shap>=0.46.0",
    "joblib>=1.4.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.3.0",
    "ruff>=0.8.0",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```

**Step 2: Create features.py**

```python
# packages/ml/src/propfair_ml/features.py
import pandas as pd
import numpy as np


FEATURE_COLUMNS = [
    "bedrooms",
    "bathrooms",
    "parking_spaces",
    "area",
    "estrato",
    "floor",
    "building_age",
]


def prepare_features(df: pd.DataFrame) -> pd.DataFrame:
    """Prepare features for model training/inference."""
    features = df[FEATURE_COLUMNS].copy()

    # Fill missing values
    features["estrato"] = features["estrato"].fillna(3)  # Median estrato
    features["floor"] = features["floor"].fillna(1)
    features["building_age"] = features["building_age"].fillna(10)

    # Derived features
    features["price_per_sqm"] = df["price"] / df["area"]
    features["rooms_per_sqm"] = (df["bedrooms"] + df["bathrooms"]) / df["area"]

    return features


def get_feature_names() -> list[str]:
    """Get list of feature names used by model."""
    return FEATURE_COLUMNS + ["price_per_sqm", "rooms_per_sqm"]
```

**Step 3: Commit**

```bash
git add packages/ml/
git commit -m "feat(ml): scaffold ML package with feature engineering"
```

---

### Task 5.2: Create XGBoost Model

**Files:**
- Create: `packages/ml/src/propfair_ml/model.py`
- Create: `packages/ml/tests/test_model.py`

**Step 1: Write the failing test**

```python
import pytest
import pandas as pd
import numpy as np
from propfair_ml.model import FairPriceModel


@pytest.fixture
def sample_data():
    return pd.DataFrame({
        "bedrooms": [2, 3, 1, 2, 3],
        "bathrooms": [1, 2, 1, 2, 2],
        "parking_spaces": [1, 1, 0, 1, 2],
        "area": [60, 80, 45, 70, 90],
        "estrato": [3, 4, 2, 3, 5],
        "floor": [2, 5, 1, 3, 8],
        "building_age": [10, 5, 20, 15, 2],
        "price": [2000000, 3500000, 1200000, 2500000, 4500000],
    })


def test_model_train_and_predict(sample_data):
    model = FairPriceModel()
    model.train(sample_data)

    test_listing = sample_data.iloc[[0]].copy()
    prediction = model.predict(test_listing)

    assert prediction is not None
    assert prediction > 0


def test_model_explain(sample_data):
    model = FairPriceModel()
    model.train(sample_data)

    test_listing = sample_data.iloc[[0]].copy()
    explanation = model.explain(test_listing)

    assert "predicted_price" in explanation
    assert "feature_impacts" in explanation
    assert len(explanation["feature_impacts"]) > 0
```

**Step 2: Run test to verify it fails**

```bash
cd packages/ml
pytest tests/test_model.py -v
```

Expected: FAIL

**Step 3: Write model.py**

```python
# packages/ml/src/propfair_ml/model.py
import pandas as pd
import numpy as np
import xgboost as xgb
import shap
import joblib
from pathlib import Path

from propfair_ml.features import prepare_features, get_feature_names


class FairPriceModel:
    def __init__(self):
        self.model: xgb.XGBRegressor | None = None
        self.explainer: shap.TreeExplainer | None = None
        self.feature_names = get_feature_names()

    def train(self, df: pd.DataFrame) -> None:
        """Train the fair price model."""
        features = prepare_features(df)
        target = df["price"]

        self.model = xgb.XGBRegressor(
            n_estimators=100,
            max_depth=6,
            learning_rate=0.1,
            random_state=42,
        )
        self.model.fit(features, target)
        self.explainer = shap.TreeExplainer(self.model)

    def predict(self, df: pd.DataFrame) -> float:
        """Predict fair price for a listing."""
        if self.model is None:
            raise ValueError("Model not trained")

        features = prepare_features(df)
        prediction = self.model.predict(features)
        return float(prediction[0])

    def explain(self, df: pd.DataFrame) -> dict:
        """Get prediction with SHAP explanation."""
        if self.model is None or self.explainer is None:
            raise ValueError("Model not trained")

        features = prepare_features(df)
        prediction = self.model.predict(features)[0]
        shap_values = self.explainer.shap_values(features)

        # Create feature impact explanation
        feature_impacts = []
        for i, name in enumerate(self.feature_names):
            impact = float(shap_values[0][i])
            feature_impacts.append({
                "feature": name,
                "value": float(features.iloc[0][name]) if name in features.columns else None,
                "impact": impact,
                "direction": "increases" if impact > 0 else "decreases",
            })

        # Sort by absolute impact
        feature_impacts.sort(key=lambda x: abs(x["impact"]), reverse=True)

        return {
            "predicted_price": int(prediction),
            "feature_impacts": feature_impacts[:5],  # Top 5 factors
            "base_value": float(self.explainer.expected_value),
        }

    def save(self, path: str | Path) -> None:
        """Save model to disk."""
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump({"model": self.model, "explainer": self.explainer}, path)

    def load(self, path: str | Path) -> None:
        """Load model from disk."""
        data = joblib.load(path)
        self.model = data["model"]
        self.explainer = data["explainer"]
```

**Step 4: Run test to verify it passes**

```bash
pytest tests/test_model.py -v
```

Expected: PASS

**Step 5: Commit**

```bash
git add .
git commit -m "feat(ml): add XGBoost fair price model with SHAP"
```

---

### Task 5.3: Add Fair Price API Endpoint

**Files:**
- Create: `apps/api/src/propfair_api/routers/analysis.py`
- Create: `apps/api/src/propfair_api/schemas/analysis.py`

**Step 1: Create schemas/analysis.py**

```python
from pydantic import BaseModel


class FeatureImpact(BaseModel):
    feature: str
    value: float | None
    impact: float
    direction: str


class FairPriceResponse(BaseModel):
    listing_id: str
    actual_price: int
    predicted_price: int
    price_difference: int
    price_difference_percent: float
    verdict: str  # "fair", "overpriced", "underpriced"
    feature_impacts: list[FeatureImpact]
```

**Step 2: Create routers/analysis.py**

```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from propfair_api.database import get_db_session
from propfair_api.schemas.analysis import FairPriceResponse, FeatureImpact

router = APIRouter(prefix="/api/v1/analysis", tags=["analysis"])


@router.get("/listings/{listing_id}/fair-price", response_model=FairPriceResponse)
async def get_fair_price(
    listing_id: str,
    db: Session = Depends(get_db_session),
) -> FairPriceResponse:
    # TODO: Implement actual ML prediction
    # For now, return mock data
    return FairPriceResponse(
        listing_id=listing_id,
        actual_price=2500000,
        predicted_price=2100000,
        price_difference=400000,
        price_difference_percent=19.0,
        verdict="overpriced",
        feature_impacts=[
            FeatureImpact(
                feature="estrato",
                value=4,
                impact=-200000,
                direction="decreases",
            ),
            FeatureImpact(
                feature="area",
                value=60,
                impact=150000,
                direction="increases",
            ),
        ],
    )
```

**Step 3: Add router to main.py**

```python
from propfair_api.routers import listings, analysis

app.include_router(analysis.router)
```

**Step 4: Commit**

```bash
git add .
git commit -m "feat(api): add fair price analysis endpoint"
```

---

## Phase 6: Authentication

### Task 6.1: Setup Auth Router

**Files:**
- Create: `apps/api/src/propfair_api/routers/auth.py`
- Create: `apps/api/src/propfair_api/schemas/auth.py`
- Create: `apps/api/src/propfair_api/auth.py`

**Step 1: Create schemas/auth.py**

```python
from pydantic import BaseModel, EmailStr


class UserRegister(BaseModel):
    email: EmailStr
    password: str
    name: str | None = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    id: str
    email: str
    name: str | None

    class Config:
        from_attributes = True
```

**Step 2: Create auth.py (utilities)**

```python
from datetime import datetime, timedelta, timezone
from passlib.context import CryptContext
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from propfair_api.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.access_token_expire_minutes
    )
    to_encode.update({"exp": expire, "type": "access"})
    return jwt.encode(to_encode, settings.secret_key, algorithm="HS256")


def create_refresh_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(
        days=settings.refresh_token_expire_days
    )
    to_encode.update({"exp": expire, "type": "refresh"})
    return jwt.encode(to_encode, settings.secret_key, algorithm="HS256")


async def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=["HS256"])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        return {"id": user_id, "email": payload.get("email")}
    except JWTError:
        raise credentials_exception
```

**Step 3: Create routers/auth.py**

```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from propfair_api.database import get_db_session
from propfair_api.schemas.auth import (
    UserRegister,
    UserLogin,
    Token,
    UserResponse,
)
from propfair_api.auth import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    get_current_user,
)

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


@router.post("/register", response_model=UserResponse)
async def register(
    user_data: UserRegister,
    db: Session = Depends(get_db_session),
) -> UserResponse:
    # TODO: Implement actual user creation
    return UserResponse(
        id="mock-user-id",
        email=user_data.email,
        name=user_data.name,
    )


@router.post("/login", response_model=Token)
async def login(
    user_data: UserLogin,
    db: Session = Depends(get_db_session),
) -> Token:
    # TODO: Implement actual login
    access_token = create_access_token({"sub": "mock-user-id", "email": user_data.email})
    refresh_token = create_refresh_token({"sub": "mock-user-id"})
    return Token(access_token=access_token, refresh_token=refresh_token)


@router.get("/me", response_model=UserResponse)
async def get_me(
    current_user: dict = Depends(get_current_user),
) -> UserResponse:
    return UserResponse(
        id=current_user["id"],
        email=current_user["email"],
        name=None,
    )
```

**Step 4: Add dependencies**

```bash
cd apps/api
pip install passlib[bcrypt] python-jose[cryptography]
```

Update pyproject.toml dependencies.

**Step 5: Commit**

```bash
git add .
git commit -m "feat(api): add authentication with JWT"
```

---

## Phase 7: Favorites

### Task 7.1: Create Favorites Router

**Files:**
- Create: `apps/api/src/propfair_api/routers/favorites.py`

**Step 1: Create favorites.py**

```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from propfair_api.database import get_db_session
from propfair_api.auth import get_current_user
from propfair_api.schemas.listing import ListingResponse, PaginatedListings

router = APIRouter(prefix="/api/v1/user/favorites", tags=["favorites"])


@router.get("", response_model=PaginatedListings)
async def get_favorites(
    page: int = 1,
    page_size: int = 20,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db_session),
) -> PaginatedListings:
    # TODO: Implement actual favorites query
    return PaginatedListings(
        items=[],
        total=0,
        page=page,
        page_size=page_size,
        total_pages=0,
    )


@router.post("/{listing_id}", status_code=status.HTTP_201_CREATED)
async def add_favorite(
    listing_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db_session),
) -> dict:
    # TODO: Implement actual favorite creation
    return {"message": "Favorite added", "listing_id": listing_id}


@router.delete("/{listing_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_favorite(
    listing_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db_session),
) -> None:
    # TODO: Implement actual favorite deletion
    pass
```

**Step 2: Add router to main.py**

**Step 3: Commit**

```bash
git add .
git commit -m "feat(api): add favorites endpoints"
```

---

## Phase 8: Deployment

### Task 8.1: Create Railway Configuration

**Files:**
- Create: `infra/railway/railway.toml`
- Create: `apps/api/Dockerfile`
- Create: `apps/web/Dockerfile`

**Step 1: Create Dockerfiles**

apps/api/Dockerfile:
```dockerfile
FROM python:3.12-slim

WORKDIR /app

RUN pip install uv

COPY pyproject.toml .
RUN uv pip install --system -e ".[dev]"

COPY src/ src/

EXPOSE 8000

CMD ["uvicorn", "propfair_api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

apps/web/Dockerfile:
```dockerfile
FROM node:22-alpine AS builder

WORKDIR /app

RUN corepack enable pnpm

COPY package.json pnpm-lock.yaml ./
RUN pnpm install --frozen-lockfile

COPY . .
RUN pnpm build

FROM node:22-alpine AS runner

WORKDIR /app

ENV NODE_ENV=production

COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static
COPY --from=builder /app/public ./public

EXPOSE 3000

CMD ["node", "server.js"]
```

**Step 2: Create railway.toml**

```toml
[build]
builder = "dockerfile"

[deploy]
healthcheckPath = "/health"
restartPolicyType = "on_failure"
```

**Step 3: Commit**

```bash
git add .
git commit -m "chore: add Railway deployment configuration"
```

---

### Task 8.2: Create GitHub Actions CI

**Files:**
- Create: `.github/workflows/ci.yml`

**Step 1: Create ci.yml**

```yaml
name: CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  lint-and-test-api:
    runs-on: ubuntu-latest
    defaults:
      run:
        working-directory: apps/api
    steps:
      - uses: actions/checkout@v4

      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - name: Install uv
        run: pip install uv

      - name: Install dependencies
        run: uv pip install --system -e ".[dev]"

      - name: Lint with ruff
        run: ruff check .

      - name: Type check with mypy
        run: mypy src/

      - name: Run tests
        run: pytest --cov=src/

  lint-and-test-web:
    runs-on: ubuntu-latest
    defaults:
      run:
        working-directory: apps/web
    steps:
      - uses: actions/checkout@v4

      - name: Setup pnpm
        uses: pnpm/action-setup@v4
        with:
          version: 9

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: "22"
          cache: "pnpm"
          cache-dependency-path: apps/web/pnpm-lock.yaml

      - name: Install dependencies
        run: pnpm install --frozen-lockfile

      - name: Lint
        run: pnpm lint

      - name: Type check
        run: pnpm typecheck

      - name: Build
        run: pnpm build
```

**Step 2: Commit**

```bash
git add .
git commit -m "chore: add GitHub Actions CI workflow"
```

---

## Summary

This plan covers the complete Slice 1 implementation:

1. **Phase 1:** Project scaffolding (monorepo, packages, Docker)
2. **Phase 2:** Scraping pipeline (Scrapy + Finca Raiz spider)
3. **Phase 3:** API endpoints (FastAPI listings)
4. **Phase 4:** Frontend (Next.js + Deck.gl map + search UI)
5. **Phase 5:** ML model (XGBoost + SHAP)
6. **Phase 6:** Authentication (JWT)
7. **Phase 7:** Favorites
8. **Phase 8:** Deployment (Railway + CI/CD)

**Total estimated tasks:** ~25 tasks with ~125 bite-sized steps

Each task follows TDD: write failing test → verify failure → implement → verify pass → commit.
