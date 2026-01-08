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
