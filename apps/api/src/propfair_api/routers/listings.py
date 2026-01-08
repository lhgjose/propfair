from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from propfair_api.database import get_db_session
from propfair_api.schemas.listing import (
    ListingResponse,
    ListingSearchParams,
    PaginatedListings,
)

router = APIRouter(prefix="/api/v1/listings", tags=["listings"])


@router.get("", response_model=PaginatedListings)
async def search_listings(
    city: str | None = Query(None),
    neighborhood: str | None = Query(None),
    min_price: int | None = Query(None),
    max_price: int | None = Query(None),
    bedrooms: int | None = Query(None),
    bathrooms: int | None = Query(None),
    min_area: float | None = Query(None),
    max_area: float | None = Query(None),
    estrato: int | None = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db_session),
) -> PaginatedListings:
    # TODO: Implement actual DB query
    return PaginatedListings(
        items=[],
        total=0,
        page=page,
        page_size=page_size,
        total_pages=0,
    )


@router.get("/{listing_id}", response_model=ListingResponse)
async def get_listing(
    listing_id: str,
    db: Session = Depends(get_db_session),
) -> ListingResponse:
    # TODO: Implement actual DB query
    raise NotImplementedError()
