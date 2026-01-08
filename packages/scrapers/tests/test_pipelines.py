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
