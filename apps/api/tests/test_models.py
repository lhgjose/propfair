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
