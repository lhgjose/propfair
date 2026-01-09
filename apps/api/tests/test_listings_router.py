import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from datetime import datetime, timezone

from propfair_api.main import app
from propfair_api.database import get_db_session
from propfair_api.models import Base, Listing


# Test database setup - use StaticPool to share connection for in-memory SQLite
TEST_DATABASE_URL = "sqlite:///:memory:"
test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

# Create tables once at module load
Base.metadata.create_all(bind=test_engine)


def override_get_db():
    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db_session] = override_get_db
client = TestClient(app)


@pytest.fixture(autouse=True)
def clear_database():
    """Clear data after each test."""
    yield
    # Clear all listings after test
    db = TestSessionLocal()
    db.query(Listing).delete()
    db.commit()
    db.close()


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
