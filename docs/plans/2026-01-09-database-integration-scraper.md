# Database Integration & Scraper Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Integrate SQLAlchemy models into the API, implement database queries for listings endpoints, validate the FincaRaiz scraper, and connect the scraper to the database.

**Architecture:** SQLAlchemy models mirror Prisma schema for direct database access. API endpoints use SQLAlchemy queries with dynamic filtering and pagination. Scraper DatabasePipeline performs upsert operations and tracks price history.

**Tech Stack:** Python 3.9, FastAPI, SQLAlchemy 2.0, Scrapy, Playwright, PostgreSQL, Prisma (schema only)

---

## Phase 1: SQLAlchemy Models

### Task 1.1: Create Base SQLAlchemy Model

**Files:**
- Create: `apps/api/src/propfair_api/models.py`
- Create: `apps/api/tests/test_models.py`

**Step 1: Write the failing test**

Create `apps/api/tests/test_models.py`:

```python
from datetime import datetime, timezone
from propfair_api.models import Base, Listing


def test_listing_model_creation():
    """Test that Listing model can be instantiated with required fields."""
    listing = Listing(
        id="test_123",
        external_id="ext_123",
        source="fincaraiz",
        url="https://example.com/listing/123",
        title="Test Apartment",
        price=2000000,
        bedrooms=2,
        bathrooms=1,
        parking_spaces=1,
        area=60.0,
        address="Calle 100 #15-20",
        neighborhood="Usaquén",
        city="Bogotá",
        latitude=4.6871,
        longitude=-74.0466,
        images=[],
        amenities=[],
        first_seen_at=datetime.now(timezone.utc),
        last_seen_at=datetime.now(timezone.utc),
        is_active=True,
        content_hash="test_hash",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )

    assert listing.id == "test_123"
    assert listing.source == "fincaraiz"
    assert listing.price == 2000000
    assert listing.city == "Bogotá"


def test_listing_model_tablename():
    """Test that Listing model maps to correct table."""
    assert Listing.__tablename__ == "listings"
```

**Step 2: Run test to verify it fails**

```bash
cd apps/api
source .venv/bin/activate
export DATABASE_URL="postgresql://propfair:propfair_dev@localhost:5432/propfair"
export REDIS_URL="redis://localhost:6379"
export SECRET_KEY="test-secret-key"
pytest tests/test_models.py -v
```

Expected: FAIL with "cannot import name 'Base'" or "cannot import name 'Listing'"

**Step 3: Create models.py with Base and Listing**

Create `apps/api/src/propfair_api/models.py`:

```python
from typing import Optional, List
from datetime import datetime
from sqlalchemy import String, Integer, Float, DateTime, Boolean, ARRAY
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models."""
    pass


class Listing(Base):
    """Listing model representing rental properties."""
    __tablename__ = "listings"

    # Primary key
    id: Mapped[str] = mapped_column(String, primary_key=True)

    # External reference
    external_id: Mapped[str] = mapped_column("external_id", String)
    source: Mapped[str] = mapped_column(String)
    url: Mapped[str] = mapped_column(String)

    # Basic info
    title: Mapped[str] = mapped_column(String)
    description: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    # Pricing
    price: Mapped[int] = mapped_column(Integer)
    admin_fee: Mapped[Optional[int]] = mapped_column("admin_fee", Integer, nullable=True)

    # Property details
    bedrooms: Mapped[int] = mapped_column(Integer)
    bathrooms: Mapped[int] = mapped_column(Integer)
    parking_spaces: Mapped[int] = mapped_column("parking_spaces", Integer)
    area: Mapped[float] = mapped_column(Float)
    estrato: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    floor: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    total_floors: Mapped[Optional[int]] = mapped_column("total_floors", Integer, nullable=True)
    building_age: Mapped[Optional[int]] = mapped_column("building_age", Integer, nullable=True)
    property_condition: Mapped[Optional[str]] = mapped_column("property_condition", String, nullable=True)

    # Location
    address: Mapped[str] = mapped_column(String)
    neighborhood: Mapped[str] = mapped_column(String)
    city: Mapped[str] = mapped_column(String)
    latitude: Mapped[float] = mapped_column(Float)
    longitude: Mapped[float] = mapped_column(Float)

    # Media & amenities
    images: Mapped[List[str]] = mapped_column(ARRAY(String))
    amenities: Mapped[List[str]] = mapped_column(ARRAY(String))

    # Metadata
    first_seen_at: Mapped[datetime] = mapped_column("first_seen_at", DateTime(timezone=True))
    last_seen_at: Mapped[datetime] = mapped_column("last_seen_at", DateTime(timezone=True))
    is_active: Mapped[bool] = mapped_column("is_active", Boolean, default=True)
    content_hash: Mapped[str] = mapped_column("content_hash", String)
    created_at: Mapped[datetime] = mapped_column("created_at", DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column("updated_at", DateTime(timezone=True))


class PriceHistory(Base):
    """Price history for tracking listing price changes."""
    __tablename__ = "price_history"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    listing_id: Mapped[str] = mapped_column("listing_id", String)
    price: Mapped[int] = mapped_column(Integer)
    admin_fee: Mapped[Optional[int]] = mapped_column("admin_fee", Integer, nullable=True)
    recorded_at: Mapped[datetime] = mapped_column("recorded_at", DateTime(timezone=True))
```

**Step 4: Run test to verify it passes**

```bash
pytest tests/test_models.py -v
```

Expected: PASS (2 tests)

**Step 5: Commit**

```bash
git add src/propfair_api/models.py tests/test_models.py
git commit -m "feat(api): add SQLAlchemy models for Listing and PriceHistory"
```

---

## Phase 2: API Database Queries

### Task 2.1: Implement Search Listings Query

**Files:**
- Modify: `apps/api/src/propfair_api/routers/listings.py`
- Modify: `apps/api/tests/test_listings_router.py`

**Step 1: Write the failing test**

Add to `apps/api/tests/test_listings_router.py`:

```python
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timezone

from propfair_api.main import app
from propfair_api.database import get_db_session
from propfair_api.models import Base, Listing


# Test database setup
TEST_DATABASE_URL = "sqlite:///:memory:"
test_engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


def override_get_db():
    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db_session] = override_get_db
client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_database():
    """Create tables before each test and drop after."""
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture
def sample_listings():
    """Create sample listings in the test database."""
    db = TestSessionLocal()

    listings = [
        Listing(
            id="listing_1",
            external_id="ext_1",
            source="fincaraiz",
            url="https://example.com/1",
            title="Apartment in Usaquén",
            price=2000000,
            bedrooms=2,
            bathrooms=1,
            parking_spaces=1,
            area=60.0,
            estrato=3,
            address="Calle 100",
            neighborhood="Usaquén",
            city="Bogotá",
            latitude=4.6871,
            longitude=-74.0466,
            images=[],
            amenities=[],
            first_seen_at=datetime.now(timezone.utc),
            last_seen_at=datetime.now(timezone.utc),
            is_active=True,
            content_hash="hash1",
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        ),
        Listing(
            id="listing_2",
            external_id="ext_2",
            source="fincaraiz",
            url="https://example.com/2",
            title="Studio in Chapinero",
            price=1500000,
            bedrooms=1,
            bathrooms=1,
            parking_spaces=0,
            area=40.0,
            estrato=4,
            address="Carrera 7",
            neighborhood="Chapinero",
            city="Bogotá",
            latitude=4.6097,
            longitude=-74.0817,
            images=[],
            amenities=[],
            first_seen_at=datetime.now(timezone.utc),
            last_seen_at=datetime.now(timezone.utc),
            is_active=True,
            content_hash="hash2",
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        ),
        Listing(
            id="listing_3",
            external_id="ext_3",
            source="fincaraiz",
            url="https://example.com/3",
            title="Penthouse in Rosales",
            price=5000000,
            bedrooms=3,
            bathrooms=3,
            parking_spaces=2,
            area=120.0,
            estrato=6,
            address="Calle 72",
            neighborhood="Rosales",
            city="Bogotá",
            latitude=4.6533,
            longitude=-74.0602,
            images=[],
            amenities=[],
            first_seen_at=datetime.now(timezone.utc),
            last_seen_at=datetime.now(timezone.utc),
            is_active=True,
            content_hash="hash3",
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        ),
    ]

    for listing in listings:
        db.add(listing)
    db.commit()
    db.close()

    return listings


def test_search_listings_no_filters(sample_listings):
    """Test search returns all active listings with no filters."""
    response = client.get("/api/v1/listings")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 3
    assert len(data["items"]) == 3
    assert data["page"] == 1
    assert data["page_size"] == 20


def test_search_listings_with_city_filter(sample_listings):
    """Test search with city filter."""
    response = client.get("/api/v1/listings?city=Bogotá")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 3


def test_search_listings_with_price_range(sample_listings):
    """Test search with price range filter."""
    response = client.get("/api/v1/listings?min_price=1800000&max_price=3000000")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["id"] == "listing_1"


def test_search_listings_with_bedrooms_filter(sample_listings):
    """Test search with bedrooms filter (>= operator)."""
    response = client.get("/api/v1/listings?bedrooms=2")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 2  # listing_1 (2 beds) and listing_3 (3 beds)


def test_search_listings_pagination(sample_listings):
    """Test pagination works correctly."""
    response = client.get("/api/v1/listings?page=1&page_size=2")
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 2
    assert data["total_pages"] == 2
```

**Step 2: Run test to verify it fails**

```bash
pytest tests/test_listings_router.py::test_search_listings_no_filters -v
```

Expected: FAIL - tests will fail because the endpoint still returns mock data

**Step 3: Implement search query in listings router**

Update `apps/api/src/propfair_api/routers/listings.py`:

```python
from typing import Optional
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session

from propfair_api.database import get_db_session
from propfair_api.models import Listing
from propfair_api.schemas.listing import (
    ListingResponse,
    ListingSearchParams,
    PaginatedListings,
)

router = APIRouter(prefix="/api/v1/listings", tags=["listings"])


@router.get("", response_model=PaginatedListings)
async def search_listings(
    city: Optional[str] = Query(None),
    neighborhood: Optional[str] = Query(None),
    min_price: Optional[int] = Query(None),
    max_price: Optional[int] = Query(None),
    bedrooms: Optional[int] = Query(None),
    bathrooms: Optional[int] = Query(None),
    min_area: Optional[float] = Query(None),
    max_area: Optional[float] = Query(None),
    estrato: Optional[int] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db_session),
) -> PaginatedListings:
    """Search listings with optional filters and pagination."""

    # Build dynamic query
    query = db.query(Listing).filter(Listing.is_active == True)

    # Apply filters
    if city:
        query = query.filter(Listing.city.ilike(f"%{city}%"))
    if neighborhood:
        query = query.filter(Listing.neighborhood.ilike(f"%{neighborhood}%"))
    if min_price:
        query = query.filter(Listing.price >= min_price)
    if max_price:
        query = query.filter(Listing.price <= max_price)
    if bedrooms:
        query = query.filter(Listing.bedrooms >= bedrooms)
    if bathrooms:
        query = query.filter(Listing.bathrooms >= bathrooms)
    if min_area:
        query = query.filter(Listing.area >= min_area)
    if max_area:
        query = query.filter(Listing.area <= max_area)
    if estrato:
        query = query.filter(Listing.estrato == estrato)

    # Get total count
    total = query.count()

    # Apply pagination and ordering
    listings = (
        query.order_by(Listing.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    # Calculate total pages
    total_pages = (total + page_size - 1) // page_size if total > 0 else 0

    return PaginatedListings(
        items=[ListingResponse.model_validate(listing) for listing in listings],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@router.get("/{listing_id}", response_model=ListingResponse)
async def get_listing(
    listing_id: str,
    db: Session = Depends(get_db_session),
) -> ListingResponse:
    """Get a single listing by ID."""
    listing = db.query(Listing).filter(
        Listing.id == listing_id,
        Listing.is_active == True
    ).first()

    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")

    return ListingResponse.model_validate(listing)
```

**Step 4: Run test to verify it passes**

```bash
pytest tests/test_listings_router.py -v
```

Expected: PASS (all 5 tests)

**Step 5: Commit**

```bash
git add src/propfair_api/routers/listings.py tests/test_listings_router.py
git commit -m "feat(api): implement database queries for listings search"
```

---

### Task 2.2: Implement Get Single Listing Query

**Files:**
- Already modified in Task 2.1
- Add test: `apps/api/tests/test_listings_router.py`

**Step 1: Write the failing test**

Add to `apps/api/tests/test_listings_router.py`:

```python
def test_get_listing_by_id(sample_listings):
    """Test getting a single listing by ID."""
    response = client.get("/api/v1/listings/listing_1")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "listing_1"
    assert data["title"] == "Apartment in Usaquén"
    assert data["price"] == 2000000


def test_get_listing_not_found():
    """Test 404 when listing doesn't exist."""
    response = client.get("/api/v1/listings/nonexistent")
    assert response.status_code == 404
    assert response.json()["detail"] == "Listing not found"
```

**Step 2: Run test to verify it fails**

```bash
pytest tests/test_listings_router.py::test_get_listing_by_id -v
```

Expected: Should already PASS since we implemented it in Task 2.1

**Step 3: Run test to verify it passes**

```bash
pytest tests/test_listings_router.py::test_get_listing_by_id tests/test_listings_router.py::test_get_listing_not_found -v
```

Expected: PASS (both tests)

**Step 4: Commit**

```bash
git add tests/test_listings_router.py
git commit -m "test(api): add tests for get single listing endpoint"
```

---

## Phase 3: Scraper Validation

### Task 3.1: Inspect FincaRaiz Website and Update Selectors

**Files:**
- Modify: `packages/scrapers/src/propfair_scrapers/spiders/fincaraiz.py`

**Step 1: Manual inspection of FincaRaiz website**

Open browser and navigate to:
```
https://www.fincaraiz.com.co/apartamentos/arriendo/bogota/
```

Using browser DevTools (Right-click → Inspect):
1. Inspect listing card elements
2. Identify CSS selectors for:
   - Listing card links
   - Pagination "next page" button
3. Click into a listing detail page
4. Identify CSS selectors for:
   - Price
   - Bedrooms, bathrooms, parking
   - Area (m²)
   - Address/neighborhood
   - Coordinates (in map element or script tags)
   - Images
   - Description

Document findings in comments in the spider file.

**Step 2: Update CSS selectors based on inspection**

Update `packages/scrapers/src/propfair_scrapers/spiders/fincaraiz.py`:

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
        "CLOSESPIDER_PAGECOUNT": 3,  # Limit to 3 pages for testing
        "LOG_LEVEL": "DEBUG",
    }

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(
                url,
                meta={"playwright": True, "playwright_include_page": True},
                callback=self.parse_listing_page,
            )

    async def parse_listing_page(self, response):
        """Parse search results page to extract listing links."""
        page = response.meta["playwright_page"]

        # Wait for listings to load
        try:
            await page.wait_for_selector("article.card", timeout=5000)
        except Exception as e:
            self.logger.error(f"Timeout waiting for listings: {e}")

        await page.close()

        # Extract listing links - UPDATE THESE SELECTORS BASED ON INSPECTION
        # Example selectors (verify with actual site):
        listing_links = response.css("article.card a.card-link::attr(href)").getall()

        self.logger.info(f"Found {len(listing_links)} listings on page")

        for link in listing_links:
            yield response.follow(
                link,
                meta={"playwright": True, "playwright_include_page": True},
                callback=self.parse_listing_detail,
            )

        # Pagination - UPDATE SELECTOR BASED ON INSPECTION
        next_page = response.css("a.pagination-next::attr(href)").get()
        if next_page:
            self.logger.info(f"Following pagination to: {next_page}")
            yield response.follow(
                next_page,
                meta={"playwright": True, "playwright_include_page": True},
                callback=self.parse_listing_page,
            )

    async def parse_listing_detail(self, response):
        """Parse individual listing detail page."""
        page = response.meta["playwright_page"]

        # Wait for key elements to load
        try:
            await page.wait_for_selector(".price-value", timeout=5000)
        except Exception as e:
            self.logger.error(f"Timeout waiting for listing details: {e}")

        await page.close()

        # Extract external ID from URL
        # Example: https://www.fincaraiz.com.co/.../apartamento-123456
        url_parts = response.url.split("-")
        external_id = url_parts[-1] if url_parts else None

        # Price extraction - UPDATE SELECTOR
        price_text = response.css("span.price-value::text").get()
        price = self._parse_price(price_text) if price_text else None

        # Basic info - UPDATE SELECTORS
        title = response.css("h1.listing-title::text").get()
        description = " ".join(response.css("div.description p::text").getall())

        # Property details - UPDATE SELECTORS
        bedrooms = self._extract_number(response, "habitaciones")
        bathrooms = self._extract_number(response, "baños")
        parking = self._extract_number(response, "garajes")
        area = self._extract_float(response, "área")

        # Location - UPDATE SELECTORS
        neighborhood = response.css("span.neighborhood::text").get()
        address = response.css("span.address::text").get()

        # Coordinates - UPDATE SELECTORS (check map div or script tags)
        lat = response.css("div.map-container::attr(data-lat)").get()
        lng = response.css("div.map-container::attr(data-lng)").get()

        # Additional details - UPDATE SELECTORS
        estrato = self._extract_number(response, "estrato")
        admin_fee_text = response.css("span.admin-fee::text").get()
        admin_fee = self._parse_price(admin_fee_text) if admin_fee_text else None

        # Images - UPDATE SELECTORS
        images = response.css("div.gallery img::attr(src)").getall()

        # Validate we have minimum required fields
        if not all([external_id, price, bedrooms, bathrooms, area, neighborhood, city]):
            self.logger.warning(f"Skipping listing {response.url}: missing required fields")
            return

        yield ListingItem(
            external_id=external_id,
            source="fincaraiz",
            url=response.url,
            title=title.strip() if title else "",
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
            latitude=float(lat) if lat else 4.6097,  # Default to Bogotá center
            longitude=float(lng) if lng else -74.0817,
            images=images,
            amenities=[],
        )

    def _parse_price(self, text: str) -> Optional[int]:
        """Parse Colombian peso price format."""
        if not text:
            return None
        # Remove $ and separators: "$ 2.500.000" -> 2500000
        cleaned = text.replace("$", "").replace(".", "").replace(",", "").strip()
        try:
            return int(cleaned)
        except ValueError:
            self.logger.warning(f"Could not parse price: {text}")
            return None

    def _extract_number(self, response, label: str) -> Optional[int]:
        """Extract number from label-value pairs."""
        # Try various selector patterns
        patterns = [
            f"span:contains('{label}') + span::text",
            f"div:contains('{label}') span.value::text",
            f"li:contains('{label}') span::text",
        ]

        for pattern in patterns:
            value = response.css(pattern).get()
            if value:
                try:
                    return int(value.strip())
                except ValueError:
                    pass
        return None

    def _extract_float(self, response, label: str) -> Optional[float]:
        """Extract float number from label-value pairs."""
        patterns = [
            f"span:contains('{label}') + span::text",
            f"div:contains('{label}') span.value::text",
            f"li:contains('{label}') span::text",
        ]

        for pattern in patterns:
            value = response.css(pattern).get()
            if value:
                cleaned = value.replace("m²", "").replace(",", ".").strip()
                try:
                    return float(cleaned)
                except ValueError:
                    pass
        return None
```

**Step 3: Test scraper with page limit**

```bash
cd packages/scrapers
source .venv/bin/activate
scrapy crawl fincaraiz -o test_output.json -s LOG_LEVEL=DEBUG
```

**Step 4: Inspect output and iterate**

Check `test_output.json`:
- Verify listings were scraped
- Check all required fields are populated
- Verify price, area, coordinates look reasonable
- Check for errors in console output

If selectors are wrong, go back to Step 2 and adjust. Repeat until output looks good.

**Step 5: Commit**

```bash
git add src/propfair_scrapers/spiders/fincaraiz.py
git commit -m "feat(scrapers): update FincaRaiz spider selectors for live site"
```

---

## Phase 4: Database Pipeline

### Task 4.1: Implement DatabasePipeline

**Files:**
- Modify: `packages/scrapers/src/propfair_scrapers/pipelines.py`
- Create: `packages/scrapers/tests/test_database_pipeline.py`

**Step 1: Add SQLAlchemy models to scraper package**

Note: The scraper needs access to the API models. We'll import them by path.

Update `packages/scrapers/src/propfair_scrapers/pipelines.py`:

```python
import hashlib
import json
import os
import sys
from datetime import datetime, timezone
from scrapy.exceptions import DropItem
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add API models to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../../api/src"))

from propfair_api.models import Listing, PriceHistory


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
    """Pipeline to save listings to PostgreSQL database."""

    def __init__(self):
        self.engine = None
        self.Session = None

    def open_spider(self, spider):
        """Initialize database connection when spider opens."""
        database_url = os.getenv("DATABASE_URL")
        if not database_url:
            spider.logger.error("DATABASE_URL not set, database pipeline disabled")
            return

        try:
            self.engine = create_engine(database_url, pool_pre_ping=True)
            self.Session = sessionmaker(bind=self.engine)
            spider.logger.info("Database connection established")
        except Exception as e:
            spider.logger.error(f"Failed to connect to database: {e}")

    def close_spider(self, spider):
        """Close database connection when spider closes."""
        if self.engine:
            self.engine.dispose()
            spider.logger.info("Database connection closed")

    def process_item(self, item, spider):
        """Save or update listing in database."""
        if not self.Session:
            spider.logger.warning("Database not connected, skipping item")
            return item

        session = self.Session()
        try:
            # Check if listing exists
            existing = session.query(Listing).filter_by(
                source=item["source"],
                external_id=item["external_id"]
            ).first()

            if existing:
                self._update_listing(session, existing, item, spider)
            else:
                self._create_listing(session, item, spider)

            session.commit()
            spider.logger.debug(f"Saved listing: {item['external_id']}")

        except Exception as e:
            session.rollback()
            spider.logger.error(f"Failed to save listing {item['external_id']}: {e}")
        finally:
            session.close()

        return item

    def _generate_cuid(self) -> str:
        """Generate a CUID-like ID."""
        import secrets
        timestamp = hex(int(datetime.now(timezone.utc).timestamp() * 1000))[2:]
        random_part = secrets.token_hex(8)
        return f"c{timestamp}{random_part}"

    def _create_listing(self, session, item, spider):
        """Create a new listing in the database."""
        listing = Listing(
            id=self._generate_cuid(),
            external_id=item["external_id"],
            source=item["source"],
            url=item["url"],
            title=item["title"],
            description=item.get("description"),
            price=item["price"],
            admin_fee=item.get("admin_fee"),
            bedrooms=item["bedrooms"],
            bathrooms=item["bathrooms"],
            parking_spaces=item["parking_spaces"],
            area=item["area"],
            estrato=item.get("estrato"),
            floor=item.get("floor"),
            total_floors=item.get("total_floors"),
            building_age=item.get("building_age"),
            property_condition=item.get("property_condition"),
            address=item["address"],
            neighborhood=item["neighborhood"],
            city=item["city"],
            latitude=item["latitude"],
            longitude=item["longitude"],
            images=item.get("images", []),
            amenities=item.get("amenities", []),
            first_seen_at=datetime.now(timezone.utc),
            last_seen_at=datetime.now(timezone.utc),
            is_active=True,
            content_hash=item["content_hash"],
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        session.add(listing)
        spider.logger.info(f"Created new listing: {item['external_id']}")

    def _update_listing(self, session, existing, item, spider):
        """Update an existing listing in the database."""
        # Update last_seen_at
        existing.last_seen_at = datetime.now(timezone.utc)
        existing.updated_at = datetime.now(timezone.utc)

        # Check if price changed
        if existing.price != item["price"]:
            spider.logger.info(
                f"Price change detected for {item['external_id']}: "
                f"{existing.price} → {item['price']}"
            )

            # Create price history record
            price_history = PriceHistory(
                id=self._generate_cuid(),
                listing_id=existing.id,
                price=item["price"],
                admin_fee=item.get("admin_fee"),
                recorded_at=datetime.now(timezone.utc)
            )
            session.add(price_history)

            # Update listing price
            existing.price = item["price"]
            existing.admin_fee = item.get("admin_fee")

        # Update other fields that might change
        existing.title = item["title"]
        existing.description = item.get("description")
        existing.images = item.get("images", [])
        existing.amenities = item.get("amenities", [])
        existing.content_hash = item["content_hash"]

        spider.logger.info(f"Updated existing listing: {item['external_id']}")
```

**Step 2: Write test for DatabasePipeline**

Create `packages/scrapers/tests/test_database_pipeline.py`:

```python
import pytest
from datetime import datetime, timezone
from unittest.mock import Mock, MagicMock
from propfair_scrapers.pipelines import DatabasePipeline
from propfair_scrapers.items import ListingItem


@pytest.fixture
def mock_spider():
    """Create a mock spider."""
    spider = Mock()
    spider.logger = Mock()
    return spider


@pytest.fixture
def sample_item():
    """Create a sample listing item."""
    return ListingItem(
        external_id="test_123",
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
        images=[],
        amenities=[],
        content_hash="test_hash",
    )


def test_database_pipeline_without_connection(mock_spider, sample_item):
    """Test pipeline handles missing database connection gracefully."""
    pipeline = DatabasePipeline()
    # Don't call open_spider, so Session is None

    result = pipeline.process_item(sample_item, mock_spider)

    assert result == sample_item
    mock_spider.logger.warning.assert_called_once()


def test_generate_cuid():
    """Test CUID generation produces valid IDs."""
    pipeline = DatabasePipeline()

    cuid1 = pipeline._generate_cuid()
    cuid2 = pipeline._generate_cuid()

    assert cuid1.startswith("c")
    assert cuid2.startswith("c")
    assert cuid1 != cuid2
    assert len(cuid1) > 10
```

**Step 3: Run test to verify it passes**

```bash
cd packages/scrapers
source .venv/bin/activate
pytest tests/test_database_pipeline.py -v
```

Expected: PASS (2 tests)

**Step 4: Commit**

```bash
git add src/propfair_scrapers/pipelines.py tests/test_database_pipeline.py
git commit -m "feat(scrapers): implement DatabasePipeline with upsert logic"
```

---

## Phase 5: End-to-End Integration

### Task 5.1: Run Full Integration Test

**Files:**
- No code changes, validation only

**Step 1: Start local infrastructure**

```bash
cd infra/docker
docker-compose up -d
```

Wait for services to be healthy:
```bash
docker-compose ps
```

Expected: Both postgres and redis showing "healthy"

**Step 2: Ensure database schema is up to date**

```bash
cd packages/db
pnpm db:push
```

Expected: "The database is already in sync with the Prisma schema"

**Step 3: Run scraper to populate database**

```bash
cd packages/scrapers
source .venv/bin/activate
export DATABASE_URL="postgresql://propfair:propfair_dev@localhost:5432/propfair"
scrapy crawl fincaraiz -s CLOSESPIDER_PAGECOUNT=2
```

Watch the output for:
- Listings being scraped
- "Created new listing" log messages
- Final item count

Expected: 20-40 items scraped and saved to database

**Step 4: Start API server**

In a new terminal:
```bash
cd apps/api
source .venv/bin/activate
export DATABASE_URL="postgresql://propfair:propfair_dev@localhost:5432/propfair"
export REDIS_URL="redis://localhost:6379"
export SECRET_KEY="dev-secret-key"
uvicorn propfair_api.main:app --reload --host 0.0.0.0 --port 8000
```

Expected: Server starts without errors

**Step 5: Test API endpoints with real data**

In another terminal:
```bash
# Test search endpoint
curl "http://localhost:8000/api/v1/listings" | jq '.total'

# Test with filters
curl "http://localhost:8000/api/v1/listings?city=Bogotá&bedrooms=2" | jq '.items | length'

# Get a specific listing (use ID from search results)
curl "http://localhost:8000/api/v1/listings/{listing_id}" | jq '.title'
```

Expected: JSON responses with real scraped data

**Step 6: Verify price history tracking**

Run scraper again with a modified price (manually edit a listing on the site or wait for natural price change):

```bash
scrapy crawl fincaraiz -s CLOSESPIDER_ITEMCOUNT=10
```

Check logs for "Price change detected" messages.

**Step 7: Document results**

Create a summary file documenting:
- Number of listings scraped
- API response times
- Any issues encountered
- Screenshots or sample data

**Step 8: Commit scrapers Python version update**

```bash
git add packages/scrapers/pyproject.toml
git commit -m "fix(scrapers): update Python version requirement to 3.9"
```

---

## Success Criteria

- ✅ SQLAlchemy models created and passing tests
- ✅ API search endpoint returns filtered results from database
- ✅ API pagination works correctly
- ✅ Get single listing endpoint returns 404 for missing listings
- ✅ Scraper successfully fetches 20+ listings from FincaRaiz
- ✅ DatabasePipeline inserts new listings into PostgreSQL
- ✅ Price changes create PriceHistory records
- ✅ End-to-end flow verified: scrape → DB → API → JSON

## Next Steps After Completion

1. Remove `CLOSESPIDER_PAGECOUNT` limit for production scraping
2. Set up cron job or scheduler for daily scraper runs
3. Implement incremental scraping (only fetch new/updated listings)
4. Add scraper monitoring and alerting
5. Optimize database queries with indexes
6. Add Redis caching layer for popular search queries
7. Train ML model on scraped data

## Troubleshooting

**If scraper selectors don't match:**
- Use browser DevTools to inspect live HTML
- Try multiple selector patterns in `_extract_number` and `_extract_float`
- Add wait statements if content loads dynamically
- Check Scrapy logs for CSS selector warnings

**If database connection fails:**
- Verify PostgreSQL is running: `docker-compose ps`
- Check DATABASE_URL format
- Ensure database exists: `psql -U propfair -d propfair -h localhost`
- Check for port conflicts on 5432

**If API tests fail:**
- Verify environment variables are set
- Check SQLAlchemy connection string
- Ensure test database is using SQLite in-memory
- Review test output for specific assertion failures

**If price history not tracking:**
- Verify `PriceHistory` model exists in `models.py`
- Check scraper logs for "Price change detected"
- Query database directly: `SELECT * FROM price_history;`
