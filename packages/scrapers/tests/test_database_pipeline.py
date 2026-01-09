import pytest
import os
import sys
from datetime import datetime, timezone
from unittest.mock import Mock, MagicMock

# Add API models to path before importing pipelines
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../../api/src"))

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
    """Create a sample listing item as dict."""
    return {
        "external_id": "test_123",
        "source": "fincaraiz",
        "url": "https://example.com/123",
        "title": "Test Apartment",
        "price": 2000000,
        "bedrooms": 2,
        "bathrooms": 1,
        "parking_spaces": 1,
        "area": 60.0,
        "address": "Calle 100",
        "neighborhood": "Usaquén",
        "city": "Bogotá",
        "latitude": 4.6871,
        "longitude": -74.0466,
        "images": [],
        "amenities": [],
        "content_hash": "test_hash",
    }


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
