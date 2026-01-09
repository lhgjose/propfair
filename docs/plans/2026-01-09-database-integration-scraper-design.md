# Database Integration & Scraper Implementation Design

**Date:** 2026-01-09
**Status:** Ready for Implementation
**Scope:** Implement SQLAlchemy models, API database queries, and scraper database pipeline

## Overview

Integrate database queries into the FastAPI backend and complete the scraper pipeline to populate the database with real Bogotá apartment listings from FincaRaiz. This connects the previously scaffolded components into a working data pipeline.

## Goals

1. Replace mock data in API endpoints with real database queries
2. Validate FincaRaiz spider CSS selectors against live website
3. Implement database pipeline for scraper to store listings
4. Test end-to-end data flow: scraper → database → API

## Architecture Decisions

### Database Access Strategy

**Chosen: SQLAlchemy Models (Python-native)**

Create SQLAlchemy models that mirror the Prisma schema definition. Both the FastAPI backend and Scrapy pipeline will use SQLAlchemy for database access.

**Rationale:**
- Everything stays in Python (API and scrapers)
- Better performance with direct database access
- SQLAlchemy is battle-tested and mature
- More control over query optimization

**Trade-off:** Need to maintain two schema definitions (Prisma + SQLAlchemy), but we'll generate SQLAlchemy models from Prisma schema to minimize duplication.

### Scraper Testing Scope

**Chosen: Limited Test Scrape (2-3 pages, ~40-60 listings)**

Initial scraper runs will be limited to avoid overwhelming the database or website while validating selectors and data quality.

**Rationale:**
- Quick validation of scraper logic
- Faster iteration if selectors need adjustment
- Sufficient data to test API queries and pagination
- Can easily remove limit for production scraping

### Testing Approach

**Chosen: Hybrid TDD**

- **Database & API:** Full TDD with tests written first
- **Scraper:** Real-world validation first, then unit tests

**Rationale:**
- Database/API benefit from rigorous test coverage
- Scraper needs validation against live site (HTML structure changes frequently)
- Pragmatic balance between test discipline and practical needs

## Component Design

### 1. SQLAlchemy Models

**Location:** `apps/api/src/propfair_api/models.py`

**Structure:**
```python
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, Float, DateTime, Boolean, ARRAY
from datetime import datetime

class Base(DeclarativeBase):
    pass

class Listing(Base):
    __tablename__ = "listings"

    # Primary key
    id: Mapped[str] = mapped_column(String, primary_key=True)

    # External reference
    external_id: Mapped[str] = mapped_column("external_id", String)
    source: Mapped[str] = mapped_column(String)
    url: Mapped[str] = mapped_column(String)

    # Basic info
    title: Mapped[str] = mapped_column(String)
    description: Mapped[str | None] = mapped_column(String, nullable=True)

    # Pricing
    price: Mapped[int] = mapped_column(Integer)
    admin_fee: Mapped[int | None] = mapped_column("admin_fee", Integer, nullable=True)

    # Property details
    bedrooms: Mapped[int] = mapped_column(Integer)
    bathrooms: Mapped[int] = mapped_column(Integer)
    parking_spaces: Mapped[int] = mapped_column("parking_spaces", Integer)
    area: Mapped[float] = mapped_column(Float)
    estrato: Mapped[int | None] = mapped_column(Integer, nullable=True)
    floor: Mapped[int | None] = mapped_column(Integer, nullable=True)
    total_floors: Mapped[int | None] = mapped_column("total_floors", Integer, nullable=True)
    building_age: Mapped[int | None] = mapped_column("building_age", Integer, nullable=True)
    property_condition: Mapped[str | None] = mapped_column("property_condition", String, nullable=True)

    # Location
    address: Mapped[str] = mapped_column(String)
    neighborhood: Mapped[str] = mapped_column(String)
    city: Mapped[str] = mapped_column(String)
    latitude: Mapped[float] = mapped_column(Float)
    longitude: Mapped[float] = mapped_column(Float)

    # Media & amenities
    images: Mapped[list[str]] = mapped_column(ARRAY(String))
    amenities: Mapped[list[str]] = mapped_column(ARRAY(String))

    # Metadata
    first_seen_at: Mapped[datetime] = mapped_column("first_seen_at", DateTime(timezone=True))
    last_seen_at: Mapped[datetime] = mapped_column("last_seen_at", DateTime(timezone=True))
    is_active: Mapped[bool] = mapped_column("is_active", Boolean, default=True)
    content_hash: Mapped[str] = mapped_column("content_hash", String)
    created_at: Mapped[datetime] = mapped_column("created_at", DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column("updated_at", DateTime(timezone=True))

    # Relationships
    price_history: Mapped[list["PriceHistory"]] = relationship(back_populates="listing")
    favorites: Mapped[list["Favorite"]] = relationship(back_populates="listing")
```

**Key Design Points:**
- Use column names that match Prisma `@map` directives (snake_case)
- All datetime fields use `timezone=True` for PostgreSQL
- Arrays stored as PostgreSQL ARRAY type
- Unique constraint on `(source, external_id)` handled at database level (Prisma)

### 2. API Database Queries

**Location:** `apps/api/src/propfair_api/routers/listings.py`

**Search Listings Endpoint:**

```python
@router.get("", response_model=PaginatedListings)
async def search_listings(...):
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
    listings = query.order_by(Listing.created_at.desc()) \
                    .offset((page - 1) * page_size) \
                    .limit(page_size) \
                    .all()

    # Calculate total pages
    total_pages = (total + page_size - 1) // page_size

    return PaginatedListings(
        items=[ListingResponse.model_validate(listing) for listing in listings],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )
```

**Get Single Listing Endpoint:**

```python
@router.get("/{listing_id}", response_model=ListingResponse)
async def get_listing(listing_id: str, db: Session = Depends(get_db_session)):
    listing = db.query(Listing).filter(
        Listing.id == listing_id,
        Listing.is_active == True
    ).first()

    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")

    return ListingResponse.model_validate(listing)
```

**Query Design Decisions:**
- ILIKE for case-insensitive city/neighborhood search
- ">=" for bedrooms/bathrooms (means "X or more")
- Exact match for estrato
- Only return active listings
- Order by newest first (created_at DESC)
- Use Pydantic's `model_validate()` for ORM conversion

### 3. Scraper Database Pipeline

**Location:** `packages/scrapers/src/propfair_scrapers/pipelines.py`

**DatabasePipeline Implementation:**

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timezone
import os

class DatabasePipeline:
    def __init__(self):
        self.engine = None
        self.Session = None

    def open_spider(self, spider):
        database_url = os.getenv("DATABASE_URL")
        self.engine = create_engine(database_url, pool_pre_ping=True)
        self.Session = sessionmaker(bind=self.engine)
        spider.logger.info("Database connection established")

    def close_spider(self, spider):
        if self.engine:
            self.engine.dispose()
            spider.logger.info("Database connection closed")

    def process_item(self, item, spider):
        session = self.Session()
        try:
            # Check if listing exists
            existing = session.query(Listing).filter_by(
                source=item['source'],
                external_id=item['external_id']
            ).first()

            if existing:
                # Update existing listing
                self._update_listing(session, existing, item, spider)
            else:
                # Create new listing
                self._create_listing(session, item, spider)

            session.commit()
            spider.logger.debug(f"Saved listing: {item['external_id']}")

        except Exception as e:
            session.rollback()
            spider.logger.error(f"Failed to save listing {item['external_id']}: {e}")
        finally:
            session.close()

        return item

    def _create_listing(self, session, item, spider):
        listing = Listing(
            id=item.get('id', self._generate_cuid()),
            external_id=item['external_id'],
            source=item['source'],
            url=item['url'],
            title=item['title'],
            description=item.get('description'),
            price=item['price'],
            admin_fee=item.get('admin_fee'),
            bedrooms=item['bedrooms'],
            bathrooms=item['bathrooms'],
            parking_spaces=item['parking_spaces'],
            area=item['area'],
            estrato=item.get('estrato'),
            floor=item.get('floor'),
            total_floors=item.get('total_floors'),
            building_age=item.get('building_age'),
            property_condition=item.get('property_condition'),
            address=item['address'],
            neighborhood=item['neighborhood'],
            city=item['city'],
            latitude=item['latitude'],
            longitude=item['longitude'],
            images=item.get('images', []),
            amenities=item.get('amenities', []),
            first_seen_at=datetime.now(timezone.utc),
            last_seen_at=datetime.now(timezone.utc),
            is_active=True,
            content_hash=item['content_hash'],
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        session.add(listing)

    def _update_listing(self, session, existing, item, spider):
        # Update last_seen_at
        existing.last_seen_at = datetime.now(timezone.utc)
        existing.updated_at = datetime.now(timezone.utc)

        # Check if price changed
        if existing.price != item['price']:
            spider.logger.info(
                f"Price change detected for {item['external_id']}: "
                f"{existing.price} → {item['price']}"
            )
            # Create price history record
            price_history = PriceHistory(
                listing_id=existing.id,
                price=item['price'],
                admin_fee=item.get('admin_fee'),
                recorded_at=datetime.now(timezone.utc)
            )
            session.add(price_history)

            # Update listing price
            existing.price = item['price']
            existing.admin_fee = item.get('admin_fee')

        # Update other fields that might change
        existing.title = item['title']
        existing.description = item.get('description')
        existing.images = item.get('images', [])
        existing.amenities = item.get('amenities', [])
        existing.content_hash = item['content_hash']
```

**Pipeline Design Decisions:**
- Connection pooling for efficiency
- Graceful error handling (log but don't crash)
- Upsert logic based on (source, external_id)
- Track price changes in PriceHistory
- Update last_seen_at on every scrape
- Use timezone-aware datetimes (UTC)

### 4. Scraper Validation

**Approach:**

1. **Manual Site Inspection:**
   - Visit https://www.fincaraiz.com.co/apartamentos/arriendo/bogota/
   - Use browser DevTools to inspect HTML structure
   - Identify CSS selectors for:
     - Listing cards/links
     - Pagination controls
     - Detail page fields (price, beds, baths, area, etc.)

2. **Update CSS Selectors:**
   - Current selectors are placeholders
   - Replace with actual selectors from live site
   - May need to use Playwright wait functions for dynamic content

3. **Test Configuration:**
   - Add to `settings.py`:
     ```python
     CLOSESPIDER_PAGECOUNT = 3  # Limit to 3 pages
     CLOSESPIDER_ITEMCOUNT = 50  # Backup limit
     LOG_LEVEL = 'DEBUG'  # Verbose logging for first run
     ```

4. **Test Command:**
   ```bash
   cd packages/scrapers
   scrapy crawl fincaraiz -o test_output.json
   ```

5. **Validation Checklist:**
   - [ ] Scraper fetches listing URLs from search page
   - [ ] Pagination works (moves to page 2, 3)
   - [ ] All required fields populated in output JSON
   - [ ] No excessive errors/drops in logs
   - [ ] Price, area, coordinates look reasonable

### 5. Testing Strategy

**API Layer (TDD):**

1. **Model Tests** (`apps/api/tests/test_models.py`):
   ```python
   def test_listing_creation():
       listing = Listing(
           id="test123",
           external_id="ext123",
           source="fincaraiz",
           # ... all required fields
       )
       # Verify fields set correctly

   def test_listing_relationships():
       # Test price_history relationship
       # Test favorites relationship
   ```

2. **Query Tests** (`apps/api/tests/test_listings_router.py`):
   ```python
   def test_search_listings_with_filters():
       # Mock database with test data
       response = client.get("/api/v1/listings?city=Bogotá&bedrooms=2")
       assert response.status_code == 200
       # Verify filters applied

   def test_search_listings_pagination():
       # Test offset/limit logic

   def test_get_listing_not_found():
       response = client.get("/api/v1/listings/nonexistent")
       assert response.status_code == 404
   ```

**Scraper Layer (Validation-first):**

1. **Manual Validation:**
   - Run spider with page limit
   - Inspect JSON output for completeness
   - Check logs for errors

2. **Unit Tests After Validation** (`packages/scrapers/tests/test_fincaraiz_spider.py`):
   ```python
   def test_parse_price():
       spider = FincaRaizSpider()
       assert spider._parse_price("$ 2.500.000") == 2500000

   def test_extract_number():
       # Test helper methods with various inputs
   ```

3. **Pipeline Tests** (`packages/scrapers/tests/test_database_pipeline.py`):
   ```python
   def test_create_new_listing():
       # Test insert logic with mock session

   def test_update_existing_listing():
       # Test upsert logic

   def test_price_history_creation():
       # Verify price changes tracked
   ```

## Implementation Workflow

### Phase 1: Database Layer (TDD)
1. Create `models.py` with SQLAlchemy models
2. Write model tests → implement → verify pass
3. Update `database.py` if needed (import models)

### Phase 2: API Queries (TDD)
1. Write endpoint tests for search and get_listing
2. Implement database queries in `listings.py`
3. Verify all tests pass
4. Manual API testing with curl/Postman

### Phase 3: Scraper Validation (Real-world)
1. Inspect FincaRaiz website manually
2. Update CSS selectors in `fincaraiz.py`
3. Run test scrape with page limits
4. Verify JSON output quality
5. Iterate on selectors if needed

### Phase 4: Database Pipeline
1. Implement `DatabasePipeline` in `pipelines.py`
2. Add `PriceHistory` model to `models.py`
3. Write pipeline tests → implement → verify
4. Test with scraper (dry run first)

### Phase 5: End-to-End Integration
1. Ensure PostgreSQL is running
2. Run Prisma migrations: `pnpm db:push`
3. Run scraper to populate database
4. Start API server
5. Test API endpoints return real data
6. Verify price history tracking works

## Data Flow

```
FincaRaiz Website
    ↓ (Scrapy + Playwright)
ListingItem (raw scraped data)
    ↓ (ValidationPipeline - check required fields)
Validated Item
    ↓ (DeduplicationPipeline - hash-based dedup)
Deduplicated Item
    ↓ (DatabasePipeline - upsert to PostgreSQL)
PostgreSQL listings table
    ↓ (SQLAlchemy queries in FastAPI)
ListingResponse (Pydantic schema)
    ↓ (JSON serialization)
Frontend via HTTP API
```

## Environment Setup

**Prerequisites:**
1. PostgreSQL running (via Docker Compose)
2. Prisma schema pushed to database: `cd packages/db && pnpm db:push`
3. API dependencies installed: `cd apps/api && pip install -e ".[dev]"`
4. Scraper dependencies installed: `cd packages/scrapers && pip install -e ".[dev]"`
5. Playwright browsers installed: `playwright install`

**Environment Variables:**

Both API and scraper need:
```env
DATABASE_URL="postgresql://propfair:propfair_dev@localhost:5432/propfair"
```

API also needs:
```env
REDIS_URL="redis://localhost:6379"
SECRET_KEY="your-secret-key"
```

## Success Criteria

- [ ] SQLAlchemy models created and tested
- [ ] API endpoints return real data from PostgreSQL
- [ ] Search filters work correctly (city, price, bedrooms, etc.)
- [ ] Pagination works with accurate total counts
- [ ] Scraper successfully scrapes 40-60 listings from FincaRaiz
- [ ] Database pipeline inserts new listings
- [ ] Price changes tracked in PriceHistory table
- [ ] End-to-end flow: scrape → DB → API → JSON response
- [ ] All tests pass (API unit + integration tests)

## Future Enhancements

- Add geospatial queries (PostGIS) for radius-based search
- Implement incremental scraping (only fetch new/updated listings)
- Add scraper scheduling (daily runs)
- Expand to other sources (Metrocuadrado, Cien Cuadras)
- Add data quality monitoring (track scraper success rates)
- Implement scraper retry logic for failed pages
- Add API caching layer (Redis) for popular queries

## References

- Prisma Schema: `packages/db/prisma/schema.prisma`
- Slice 1 Plan: `docs/plans/2026-01-07-slice-1-bogota-apartments.md`
- Scrapy Documentation: https://docs.scrapy.org/
- SQLAlchemy 2.0 Documentation: https://docs.sqlalchemy.org/
