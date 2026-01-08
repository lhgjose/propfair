import pandas as pd


FEATURE_COLUMNS = [
    "bedrooms",
    "bathrooms",
    "parking_spaces",
    "area",
    "estrato",
    "floor",
    "building_age",
]


def prepare_features(df: pd.DataFrame) -> pd.DataFrame:
    """Prepare features for model training/inference."""
    features = df[FEATURE_COLUMNS].copy()

    # Fill missing values
    features["estrato"] = features["estrato"].fillna(3)  # Median estrato
    features["floor"] = features["floor"].fillna(1)
    features["building_age"] = features["building_age"].fillna(10)

    # Derived features
    features["price_per_sqm"] = df["price"] / df["area"]
    features["rooms_per_sqm"] = (df["bedrooms"] + df["bathrooms"]) / df["area"]

    return features


def get_feature_names() -> list[str]:
    """Get list of feature names used by model."""
    return FEATURE_COLUMNS + ["price_per_sqm", "rooms_per_sqm"]
