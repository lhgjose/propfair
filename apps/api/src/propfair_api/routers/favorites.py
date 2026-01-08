from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from propfair_api.database import get_db_session
from propfair_api.auth import get_current_user
from propfair_api.schemas.listing import PaginatedListings

router = APIRouter(prefix="/api/v1/user/favorites", tags=["favorites"])


@router.get("", response_model=PaginatedListings)
async def get_favorites(
    page: int = 1,
    page_size: int = 20,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db_session),
) -> PaginatedListings:
    # TODO: Implement actual favorites query
    return PaginatedListings(
        items=[],
        total=0,
        page=page,
        page_size=page_size,
        total_pages=0,
    )


@router.post("/{listing_id}", status_code=status.HTTP_201_CREATED)
async def add_favorite(
    listing_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db_session),
) -> dict:
    # TODO: Implement actual favorite creation
    return {"message": "Favorite added", "listing_id": listing_id}


@router.delete("/{listing_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_favorite(
    listing_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db_session),
) -> None:
    # TODO: Implement actual favorite deletion
    pass
