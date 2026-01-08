from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from propfair_api.database import get_db_session
from propfair_api.schemas.analysis import FairPriceResponse, FeatureImpact

router = APIRouter(prefix="/api/v1/analysis", tags=["analysis"])


@router.get("/listings/{listing_id}/fair-price", response_model=FairPriceResponse)
async def get_fair_price(
    listing_id: str,
    db: Session = Depends(get_db_session),
) -> FairPriceResponse:
    # TODO: Implement actual ML prediction
    # For now, return mock data
    return FairPriceResponse(
        listing_id=listing_id,
        actual_price=2500000,
        predicted_price=2100000,
        price_difference=400000,
        price_difference_percent=19.0,
        verdict="overpriced",
        feature_impacts=[
            FeatureImpact(
                feature="estrato",
                value=4,
                impact=-200000,
                direction="decreases",
            ),
            FeatureImpact(
                feature="area",
                value=60,
                impact=150000,
                direction="increases",
            ),
        ],
    )
