import pytest
import pandas as pd
import numpy as np
from propfair_ml.model import FairPriceModel


@pytest.fixture
def sample_data():
    return pd.DataFrame({
        "bedrooms": [2, 3, 1, 2, 3],
        "bathrooms": [1, 2, 1, 2, 2],
        "parking_spaces": [1, 1, 0, 1, 2],
        "area": [60, 80, 45, 70, 90],
        "estrato": [3, 4, 2, 3, 5],
        "floor": [2, 5, 1, 3, 8],
        "building_age": [10, 5, 20, 15, 2],
        "price": [2000000, 3500000, 1200000, 2500000, 4500000],
    })


def test_model_train_and_predict(sample_data):
    model = FairPriceModel()
    model.train(sample_data)

    test_listing = sample_data.iloc[[0]].copy()
    prediction = model.predict(test_listing)

    assert prediction is not None
    assert prediction > 0


def test_model_explain(sample_data):
    model = FairPriceModel()
    model.train(sample_data)

    test_listing = sample_data.iloc[[0]].copy()
    explanation = model.explain(test_listing)

    assert "predicted_price" in explanation
    assert "feature_impacts" in explanation
    assert len(explanation["feature_impacts"]) > 0
