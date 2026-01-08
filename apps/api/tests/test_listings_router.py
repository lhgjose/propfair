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
