from __future__ import annotations

import json
import uuid
from pathlib import Path
from typing import Any

import joblib
import pandas as pd
from fastapi import APIRouter, Depends, HTTPException
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline

from app.config import settings
from app.core.security import current_user
from app.core.storage import connection, decode_json
from app.api.platform import load_dataset, norm
from app.services.analysis_service import analyze_dataset

router = APIRouter()


@router.post("/predict")
def predict(body: dict[str, Any], user: dict = Depends(current_user)):
    customer_id = str(body.get("customer_id", ""))
    features = body.get("features", {})

    records = _customers(customer_id, user)
    customer = next((x for x in records if x["id"] == customer_id), None)

    if not customer:
        raise HTTPException(404, "Customer not found in your uploaded data")

    dataset, frame = load_dataset(customer["dataset_id"], user["sub"])

    # Use analysis service to detect semantic columns and validate availability
    analysis = analyze_dataset(customer["dataset_id"], user["sub"])
    detected = analysis.get("detected", {})
    target = detected.get("churn") or detected.get("fraud")

    if not target:
        return {"available": False, "reason": "This dataset does not contain a suitable churn/fraud target."}

    numeric = [
        str(c)
        for c in frame.select_dtypes(include="number").columns
        if str(c) != target
    ]

    if not numeric:
        return {"available": False, "reason": "The dataset needs numeric feature columns to train predictions."}

    model_dir = Path(settings.upload_dir) / "models"
    model_dir.mkdir(parents=True, exist_ok=True)
    model_path = model_dir / f"{dataset['id']}.joblib"

    if model_path.exists():
        artifact = joblib.load(model_path)
        model = artifact["model"]
        numeric = artifact["features"]
    else:
        y = (
            pd.to_numeric(frame[target], errors="coerce")
            .fillna(0)
            >= 0.5
        ).astype(int)

        if y.nunique() < 2:
            return {"available": False, "reason": "The uploaded target column needs at least two outcome classes to train the model."}

        model = make_pipeline(
            SimpleImputer(strategy="median"),
            LogisticRegression(max_iter=1000, class_weight="balanced"),
        )

        X = frame[numeric].apply(pd.to_numeric, errors="coerce")
        model.fit(X, y)

        joblib.dump(
            {
                "model": model,
                "features": numeric,
            },
            model_path,
        )

    values = features or customer["payload"]
    sample = pd.DataFrame([{c: values.get(c) for c in numeric}])

    probability = float(
        model.predict_proba(sample[numeric].apply(pd.to_numeric, errors="coerce"))[0][1]
    )

    confidence = round(max(probability, 1 - probability), 3)
    prediction = "high_churn_risk" if probability >= 0.5 else "low_churn_risk"
    pid = str(uuid.uuid4())

    coefficients = model.named_steps["logisticregression"].coef_[0]
    explanation = sorted(
        [
            {
                "feature": name,
                "contribution": round(float(coef), 4),
            }
            for name, coef in zip(numeric, coefficients)
        ],
        key=lambda item: abs(item["contribution"]),
        reverse=True,
    )[:5]

    with connection() as conn:
        conn.execute(
            """
            INSERT INTO predictions(
                id,
                customer_id,
                dataset_id,
                prediction,
                probability,
                confidence,
                explanation_json
            ) VALUES(?,?,?,?,?,?,?)
            """,
            (
                pid,
                customer_id,
                customer["dataset_id"],
                prediction,
                probability,
                confidence,
                json.dumps(explanation),
            ),
        )

    return {
        "available": True,
        "id": pid,
        "prediction": prediction,
        "probability": probability,
        "confidence": confidence,
        "explanation": explanation,
        "model": {"features": numeric},
    }


@router.post("/predict/batch")
def predict_batch(body: dict[str, Any], user: dict = Depends(current_user)):
    return [
        predict(
            {
                "customer_id": str(item.get("customer_id", "")),
                "features": item.get("features", {}),
            },
            user,
        )
        for item in body.get("items", [])
    ]


@router.get("/predictions/history")
def prediction_history(user: dict = Depends(current_user)):
    with connection() as conn:
        rows = conn.execute(
            """
            SELECT p.*
            FROM predictions p
            JOIN datasets d
                ON p.dataset_id=d.id
            WHERE d.owner_id=?
            ORDER BY p.created_at DESC
            LIMIT 100
            """,
            (user["sub"],),
        ).fetchall()

    return [
        {
            **dict(r),
            "explanation": decode_json(r["explanation_json"], []),
        }
        for r in rows
    ]


def _customers(customer_id: str, user: dict) -> list[dict[str, Any]]:
    with connection() as conn:
        sql = """
            SELECT c.*
            FROM customers c
            JOIN datasets d
                ON c.dataset_id=d.id
            WHERE d.owner_id=?
        """

        args = [user["sub"]]

        if customer_id:
            sql += """
                AND (
                    c.id LIKE ?
                    OR c.name LIKE ?
                    OR c.email LIKE ?
                    OR c.phone LIKE ?
                )
            """
            args += [f"%{customer_id}%"] * 4

        rows = conn.execute(sql + " LIMIT ?", (*args, 200)).fetchall()

    return [
        {
            **dict(r),
            "payload": decode_json(r["payload_json"], {}),
        }
        for r in rows
    ]
