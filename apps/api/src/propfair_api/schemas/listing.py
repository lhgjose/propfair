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
