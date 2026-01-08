import pandas as pd
import numpy as np
import xgboost as xgb
import shap
import joblib
from pathlib import Path

from propfair_ml.features import prepare_features, get_feature_names


class FairPriceModel:
    def __init__(self):
        self.model: xgb.XGBRegressor | None = None
        self.explainer: shap.TreeExplainer | None = None
        self.feature_names = get_feature_names()

    def train(self, df: pd.DataFrame) -> None:
        """Train the fair price model."""
        features = prepare_features(df)
        target = df["price"]

        self.model = xgb.XGBRegressor(
            n_estimators=100,
            max_depth=6,
            learning_rate=0.1,
            random_state=42,
        )
        self.model.fit(features, target)
        self.explainer = shap.TreeExplainer(self.model)

    def predict(self, df: pd.DataFrame) -> float:
        """Predict fair price for a listing."""
        if self.model is None:
            raise ValueError("Model not trained")

        features = prepare_features(df)
        prediction = self.model.predict(features)
        return float(prediction[0])

    def explain(self, df: pd.DataFrame) -> dict:
        """Get prediction with SHAP explanation."""
        if self.model is None or self.explainer is None:
            raise ValueError("Model not trained")

        features = prepare_features(df)
        prediction = self.model.predict(features)[0]
        shap_values = self.explainer.shap_values(features)

        # Create feature impact explanation
        feature_impacts = []
        for i, name in enumerate(self.feature_names):
            impact = float(shap_values[0][i])
            feature_impacts.append({
                "feature": name,
                "value": float(features.iloc[0][name]) if name in features.columns else None,
                "impact": impact,
                "direction": "increases" if impact > 0 else "decreases",
            })

        # Sort by absolute impact
        feature_impacts.sort(key=lambda x: abs(x["impact"]), reverse=True)

        return {
            "predicted_price": int(prediction),
            "feature_impacts": feature_impacts[:5],  # Top 5 factors
            "base_value": float(self.explainer.expected_value),
        }

    def save(self, path: str | Path) -> None:
        """Save model to disk."""
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump({"model": self.model, "explainer": self.explainer}, path)

    def load(self, path: str | Path) -> None:
        """Load model from disk."""
        data = joblib.load(path)
        self.model = data["model"]
        self.explainer = data["explainer"]
