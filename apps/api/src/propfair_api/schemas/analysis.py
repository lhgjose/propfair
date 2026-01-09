from typing import Optional, List
from pydantic import BaseModel


class FeatureImpact(BaseModel):
    feature: str
    value: Optional[float]
    impact: float
    direction: str


class FairPriceResponse(BaseModel):
    listing_id: str
    actual_price: int
    predicted_price: int
    price_difference: int
    price_difference_percent: float
    verdict: str  # "fair", "overpriced", "underpriced"
    feature_impacts: List[FeatureImpact]
