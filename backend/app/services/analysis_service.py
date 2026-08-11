from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

import pandas as pd

try:
    from app.api.platform import load_dataset
except Exception:
    # avoid import-time dependency on FastAPI when running offline tests
    load_dataset = None


SEMANTIC_CANDIDATES = {
    "customer_id": ["customer_id", "customerid", "customer", "customer_number", "user_id", "user", "employee_id", "employee", "id"],
    "name": ["name", "full_name", "customer_name", "employee_name"],
    "money": ["revenue", "sales", "amount", "total_amount", "purchase_amount", "spend", "salary", "income", "compensation", "price"],
    "date": ["date", "created_at", "updated_at", "transaction_date", "purchase_date", "order_date", "timestamp"],
    "churn": ["churn", "churned", "is_churned", "churn_flag"],
    "fraud": ["fraud", "is_fraud", "fraud_flag", "fraudulent", "risk"],
    "category": ["category", "segment", "department", "type", "group"],
    "location": ["city", "state", "country", "region"],
}


def _normalize(name: str) -> str:
    return str(name).lower().replace(" ", "_")


def detect_semantic_columns(df: pd.DataFrame) -> dict[str, Optional[str]]:
    cols = { _normalize(c): str(c) for c in df.columns }

    detected: dict[str, Optional[str]] = {}

    for key, candidates in SEMANTIC_CANDIDATES.items():
        found = None
        # Prefer exact name matches
        for alias in candidates:
            if _normalize(alias) in cols:
                # basic type validation
                col_name = cols[_normalize(alias)]
                ser = df[col_name]
                if key == "money":
                    # prefer numeric-like columns
                    if pd.api.types.is_numeric_dtype(ser) or ser.astype(str).str.replace("[^0-9.-]", "", regex=True).str.len().gt(0).any():
                        found = col_name
                        break
                elif key == "date":
                    try:
                        parsed = pd.to_datetime(ser, errors="coerce")
                        if parsed.notna().sum() > 0:
                            found = col_name
                            break
                    except Exception:
                        continue
                else:
                    found = col_name
                    break

        # fallback: attempt fuzzy match by presence of keyword in any column name
        if not found:
            for col in df.columns:
                lname = _normalize(col)
                if any(_normalize(cand) in lname for cand in candidates):
                    found = str(col)
                    break

        detected[key] = found

    return detected


def classify_columns(df: pd.DataFrame) -> dict[str, list[str]]:
    """Return lists of numeric, categorical, datetime and identifier columns."""
    numeric: list[str] = []
    categorical: list[str] = []
    datetime_cols: list[str] = []
    identifier: list[str] = []

    for col in df.columns:
        name = str(col)
        nname = _normalize(name)

        # identifier heuristics
        if nname == "id" or nname.endswith("_id") or "uuid" in nname or (nname.endswith("id") and len(nname) <= 10):
            identifier.append(name)
            continue

        ser = df[col]

        # numeric detection: either numeric dtype or many convertible numeric values
        if pd.api.types.is_numeric_dtype(ser):
            numeric.append(name)
            continue

        coerced = pd.to_numeric(ser, errors="coerce")
        if coerced.notna().sum() >= max(1, len(ser) * 0.5):
            numeric.append(name)
            continue

        # datetime detection (after numeric detection to avoid parsing numbers as years)
        try:
            parsed = pd.to_datetime(ser, errors="coerce")
            # crude sanity: consider datetime only if many values parsed and years are reasonable
            if parsed.notna().sum() > max(1, len(ser) * 0.05):
                years = parsed.dt.year.dropna()
                if not years.empty:
                    ymean = int(years.mean())
                    if 1800 < ymean < 2100:
                        datetime_cols.append(name)
                        continue
        except Exception:
            pass

        # categorical: object-like with moderate cardinality
        uniques = ser.dropna().astype(str).nunique()
        if uniques <= max(50, max(5, int(len(ser) * 0.5))):
            categorical.append(name)
        else:
            # high-cardinality non-numeric is likely identifier
            identifier.append(name)

    return {
        "numeric": numeric,
        "categorical": categorical,
        "datetime": datetime_cols,
        "identifier": identifier,
    }


def compute_metrics(df: pd.DataFrame, detected: dict[str, Optional[str]]) -> dict[str, Any]:
    metrics: dict[str, Any] = {}

    metrics["records"] = {"value": int(len(df)), "available": True}

    # unique customers/employees/users
    cid = detected.get("customer_id")
    if cid:
        metrics["unique_customers"] = {"value": int(df[cid].nunique()), "available": True}
    else:
        metrics["unique_customers"] = {"value": None, "available": False, "reason": "No customer identifier column found."}

    # money summary
    money = detected.get("money")
    if money:
        ser = pd.to_numeric(df[money], errors="coerce").fillna(0)
        metrics["revenue"] = {"value": float(ser.sum()), "available": True}
        metrics["average_money"] = {"value": float(ser.mean()), "available": True}
        metrics["min_money"] = {"value": float(ser.min()), "available": True}
        metrics["max_money"] = {"value": float(ser.max()), "available": True}
    else:
        metrics["revenue"] = {"value": None, "available": False, "reason": "No revenue/sales column found in this dataset."}
        metrics["average_money"] = {"value": None, "available": False, "reason": "No revenue/sales column found in this dataset."}

    # churn
    churn = detected.get("churn")
    if churn:
        ser = pd.to_numeric(df[churn], errors="coerce")
        if ser.notna().sum() > 0:
            rate = float((ser.fillna(0) >= 0.5).sum()) / max(1, int(len(df)))
            metrics["churn_rate"] = {"value": rate, "available": True}
        else:
            metrics["churn_rate"] = {"value": None, "available": False, "reason": "Churn column exists but contains no numeric values."}
    else:
        metrics["churn_rate"] = {"value": None, "available": False, "reason": "No churn target column found."}

    # fraud
    fraud = detected.get("fraud")
    if fraud:
        ser = pd.to_numeric(df[fraud], errors="coerce").fillna(0)
        metrics["fraud_count"] = {"value": int((ser >= 0.5).sum()), "available": True}
    else:
        metrics["fraud_count"] = {"value": None, "available": False, "reason": "No fraud/risk column found."}

    # missing values
    metrics["missing_values"] = {"value": int(df.isna().sum().sum()), "available": True}

    # category counts
    category = detected.get("category")
    if category:
        metrics["categories"] = {"value": int(df[category].nunique()), "available": True}
    else:
        metrics["categories"] = {"value": None, "available": False, "reason": "No category-like column found."}

    return metrics


def generate_charts(df: pd.DataFrame, detected: dict[str, Optional[str]]) -> List[dict[str, Any]]:
    charts: List[dict[str, Any]] = []

    cols = classify_columns(df)
    numeric = cols["numeric"]
    categorical = cols["categorical"]
    datetimes = cols["datetime"]
    identifiers = set(cols["identifier"])  # don't use these in analysis

    # helper to avoid identifier usage
    def usable(col: str) -> bool:
        return col and col not in identifiers

    # 1. Date + numeric => time series (one per numeric, prefer semantic money/aqi)
    if datetimes and numeric:
        date_col = datetimes[0]
        # prioritize numerics that are money/aqi/pm/temperature/humidity
        priority_keywords = ["revenue", "sales", "amount", "price", "salary", "income", "aqi", "pm25", "pm10", "temperature", "temp", "humidity"]
        def priority_score(nc: str) -> int:
            ln = _normalize(nc)
            return sum(1 for k in priority_keywords if k in ln)

        numerics_sorted = sorted([n for n in numeric if usable(n)], key=lambda x: -priority_score(x))
        for n in numerics_sorted[:3]:
            tmp = pd.DataFrame({
                "date": pd.to_datetime(df[date_col], errors="coerce"),
                "value": pd.to_numeric(df[n], errors="coerce"),
            }).dropna()
            if tmp.empty:
                continue
            series = [ {"period": str(period), "value": float(value)} for period, value in tmp.groupby(tmp.date.dt.to_period("M")).value.sum().items() ]
            charts.append({"type": "line", "title": f"{n} over time", "x_key": "period", "y_key": "value", "data": series})

    # 2. Category + numeric => bar (aggregate mean or sum)
    if categorical and numeric:
        # choose best category (prefer 'category','department','segment','country','city')
        cat_priority = ["category", "department", "segment", "team", "type", "country", "city", "region"]
        def cat_score(c: str) -> int:
            ln = _normalize(c)
            return sum(1 for k in cat_priority if k in ln)

        cats_sorted = sorted([c for c in categorical if usable(c)], key=lambda x: -cat_score(x))
        # choose numeric priority as above
        num_priority = ["revenue", "sales", "amount", "price", "salary", "income", "aqi", "pm25", "pm10"]
        def num_score(n: str) -> int:
            ln = _normalize(n)
            return sum(1 for k in num_priority if k in ln)

        nums_sorted = sorted([n for n in numeric if usable(n)], key=lambda x: -num_score(x))

        if cats_sorted and nums_sorted:
            c = cats_sorted[0]
            n = nums_sorted[0]
            temp = df[[c, n]].copy()
            temp[n] = pd.to_numeric(temp[n], errors="coerce")
            temp = temp.dropna(subset=[n])
            if not temp.empty:
                grouped = temp.groupby(temp[c].fillna("Unknown").astype(str))[n].mean().sort_values(ascending=False).head(10)
                charts.append({"type": "bar", "title": f"Average {n} by {c}", "x_key": c, "y_key": "value", "data": [{c: str(k), "value": float(v)} for k, v in grouped.items()]})
            # also include counts by category as a useful companion chart
            counts = temp[c].fillna("Unknown").astype(str).value_counts().head(10)
            charts.append({"type": "bar", "title": f"{c} distribution (count)", "x_key": c, "y_key": "count", "data": [{c: str(k), "count": int(v)} for k, v in counts.items()]})

    # 3. Single numeric -> distribution histogram
    if numeric:
        # choose a numeric that is not identifier and has sufficient cardinality
        candidates = [n for n in numeric if usable(n)]
        hist_chosen = None
        # prefer semantically meaningful numerics (salary/revenue) for distribution
        num_priority = ["revenue", "sales", "amount", "price", "salary", "income", "aqi", "pm25", "pm10"]
        def num_score_local(n: str) -> int:
            ln = _normalize(n)
            return sum(1 for k in num_priority if k in ln)

        candidates_sorted = sorted(candidates, key=lambda x: -num_score_local(x))
        for n in candidates_sorted:
            vals = pd.to_numeric(df[n], errors="coerce").dropna()
            if len(vals.unique()) >= 5 and len(vals) >= 5:
                hist_chosen = n
                break
        if hist_chosen:
            vals = pd.to_numeric(df[hist_chosen], errors="coerce").dropna()
            try:
                bins = pd.cut(vals, bins=10)
                counts = bins.value_counts().sort_index()
                data = [{"bin": str(idx), "count": int(v)} for idx, v in counts.items()]
                charts.append({"type": "bar", "title": f"{hist_chosen} distribution", "x_key": "bin", "y_key": "count", "data": data})
            except Exception:
                pass

    # 4. Numeric vs numeric -> scatter (score pairs, avoid id and lat/lon)
    # avoid using latitude/longitude as default scatter
    lat_names = {"lat", "latitude"}
    lon_names = {"lon", "lng", "longitude"}
    def is_latlon_pair(a: str, b: str) -> bool:
        na = _normalize(a)
        nb = _normalize(b)
        return (na in lat_names and nb in lon_names) or (na in lon_names and nb in lat_names)

    num_pairs: list[tuple[str, str, int]] = []
    for i in range(len(numeric)):
        for j in range(i + 1, len(numeric)):
            a = numeric[i]
            b = numeric[j]
            if not usable(a) or not usable(b):
                continue
            if is_latlon_pair(a, b):
                continue
            # avoid identifiers
            vals = df[[a, b]].dropna()
            if vals.empty:
                continue
            # score based on semantic relevance (e.g., aqi vs temperature), and uniqueness
            score = 0
            an = _normalize(a)
            bn = _normalize(b)
            if any(k in an for k in ["aqi", "pm25", "pm10", "temperature", "temp", "humidity", "salary", "income"]):
                score += 2
            if any(k in bn for k in ["aqi", "pm25", "pm10", "temperature", "temp", "humidity", "salary", "income"]):
                score += 2
            # penalize id-like
            if an.endswith("id") or bn.endswith("id"):
                score -= 5
            # prefer columns with many distinct values
            score += int(vals.shape[0] / 100)
            num_pairs.append((a, b, score))

    num_pairs = sorted(num_pairs, key=lambda x: -x[2])
    for a, b, s in num_pairs[:2]:
        scatter = df[[a, b]].dropna().head(500)
        if not scatter.empty:
            charts.append({"type": "scatter", "title": f"{b} vs {a}", "x_key": a, "y_key": b, "data": scatter.to_dict(orient="records")})

    # final: limit number of charts to avoid overwhelming frontend
    if len(charts) > 6:
        charts = charts[:6]

    return charts


def generate_insights(df: pd.DataFrame, detected: dict[str, Optional[str]], source: Optional[str] = None) -> List[dict[str, Any]]:
    insights: List[dict[str, Any]] = []
    # Use metrics to derive simple, factual insights
    metrics = compute_metrics(df, detected)

    # top category
    category = detected.get("category")
    if category:
        top = df[category].fillna("Unknown").astype(str).value_counts().head(1)
        if not top.empty:
            name = top.index[0]
            count = int(top.iloc[0])
            insights.append({
                "title": f"Dominant {category}: {name}",
                "description": f"{count} records belong to {name} in column {category}.",
                "metric": "category_dominance",
                "value": count,
                "source": source,
            })

    # money-driven insights
    money = detected.get("money")
    date = detected.get("date")
    if money:
        ser = pd.to_numeric(df[money], errors="coerce").dropna()
        if not ser.empty:
            top_idx = ser.idxmax()
            top_val = float(ser.max())
            insights.append({
                "title": f"Highest {money}",
                "description": f"Maximum {money} value is {top_val}.",
                "metric": "max_money",
                "value": top_val,
                "source": source,
            })
            if date:
                tmp = pd.DataFrame({"date": pd.to_datetime(df[date], errors="coerce"), "value": ser}).dropna()
                if not tmp.empty:
                    recent = tmp.sort_values("date", ascending=False).head(1)
                    if not recent.empty:
                        insights.append({"title": f"Most recent {money} record", "description": f"Most recent {money} at {recent.iloc[0]["date"]}: {recent.iloc[0]["value"]}", "metric": "recent_money", "value": float(recent.iloc[0]["value"]), "source": source})

    # churn concentration
    churn = detected.get("churn")
    if churn:
        ser = pd.to_numeric(df[churn], errors="coerce").fillna(0)
        if ser.sum() > 0:
            pct = float((ser >= 0.5).sum()) / max(1, int(len(df)))
            insights.append({"title": "Churn concentration", "description": f"{pct*100:.1f}% of records indicate churn (>=0.5).", "metric": "churn_rate", "value": pct, "source": source})

    # Air quality / sensor-driven insights
    # Detect common pollutant columns by name
    pollutant_aliases = {
        "aqi": ["aqi", "air_quality", "airquality"],
        "pm25": ["pm25", "pm_25", "pm_2_5"],
        "pm10": ["pm10", "pm_10"],
        "no2": ["no2"],
        "so2": ["so2"],
        "o3": ["o3"],
        "co": ["co"],
        "temperature": ["temperature", "temp"],
        "humidity": ["humidity"],
    }

    # helper to find column by aliases
    def _find_alias(aliases: list[str]) -> Optional[str]:
        for a in aliases:
            for col in df.columns:
                if _normalize(col) == _normalize(a) or _normalize(a) in _normalize(col):
                    return str(col)
        return None

    location_col = detected.get("location")

    for key, aliases in pollutant_aliases.items():
        col = _find_alias(aliases)
        if col and pd.api.types.is_numeric_dtype(df[col]):
            vals = pd.to_numeric(df[col], errors="coerce").dropna()
            if vals.empty:
                continue
            insights.append({
                "title": f"Average {key}",
                "description": f"Average {key} is {vals.mean():.2f}.",
                "metric": f"avg_{key}",
                "value": float(vals.mean()),
                "source": source,
            })

            # highest location if location column exists
            if location_col:
                idx = vals.idxmax()
                loc = str(df.loc[idx, location_col]) if pd.notna(df.loc[idx, location_col]) else str(idx)
                insights.append({
                    "title": f"Highest {key} location",
                    "description": f"Highest {key} observed at {loc} with value {vals.max():.2f}.",
                    "metric": f"max_{key}_location",
                    "value": float(vals.max()),
                    "source": source,
                })

    return insights


def analyze_dataset(dataset_id: str, owner_id: str) -> dict[str, Any]:
    row, df = load_dataset(dataset_id, owner_id)
    detected = detect_semantic_columns(df)
    metrics = compute_metrics(df, detected)
    charts = generate_charts(df, detected)
    insights = generate_insights(df, detected, source=row.get("filename"))
    
    # include classified column lists
    classification = classify_columns(df)

    return {
        "dataset_id": dataset_id,
        "filename": row.get("filename"),
        "records": int(len(df)),
        "columns": [str(c) for c in df.columns],
        "detected": detected,
        "numeric_columns": classification.get("numeric", []),
        "categorical_columns": classification.get("categorical", []),
        "datetime_columns": classification.get("datetime", []),
        "identifier_columns": classification.get("identifier", []),
        "metrics": metrics,
        "charts": charts,
        "insights": insights,
    }
