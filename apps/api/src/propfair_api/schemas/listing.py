from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime


class ListingBase(BaseModel):
    title: str
    description: Optional[str] = None
    price: int
    admin_fee: Optional[int] = None
    bedrooms: int
    bathrooms: int
    parking_spaces: int
    area: float
    estrato: Optional[int] = None
    address: str
    neighborhood: str
    city: str
    latitude: float
    longitude: float


class ListingResponse(ListingBase):
    id: str
    source: str
    url: str
    images: List[str]
    is_active: bool
    first_seen_at: datetime
    last_seen_at: datetime

    class Config:
        from_attributes = True


class ListingSearchParams(BaseModel):
    city: Optional[str] = None
    neighborhood: Optional[str] = None
    min_price: Optional[int] = None
    max_price: Optional[int] = None
    bedrooms: Optional[int] = None
    bathrooms: Optional[int] = None
    min_area: Optional[float] = None
    max_area: Optional[float] = None
    estrato: Optional[int] = None
    page: int = 1
    page_size: int = 20


class PaginatedListings(BaseModel):
    items: List[ListingResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
