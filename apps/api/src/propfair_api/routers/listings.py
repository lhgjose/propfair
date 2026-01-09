from typing import Optional
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session

from propfair_api.database import get_db_session
from propfair_api.models import Listing
from propfair_api.schemas.listing import (
    ListingResponse,
    ListingSearchParams,
    PaginatedListings,
)

router = APIRouter(prefix="/api/v1/listings", tags=["listings"])


@router.get("", response_model=PaginatedListings)
async def search_listings(
    city: Optional[str] = Query(None),
    neighborhood: Optional[str] = Query(None),
    min_price: Optional[int] = Query(None),
    max_price: Optional[int] = Query(None),
    bedrooms: Optional[int] = Query(None),
    bathrooms: Optional[int] = Query(None),
    min_area: Optional[float] = Query(None),
    max_area: Optional[float] = Query(None),
    estrato: Optional[int] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db_session),
) -> PaginatedListings:
    """Search listings with optional filters and pagination."""

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
    listings = (
        query.order_by(Listing.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    # Calculate total pages
    total_pages = (total + page_size - 1) // page_size if total > 0 else 0

    return PaginatedListings(
        items=[ListingResponse.model_validate(listing) for listing in listings],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@router.get("/{listing_id}", response_model=ListingResponse)
async def get_listing(
    listing_id: str,
    db: Session = Depends(get_db_session),
) -> ListingResponse:
    """Get a single listing by ID."""
    listing = db.query(Listing).filter(
        Listing.id == listing_id,
        Listing.is_active == True
    ).first()

    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")

    return ListingResponse.model_validate(listing)
