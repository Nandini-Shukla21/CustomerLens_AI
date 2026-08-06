from __future__ import annotations

import hashlib
import json
import uuid
import re

from datetime import datetime, timezone
from functools import lru_cache
from pathlib import Path
from typing import Any
from io import BytesIO

import pandas as pd
from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from fastapi.responses import StreamingResponse
from loguru import logger

from app.config import settings
from app.core.security import current_user
from app.core.storage import connection, decode_json, row_dict
from app.rag.parser import DocumentParser
from app.rag.chunker import DocumentChunker
from app.services.embedding_service import EmbeddingService
from app.services.groq_service import GroqService


router = APIRouter()


# ============================================================
# RAG / EMBEDDING SERVICE
# ============================================================

@lru_cache(maxsize=1)
def document_embeddings() -> EmbeddingService:
    """
    Create one persistent Chroma/SentenceTransformer service
    per API process.
    """
    return EmbeddingService()


# ============================================================
# RAG CONTEXT BUILDER
# ============================================================

def build_rag_context(
    matches: list[dict[str, Any]],
    max_chunks: int = 3,
    max_chars_per_chunk: int = 1200,
    max_total_chars: int = 4000,
) -> str:
    """
    Build a compact RAG context.

    Important:
    - Only the best few chunks are sent to the LLM.
    - Each chunk is truncated.
    - The total context is capped.
    
    This prevents Groq from receiving large irrelevant sections
    of documents and producing unnecessarily long answers.
    """

    safe_matches = [
        document_embeddings().normalize_match(match)
        for match in (matches or [])
    ]

    context_parts: list[str] = []
    total_chars = 0

    for match in safe_matches[:max_chunks]:

        text = str(match.get("text") or "").strip()

        if not text:
            continue

        filename = (
            str(match.get("filename") or "<missing-filename>")
            .strip()
            or "<missing-filename>"
        )

        chunk_id = (
            str(match.get("chunk_id") or "<missing-chunk-id>")
            .strip()
            or "<missing-chunk-id>"
        )

        score = float(match.get("score", 0.0))

        # Keep only a reasonable amount from each retrieved chunk.
        text = text[:max_chars_per_chunk].strip()

        chunk_text = (
            f"[Source: {filename} | Chunk: {chunk_id} | "
            f"Relevance: {score:.3f}]\n{text}"
        )

        # Prevent total context from becoming too large.
        remaining = max_total_chars - total_chars

        if remaining <= 0:
            break

        chunk_text = chunk_text[:remaining]

        context_parts.append(chunk_text)
        total_chars += len(chunk_text)

    return "\n\n".join(context_parts)


# ============================================================
# DATASET HELPERS
# ============================================================

def norm(columns: list[str], names: list[str]) -> str | None:
    """
    Find a column using normalized names.
    """
    lowered = {
        str(c).lower().replace(" ", "_"): str(c)
        for c in columns
    }

    return next(
        (lowered[n] for n in names if n in lowered),
        None,
    )


def load_dataset(
    dataset_id: str,
    owner_id: str | None = None,
) -> tuple[dict[str, Any], pd.DataFrame]:

    with connection() as conn:

        query = (
            "SELECT * FROM datasets WHERE id=?"
            + (" AND owner_id=?" if owner_id else "")
        )

        params = (
            (dataset_id, owner_id)
            if owner_id
            else (dataset_id,)
        )

        row = row_dict(
            conn.execute(query, params).fetchone()
        )

    if not row:
        raise HTTPException(404, "Dataset not found")

    try:
        return row, pd.read_csv(row["path"])

    except Exception as exc:
        raise HTTPException(
            500,
            "Dataset file cannot be read",
        ) from exc


# ============================================================
# DATASET METRICS
# ============================================================

def metrics(df: pd.DataFrame) -> dict[str, Any]:

    revenue = norm(
        list(df.columns),
        ["revenue", "amount", "sales", "total_amount", "spend"],
    )

    customer = norm(
        list(df.columns),
        ["customer_id", "id", "email"],
    )

    churn = norm(
        list(df.columns),
        ["churn", "churn_score"],
    )

    risk = norm(
        list(df.columns),
        ["risk", "risk_score"],
    )

    ltv = norm(
        list(df.columns),
        ["ltv", "lifetime_value"],
    )

    return {
        "total_customers": (
            int(df[customer].nunique())
            if customer
            else int(len(df))
        ),

        "revenue": (
            float(
                pd.to_numeric(
                    df[revenue],
                    errors="coerce",
                )
                .fillna(0)
                .sum()
            )
            if revenue
            else 0
        ),

        "transactions": int(len(df)),

        "predicted_churn": (
            int(
                (
                    pd.to_numeric(
                        df[churn],
                        errors="coerce",
                    )
                    .fillna(0)
                    >= 0.5
                ).sum()
            )
            if churn
            else 0
        ),

        "high_risk_customers": (
            int(
                (
                    pd.to_numeric(
                        df[risk],
                        errors="coerce",
                    )
                    .fillna(0)
                    >= 0.6
                ).sum()
            )
            if risk
            else 0
        ),

        "average_lifetime_value": (
            float(
                pd.to_numeric(
                    df[ltv],
                    errors="coerce",
                ).mean()
            )
            if ltv
            else 0
        ),

        "average_revenue": (
            float(
                pd.to_numeric(
                    df[revenue],
                    errors="coerce",
                ).mean()
            )
            if revenue
            else 0
        ),
    }


# ============================================================
# DASHBOARD INSIGHTS
# ============================================================

def live_insights(
    frame: pd.DataFrame,
) -> list[dict[str, Any]]:

    if frame.empty:
        return []

    result = metrics(frame)

    items = [
        {
            "title": "Dataset is ready for analysis",
            "description": (
                f"{result['total_customers']:,} uploaded "
                "customer records are available."
            ),
            "priority": "info",
            "confidence": 1.0,
            "action": (
                "Open Customer 360 to explore uploaded customers."
            ),
        }
    ]

    if result["high_risk_customers"]:

        items.append(
            {
                "title": "High-risk customers detected",
                "description": (
                    f"{result['high_risk_customers']:,} records "
                    "meet the uploaded risk-score threshold."
                ),
                "priority": "high",
                "confidence": 0.9,
                "action": (
                    "Review these customers and run a prediction."
                ),
            }
        )

    if result["predicted_churn"]:

        items.append(
            {
                "title": "Churn signals detected",
                "description": (
                    f"{result['predicted_churn']:,} records "
                    "have a churn score of 0.5 or higher."
                ),
                "priority": "high",
                "confidence": 0.9,
                "action": (
                    "Prioritize retention outreach for the affected customers."
                ),
            }
        )

    if result["revenue"]:

        items.append(
            {
                "title": "Revenue available",
                "description": (
                    f"Uploaded records total "
                    f"${result['revenue']:,.2f} in revenue."
                ),
                "priority": "medium",
                "confidence": 0.95,
                "action": (
                    "Use Analytics to inspect revenue trends."
                ),
            }
        )

    return items


# ============================================================
# STRUCTURED CSV / DATASET ANSWERS
# ============================================================

def structured_answer(question: str, user_id: str) -> dict[str, Any] | None:
    """
    Answer analytical questions directly from uploaded structured datasets.

    This handles:
    - Counts
    - Distributions
    - Averages
    - Grouped averages
    - Grouped counts
    - Highest/lowest groups
    - Employee survey analysis
    - Customer dataset analysis

    Answers are calculated directly with pandas and are never invented by an LLM.
    """

    text = question.lower().strip()

    # ---------------------------------------------------------
    # Load all datasets belonging to the current user
    # ---------------------------------------------------------
    with connection() as conn:
        rows = conn.execute(
            "SELECT id, filename, path FROM datasets WHERE owner_id=?",
            (user_id,),
        ).fetchall()

    if not rows:
        return {
            "answer": "No uploaded structured dataset is available yet.",
            "sources": [],
            "confidence": 0.0,
        }

    datasets: list[tuple[str, pd.DataFrame]] = []

    for row in rows:
        try:
            frame = pd.read_csv(row["path"])
            datasets.append((row["filename"], frame))
        except Exception:
            continue

    if not datasets:
        return {
            "answer": "The uploaded datasets could not be read.",
            "sources": [],
            "confidence": 0.0,
        }

    # ---------------------------------------------------------
    # Helper functions
    # ---------------------------------------------------------

    def normalized_column_map(frame: pd.DataFrame) -> dict[str, str]:
        """
        Map normalized column names to their original column names.

        Examples:
        EmpID -> empid
        MaritalStatus -> maritalstatus
        Job_Level -> job_level
        """
        result = {}

        for column in frame.columns:
            original = str(column)
            normalized = re.sub(r"[^a-z0-9]", "", original.lower())
            result[normalized] = original

        return result

    def find_column(
        frame: pd.DataFrame,
        aliases: list[str],
    ) -> str | None:
        """
        Find a column using flexible aliases.
        """

        mapping = normalized_column_map(frame)

        for alias in aliases:
            normalized_alias = re.sub(
                r"[^a-z0-9]",
                "",
                alias.lower(),
            )

            if normalized_alias in mapping:
                return mapping[normalized_alias]

        return None

    def choose_dataset() -> tuple[str, pd.DataFrame]:
        """
        Choose the most relevant uploaded dataset for the question.

        Employee-related questions prefer employee_survey.csv.
        Customer-related questions prefer customers.csv.
        Otherwise choose the dataset whose columns best match
        words present in the question.
        """

        employee_words = {
            "employee",
            "employees",
            "department",
            "dept",
            "experience",
            "marital",
            "maritalstatus",
            "joblevel",
            "job",
            "gender",
            "workenv",
            "workload",
            "stress",
            "sleephours",
            "commute",
            "training",
            "jobsatisfaction",
            "emp",
            "full-time",
            "part-time",
            "contract",
        }

        customer_words = {
            "customer",
            "customers",
            "revenue",
            "sales",
            "segment",
            "ltv",
            "lifetime",
            "churn",
            "risk",
            "spend",
        }

        employee_score = sum(
            1 for word in employee_words if word in text
        )

        customer_score = sum(
            1 for word in customer_words if word in text
        )

        # Explicit employee question
        if employee_score > customer_score and employee_score > 0:
            for filename, frame in datasets:
                if "employee" in filename.lower():
                    return filename, frame

        # Explicit customer question
        if customer_score > employee_score and customer_score > 0:
            for filename, frame in datasets:
                if "customer" in filename.lower():
                    return filename, frame

        # Score datasets according to matching question words
        best_filename, best_frame = datasets[0]
        best_score = -1

        for filename, frame in datasets:
            columns_text = " ".join(
                re.sub(r"[^a-z0-9]", "", str(column).lower())
                for column in frame.columns
            )

            score = 0

            for word in text.split():
                clean_word = re.sub(r"[^a-z0-9]", "", word)

                if clean_word and clean_word in columns_text:
                    score += 1

            if score > best_score:
                best_score = score
                best_filename = filename
                best_frame = frame

        return best_filename, best_frame

    filename, frame = choose_dataset()

    if frame.empty:
        return {
            "answer": f"The selected dataset {filename} is empty.",
            "sources": [filename],
            "confidence": 0.0,
        }

    # ---------------------------------------------------------
    # Detect common columns
    # ---------------------------------------------------------

    customer_id = find_column(
        frame,
        [
            "customer_id",
            "customerid",
            "id",
            "empid",
            "employee_id",
            "employeeid",
        ],
    )

    name = find_column(
        frame,
        [
            "name",
            "customer_name",
            "customername",
        ],
    )

    department = find_column(
        frame,
        [
            "department",
            "dept",
        ],
    )

    experience = find_column(
        frame,
        [
            "experience",
            "years_experience",
            "yearsofexperience",
            "work_experience",
        ],
    )

    age = find_column(
        frame,
        [
            "age",
        ],
    )

    gender = find_column(
        frame,
        [
            "gender",
            "sex",
        ],
    )

    marital_status = find_column(
        frame,
        [
            "maritalstatus",
            "marital_status",
            "marital",
        ],
    )

    employee_type = find_column(
        frame,
        [
            "emptype",
            "employee_type",
            "employeetype",
            "employment_type",
        ],
    )

    job_level = find_column(
        frame,
        [
            "joblevel",
            "job_level",
            "level",
        ],
    )

    job_satisfaction = find_column(
        frame,
        [
            "jobsatisfaction",
            "job_satisfaction",
            "satisfaction",
        ],
    )

    revenue = find_column(
        frame,
        [
            "revenue",
            "amount",
            "sales",
            "total_amount",
            "spend",
        ],
    )

    churn = find_column(
        frame,
        [
            "churn",
            "churn_score",
            "churned",
        ],
    )

    risk = find_column(
        frame,
        [
            "risk",
            "risk_score",
        ],
    )

    segment = find_column(
        frame,
        [
            "segment",
            "customer_segment",
        ],
    )

    # ---------------------------------------------------------
    # Determine whether this is an analytical question
    # ---------------------------------------------------------

    analytical_words = {
        "average",
        "mean",
        "highest",
        "lowest",
        "top",
        "bottom",
        "distribution",
        "count",
        "how many",
        "compare",
        "comparison",
        "group",
        "by",
        "per",
        "trend",
        "total",
        "sum",
        "maximum",
        "minimum",
    }

    is_analytical = any(
        word in text for word in analytical_words
    )

    if not is_analytical:
        return None

    # ---------------------------------------------------------
    # 1. Total number of employees
    # ---------------------------------------------------------

    if (
        ("how many employees" in text)
        or ("number of employees" in text)
        or ("employee count" in text)
    ):

        if customer_id:
            count = frame[customer_id].nunique()

            return {
                "answer": (
                    f"There are {count:,} employees in "
                    f"{filename}."
                ),
                "sources": [filename],
                "confidence": 0.99,
            }

        return {
            "answer": (
                f"There are {len(frame):,} employee records "
                f"in {filename}."
            ),
            "sources": [filename],
            "confidence": 0.99,
        }

    # ---------------------------------------------------------
    # 2. Number of employees by department
    # ---------------------------------------------------------

    if (
        department
        and (
            "employees in each department" in text
            or "employee count by department" in text
            or "number of employees by department" in text
            or "how many employees in each department" in text
            or "employees per department" in text
        )
    ):

        counts = (
            frame[department]
            .fillna("Unknown")
            .astype(str)
            .value_counts()
        )

        parts = [
            f"{group}: {count:,}"
            for group, count in counts.items()
        ]

        return {
            "answer": (
                f"Employee count by department in {filename}: "
                + "; ".join(parts)
                + "."
            ),
            "sources": [filename],
            "confidence": 0.99,
        }

    # ---------------------------------------------------------
    # 3. Distribution of any categorical column
    # ---------------------------------------------------------

    categorical_targets = []

    if "marital" in text or "marital status" in text:
        if marital_status:
            categorical_targets.append(
                ("MaritalStatus", marital_status)
            )

    if "employee type" in text or "employment type" in text:
        if employee_type:
            categorical_targets.append(
                ("EmpType", employee_type)
            )

    if "gender" in text:
        if gender:
            categorical_targets.append(
                ("Gender", gender)
            )

    if "job level" in text:
        if job_level:
            categorical_targets.append(
                ("JobLevel", job_level)
            )

    if "department" in text and "distribution" in text:
        if department:
            categorical_targets.append(
                ("Department", department)
            )

    if categorical_targets and (
        "distribution" in text
        or "breakdown" in text
    ):

        display_name, column = categorical_targets[0]

        counts = (
            frame[column]
            .fillna("Unknown")
            .astype(str)
            .value_counts()
        )

        total = len(frame)

        parts = [
            f"{value}: {count:,} "
            f"({count / total:.1%})"
            for value, count in counts.items()
        ]

        return {
            "answer": (
                f"Distribution of {display_name} in "
                f"{filename}: "
                + "; ".join(parts)
                + "."
            ),
            "sources": [filename],
            "confidence": 0.99,
        }

    # ---------------------------------------------------------
    # 4. Average experience by department
    # ---------------------------------------------------------

    if (
        experience
        and department
        and "experience" in text
        and "department" in text
        and (
            "average" in text
            or "mean" in text
            or "compare" in text
        )
    ):

        temp = frame.copy()

        temp[experience] = pd.to_numeric(
            temp[experience],
            errors="coerce",
        )

        grouped = (
            temp.dropna(subset=[experience])
            .groupby(department)[experience]
            .mean()
            .sort_values(ascending=False)
        )

        if grouped.empty:
            return {
                "answer": (
                    f"No valid experience values were found "
                    f"in {filename}."
                ),
                "sources": [filename],
                "confidence": 0.0,
            }

        parts = [
            f"{group}: {value:.2f} years"
            for group, value in grouped.items()
        ]

        highest_department = grouped.index[0]
        highest_value = grouped.iloc[0]

        return {
            "answer": (
                f"Average experience by department in "
                f"{filename}: "
                + "; ".join(parts)
                + f". The department with the highest "
                f"average experience is {highest_department} "
                f"with {highest_value:.2f} years."
            ),
            "sources": [filename],
            "confidence": 0.99,
        }

    # ---------------------------------------------------------
    # 5. Highest / lowest average experience
    # ---------------------------------------------------------

    if (
        experience
        and department
        and "experience" in text
        and "department" in text
        and (
            "highest" in text
            or "lowest" in text
        )
    ):

        temp = frame.copy()

        temp[experience] = pd.to_numeric(
            temp[experience],
            errors="coerce",
        )

        grouped = (
            temp.dropna(subset=[experience])
            .groupby(department)[experience]
            .mean()
        )

        if grouped.empty:
            return {
                "answer": "No valid experience data was found.",
                "sources": [filename],
                "confidence": 0.0,
            }

        if "lowest" in text:
            group = grouped.idxmin()
            value = grouped.min()
            label = "lowest"
        else:
            group = grouped.idxmax()
            value = grouped.max()
            label = "highest"

        return {
            "answer": (
                f"The department with the {label} average "
                f"experience is {group}, with "
                f"{value:.2f} years."
            ),
            "sources": [filename],
            "confidence": 0.99,
        }

    # ---------------------------------------------------------
    # 6. Average of a numeric column
    # ---------------------------------------------------------

    numeric_targets = []

    if "age" in text and age:
        numeric_targets.append(("Age", age))

    if "experience" in text and experience:
        numeric_targets.append(("Experience", experience))

    if "job satisfaction" in text and job_satisfaction:
        numeric_targets.append(
            ("Job Satisfaction", job_satisfaction)
        )

    if "revenue" in text and revenue:
        numeric_targets.append(("Revenue", revenue))

    if "risk" in text and risk:
        numeric_targets.append(("Risk", risk))

    if "churn" in text and churn:
        numeric_targets.append(("Churn", churn))

    if numeric_targets and (
        "average" in text
        or "mean" in text
    ):

        display_name, column = numeric_targets[0]

        values = pd.to_numeric(
            frame[column],
            errors="coerce",
        ).dropna()

        if values.empty:
            return {
                "answer": (
                    f"No valid {display_name} values were found "
                    f"in {filename}."
                ),
                "sources": [filename],
                "confidence": 0.0,
            }

        average = values.mean()

        if display_name in {"Age", "Experience"}:
            answer = (
                f"The average {display_name.lower()} is "
                f"{average:.2f} years in {filename}."
            )
        else:
            answer = (
                f"The average {display_name.lower()} is "
                f"{average:.2f} in {filename}."
            )

        return {
            "answer": answer,
            "sources": [filename],
            "confidence": 0.99,
        }

    # ---------------------------------------------------------
    # 7. Average numeric metric by department
    # ---------------------------------------------------------

    if department and (
        "average" in text
        or "mean" in text
        or "compare" in text
    ):

        metric_column = None
        metric_name = None

        if "age" in text and age:
            metric_column = age
            metric_name = "age"

        elif "experience" in text and experience:
            metric_column = experience
            metric_name = "experience"

        elif "job satisfaction" in text and job_satisfaction:
            metric_column = job_satisfaction
            metric_name = "job satisfaction"

        elif "revenue" in text and revenue:
            metric_column = revenue
            metric_name = "revenue"

        if metric_column:
            temp = frame.copy()

            temp[metric_column] = pd.to_numeric(
                temp[metric_column],
                errors="coerce",
            )

            grouped = (
                temp.dropna(subset=[metric_column])
                .groupby(department)[metric_column]
                .mean()
                .sort_values(ascending=False)
            )

            if not grouped.empty:
                parts = [
                    f"{group}: {value:.2f}"
                    for group, value in grouped.items()
                ]

                return {
                    "answer": (
                        f"Average {metric_name} by department "
                        f"in {filename}: "
                        + "; ".join(parts)
                        + "."
                    ),
                    "sources": [filename],
                    "confidence": 0.99,
                }

    # ---------------------------------------------------------
    # 8. Average numeric metric by job level
    # ---------------------------------------------------------

    if job_level and (
        "job level" in text
        or "joblevel" in text
    ) and (
        "average" in text
        or "mean" in text
        or "compare" in text
    ):

        metric_column = None
        metric_name = None

        if "experience" in text and experience:
            metric_column = experience
            metric_name = "experience"

        elif "age" in text and age:
            metric_column = age
            metric_name = "age"

        elif "job satisfaction" in text and job_satisfaction:
            metric_column = job_satisfaction
            metric_name = "job satisfaction"

        if metric_column:
            temp = frame.copy()

            temp[metric_column] = pd.to_numeric(
                temp[metric_column],
                errors="coerce",
            )

            grouped = (
                temp.dropna(subset=[metric_column])
                .groupby(job_level)[metric_column]
                .mean()
                .sort_values(ascending=False)
            )

            parts = [
                f"{group}: {value:.2f}"
                for group, value in grouped.items()
            ]

            return {
                "answer": (
                    f"Average {metric_name} by job level "
                    f"in {filename}: "
                    + "; ".join(parts)
                    + "."
                ),
                "sources": [filename],
                "confidence": 0.99,
            }

    # ---------------------------------------------------------
    # 9. Revenue / sales analysis
    # ---------------------------------------------------------

    if revenue:

        numeric_revenue = pd.to_numeric(
            frame[revenue],
            errors="coerce",
        ).fillna(0)

        if "total" in text or "sum" in text:
            return {
                "answer": (
                    f"Total {revenue} in {filename} is "
                    f"${numeric_revenue.sum():,.2f}."
                ),
                "sources": [filename],
                "confidence": 0.99,
            }

        if "highest" in text or "maximum" in text:
            index = numeric_revenue.idxmax()
            value = numeric_revenue.loc[index]

            identifier = (
                str(frame.loc[index, name])
                if name
                else str(frame.loc[index, customer_id])
                if customer_id
                else str(index)
            )

            return {
                "answer": (
                    f"The highest {revenue} is "
                    f"${value:,.2f}, belonging to "
                    f"{identifier}."
                ),
                "sources": [filename],
                "confidence": 0.99,
            }

    # ---------------------------------------------------------
    # 10. Churn analysis
    # ---------------------------------------------------------

    if churn and "churn" in text:

        values = pd.to_numeric(
            frame[churn],
            errors="coerce",
        ).fillna(0)

        high_churn = int((values >= 0.5).sum())

        return {
            "answer": (
                f"{high_churn:,} records in {filename} "
                f"have a churn score of 0.50 or higher."
            ),
            "sources": [filename],
            "confidence": 0.99,
        }

    # ---------------------------------------------------------
    # 11. Risk analysis
    # ---------------------------------------------------------

    if risk and "risk" in text:

        values = pd.to_numeric(
            frame[risk],
            errors="coerce",
        ).fillna(0)

        high_risk = int((values >= 0.6).sum())

        return {
            "answer": (
                f"{high_risk:,} records in {filename} "
                f"have a high risk score of 0.60 or higher."
            ),
            "sources": [filename],
            "confidence": 0.99,
        }

    # ---------------------------------------------------------
    # 12. Segment distribution
    # ---------------------------------------------------------

    if segment and (
        "segment" in text
        and (
            "distribution" in text
            or "breakdown" in text
        )
    ):

        counts = (
            frame[segment]
            .fillna("Unknown")
            .astype(str)
            .value_counts()
        )

        parts = [
            f"{group}: {count:,}"
            for group, count in counts.items()
        ]

        return {
            "answer": (
                f"Segment distribution in {filename}: "
                + "; ".join(parts)
                + "."
            ),
            "sources": [filename],
            "confidence": 0.99,
        }

    # ---------------------------------------------------------
    # 13. Generic dataset information
    # ---------------------------------------------------------

    return {
        "answer": (
            f"{filename} contains {len(frame):,} records "
            f"and {len(frame.columns):,} columns: "
            + ", ".join(map(str, frame.columns))
            + "."
        ),
        "sources": [filename],
        "confidence": 0.95,
    }


# ============================================================
# DATASET UPLOAD
# ============================================================

@router.post("/datasets", status_code=201)
async def upload_dataset(
    file: UploadFile = File(...),
    user: dict = Depends(current_user),
):

    if (
        not file.filename
        or Path(file.filename).suffix.lower()
        not in {".csv", ".json", ".xlsx", ".xls"}
    ):
        raise HTTPException(
            422,
            "Supported dataset files: CSV, JSON, XLSX, XLS",
        )

    data = await file.read()

    if not data:
        raise HTTPException(
            422,
            "Uploaded file is empty",
        )

    dataset_id = str(uuid.uuid4())

    directory = (
        Path(settings.upload_dir) / "datasets"
    )

    directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    path = directory / f"{dataset_id}.csv"

    source = Path(
        file.filename
    ).suffix.lower()

    try:

        if source == ".csv":

            frame = pd.read_csv(
                BytesIO(data)
            )

        elif source == ".json":

            frame = pd.read_json(
                BytesIO(data)
            )

        else:

            frame = pd.read_excel(
                BytesIO(data)
            )

    except Exception as exc:

        raise HTTPException(
            422,
            f"Unable to parse dataset: {exc}",
        ) from exc

    frame.to_csv(
        path,
        index=False,
    )

    summary = {
        "missing_values": {
            str(k): int(v)
            for k, v in frame.isna().sum().items()
        },

        "data_types": {
            str(k): str(v)
            for k, v in frame.dtypes.items()
        },

        "quality_score": round(
            100
            * (
                1
                - frame.isna().sum().sum()
                / max(1, frame.size)
            ),
            2,
        ),
    }

    with connection() as conn:

        conn.execute(
            """
            INSERT INTO datasets(
                id,
                filename,
                path,
                rows,
                columns,
                schema_json,
                summary_json,
                owner_id
            )
            VALUES(?,?,?,?,?,?,?,?)
            """,
            (
                dataset_id,
                file.filename,
                str(path),
                len(frame),
                len(frame.columns),
                json.dumps(
                    list(map(str, frame.columns))
                ),
                json.dumps(summary),
                user["sub"],
            ),
        )

        customer_id = norm(
            list(frame.columns),
            ["customer_id", "id", "email"],
        )

        name = norm(
            list(frame.columns),
            ["name", "customer_name"],
        )

        email = norm(
            list(frame.columns),
            ["email"],
        )

        phone = norm(
            list(frame.columns),
            ["phone", "phone_number"],
        )

        rev = norm(
            list(frame.columns),
            ["revenue", "amount", "sales"],
        )

        tx = norm(
            list(frame.columns),
            ["transactions", "transaction_count"],
        )

        ltv = norm(
            list(frame.columns),
            ["ltv", "lifetime_value"],
        )

        risk = norm(
            list(frame.columns),
            ["risk", "risk_score"],
        )

        churn = norm(
            list(frame.columns),
            ["churn", "churn_score"],
        )

        for i, row in frame.iterrows():

            cid = (
                str(row[customer_id])
                if customer_id
                and pd.notna(row[customer_id])
                else f"{dataset_id}:{i}"
            )

            def value(col):
                if not col:
                    return 0

                return float(
                    pd.to_numeric(
                        pd.Series([row[col]]),
                        errors="coerce",
                    )
                    .fillna(0)
                    .iloc[0]
                )

            conn.execute(
                """
                INSERT OR REPLACE INTO customers
                VALUES(?,?,?,?,?,?,?,?,?,?,?)
                """,
                (
                    cid,
                    dataset_id,
                    json.dumps(
                        {
                            str(k): (
                                None
                                if pd.isna(v)
                                else str(v)
                            )
                            for k, v in row.items()
                        }
                    ),
                    (
                        str(row[name])
                        if name
                        and pd.notna(row[name])
                        else cid
                    ),
                    (
                        str(row[email])
                        if email
                        and pd.notna(row[email])
                        else None
                    ),
                    (
                        str(row[phone])
                        if phone
                        and pd.notna(row[phone])
                        else None
                    ),
                    value(rev),
                    value(tx),
                    value(ltv),
                    value(risk),
                    value(churn),
                ),
            )

        conn.execute(
            """
            INSERT INTO uploads(
                id,
                dataset_id,
                owner_id,
                filename,
                file_type,
                size_bytes,
                status
            )
            VALUES(?,?,?,?,?,?,?)
            """,
            (
                str(uuid.uuid4()),
                dataset_id,
                user["sub"],
                file.filename,
                source,
                len(data),
                "ready",
            ),
        )

    return {
        "dataset_id": dataset_id,
        "filename": file.filename,
        "row_count": len(frame),
        "column_count": len(frame.columns),
        "columns": list(map(str, frame.columns)),
        **summary,
    }


# ============================================================
# DATASET ENDPOINTS
# ============================================================

@router.get("/datasets")
def datasets(
    user: dict = Depends(current_user),
):

    with connection() as conn:

        return [
            dict(r)
            for r in conn.execute(
                """
                SELECT id,filename,rows,columns,created_at
                FROM datasets
                WHERE owner_id=?
                ORDER BY created_at DESC
                """,
                (user["sub"],),
            ).fetchall()
        ]


@router.get("/uploads")
def upload_history(
    user: dict = Depends(current_user),
):

    with connection() as conn:

        return [
            dict(row)
            for row in conn.execute(
                """
                SELECT
                    id,
                    dataset_id,
                    document_id,
                    filename,
                    file_type,
                    size_bytes,
                    status,
                    created_at
                FROM uploads
                WHERE owner_id=?
                ORDER BY created_at DESC
                """,
                (user["sub"],),
            ).fetchall()
        ]


@router.get("/datasets/{dataset_id}/summary")
def dataset_summary(
    dataset_id: str,
    user: dict = Depends(current_user),
):

    row, frame = load_dataset(
        dataset_id,
        user["sub"],
    )

    return {
        "dataset_id": dataset_id,
        "filename": row["filename"],
        "rows": row["rows"],
        "columns": row["columns"],
        **decode_json(
            row["summary_json"],
            {},
        ),
    }


@router.get("/datasets/{dataset_id}/columns")
def dataset_columns(
    dataset_id: str,
    user: dict = Depends(current_user),
):

    _, frame = load_dataset(
        dataset_id,
        user["sub"],
    )

    return [
        {
            "name": str(c),
            "type": str(frame[c].dtype),
            "missing": int(
                frame[c].isna().sum()
            ),
            "unique": int(
                frame[c].nunique()
            ),
        }
        for c in frame.columns
    ]


@router.get("/datasets/{dataset_id}/preview")
def dataset_preview(
    dataset_id: str,
    offset: int = 0,
    limit: int = Query(25, le=200),
    q: str = "",
    user: dict = Depends(current_user),
):

    _, frame = load_dataset(
        dataset_id,
        user["sub"],
    )

    if q:

        filtered = frame[
            frame.astype(str)
            .apply(
                lambda c: c.str.contains(
                    q,
                    case=False,
                    na=False,
                )
            )
            .any(axis=1)
        ]

    else:

        filtered = frame

    return {
        "total": len(filtered),
        "rows": (
            filtered.iloc[
                offset:offset + limit
            ]
            .where(
                filtered.notna(),
                None,
            )
            .to_dict(
                orient="records"
            )
        ),
    }


@router.get("/datasets/{dataset_id}")
def dataset(
    dataset_id: str,
    user: dict = Depends(current_user),
):

    return dataset_summary(
        dataset_id,
        user,
    )


@router.delete(
    "/datasets/{dataset_id}",
    status_code=204,
)
def delete_dataset(
    dataset_id: str,
    user: dict = Depends(current_user),
):

    row, _ = load_dataset(
        dataset_id,
        user["sub"],
    )

    with connection() as conn:

        conn.execute(
            "DELETE FROM datasets WHERE id=?",
            (dataset_id,),
        )

    Path(
        row["path"]
    ).unlink(
        missing_ok=True
    )


# ============================================================
# DASHBOARD
# ============================================================

@router.get("/dashboard")
def dashboard(
    user: dict = Depends(current_user),
):

    with connection() as conn:

        rows = conn.execute(
            """
            SELECT *
            FROM datasets
            WHERE owner_id=?
            ORDER BY created_at DESC
            """,
            (user["sub"],),
        ).fetchall()

        uploads = [
            dict(r)
            for r in conn.execute(
                """
                SELECT filename,status,created_at
                FROM uploads
                ORDER BY created_at DESC
                LIMIT 5
                """
            ).fetchall()
        ]

    frames = []

    for row in rows:

        try:
            frames.append(
                pd.read_csv(row["path"])
            )

        except Exception:
            continue

    frame = (
        pd.concat(
            frames,
            ignore_index=True,
        )
        if frames
        else pd.DataFrame()
    )

    result = (
        metrics(frame)
        if not frame.empty
        else metrics(pd.DataFrame())
    )

    segment = norm(
        list(frame.columns),
        ["segment", "customer_segment"],
    )

    risk = norm(
        list(frame.columns),
        ["risk", "risk_score"],
    )

    date = norm(
        list(frame.columns),
        [
            "date",
            "transaction_date",
            "created_at",
        ],
    )

    revenue = norm(
        list(frame.columns),
        ["revenue", "amount", "sales"],
    )

    result.update(
        {
            "datasets": len(rows),
            "documents": 0,
            "recent_uploads": uploads,

            "segment_distribution": (
                [
                    {
                        "name": str(k),
                        "value": int(v),
                    }
                    for k, v in
                    frame[segment]
                    .fillna("Unknown")
                    .value_counts()
                    .items()
                ]
                if segment
                else []
            ),

            "risk_distribution": (
                [
                    {
                        "name": str(k),
                        "value": int(v),
                    }
                    for k, v in
                    pd.cut(
                        pd.to_numeric(
                            frame[risk],
                            errors="coerce",
                        ).fillna(0),
                        [-1, 0.3, 0.6, 1],
                        labels=[
                            "Low",
                            "Medium",
                            "High",
                        ],
                    )
                    .value_counts()
                    .items()
                ]
                if risk
                else []
            ),

            "revenue_trend": [],

            "ai_insights": live_insights(
                frame
            ),
        }
    )

    if date and revenue:

        tmp = pd.DataFrame(
            {
                "date": pd.to_datetime(
                    frame[date],
                    errors="coerce",
                ),

                "revenue": pd.to_numeric(
                    frame[revenue],
                    errors="coerce",
                ).fillna(0),
            }
        ).dropna()

        result["revenue_trend"] = [
            {
                "period": str(k),
                "revenue": float(v),
            }
            for k, v in
            tmp.groupby(
                tmp.date.dt.to_period("M")
            )["revenue"]
            .sum()
            .items()
        ]

    return result


# ============================================================
# CUSTOMERS
# ============================================================

@router.get("/customers")
def customers(
    q: str = "",
    limit: int = Query(50, le=200),
    user: dict = Depends(current_user),
):

    with connection() as conn:

        sql = """
            SELECT c.*
            FROM customers c
            JOIN datasets d
                ON c.dataset_id=d.id
            WHERE d.owner_id=?
        """

        args = [user["sub"]]

        if q:

            sql += """
                AND (
                    c.id LIKE ?
                    OR c.name LIKE ?
                    OR c.email LIKE ?
                    OR c.phone LIKE ?
                )
            """

            args += [f"%{q}%"] * 4

        rows = conn.execute(
            sql + " LIMIT ?",
            (*args, limit),
        ).fetchall()

    return [
        {
            **dict(r),
            "payload": decode_json(
                r["payload_json"],
                {},
            ),
        }
        for r in rows
    ]


@router.get("/customers/search")
def customer_search(
    q: str,
    user: dict = Depends(current_user),
):

    return customers(
        q,
        50,
        user,
    )


@router.get("/customers/{customer_id}")
def customer(
    customer_id: str,
    user: dict = Depends(current_user),
):

    records = customers(
        customer_id,
        200,
        user,
    )

    item = next(
        (
            r
            for r in records
            if r["id"] == customer_id
        ),
        None,
    )

    if not item:
        raise HTTPException(
            404,
            "Customer not found",
        )

    return {
        "profile": item,
        "revenue": item["revenue"],
        "transactions": item["transactions"],
        "lifetime_value": item["ltv"],
        "risk_score": item["risk"],
        "churn_score": item["churn"],
        "complaint_history": [],
        "purchase_timeline": [],
        "ai_summary": (
            "Customer risk is "
            f"{'high' if item['risk'] >= 0.6 else 'low'} "
            "based on values present in the uploaded dataset."
        ),
    }


# ============================================================
# ANALYTICS
# ============================================================

@router.get("/analytics")
def analytics(
    dataset_id: str | None = None,
    user: dict = Depends(current_user),
):

    if dataset_id:

        _, frame = load_dataset(
            dataset_id,
            user["sub"],
        )

    else:

        with connection() as conn:

            row = conn.execute(
                """
                SELECT id
                FROM datasets
                WHERE owner_id=?
                ORDER BY created_at DESC
                LIMIT 1
                """,
                (user["sub"],),
            ).fetchone()

        frame = (
            load_dataset(
                row["id"],
                user["sub"],
            )[1]
            if row
            else pd.DataFrame()
        )

    segment = norm(
        list(frame.columns),
        ["segment", "customer_segment"],
    )

    revenue = norm(
        list(frame.columns),
        [
            "revenue",
            "amount",
            "sales",
            "total_amount",
            "spend",
        ],
    )

    date = norm(
        list(frame.columns),
        [
            "date",
            "transaction_date",
            "created_at",
        ],
    )

    trends = []

    if date and revenue:

        tmp = pd.DataFrame(
            {
                "date": pd.to_datetime(
                    frame[date],
                    errors="coerce",
                ),

                "revenue": pd.to_numeric(
                    frame[revenue],
                    errors="coerce",
                ).fillna(0),
            }
        ).dropna()

        trends = [
            {
                "period": str(k),
                "revenue": float(v),
            }
            for k, v in
            tmp.groupby(
                tmp.date.dt.to_period("M")
            )["revenue"]
            .sum()
            .items()
        ]

    return {
        "kpis": metrics(frame),
        "columns": list(
            map(str, frame.columns)
        ),
        "records": len(frame),
        "revenue_trend": trends,
        "segments": (
            [
                {
                    "name": str(k),
                    "value": int(v),
                }
                for k, v in
                frame[segment]
                .fillna("Unknown")
                .value_counts()
                .items()
            ]
            if segment
            else []
        ),
    }


# ============================================================
# INSIGHTS
# ============================================================

@router.get("/insights")
def insights(
    user: dict = Depends(current_user),
):

    data = dashboard(user)

    return data["ai_insights"]


# ============================================================
# ACTIVITY
# ============================================================

@router.get("/activity")
def activity(
    user: dict = Depends(current_user),
):

    with connection() as conn:

        uploads = conn.execute(
            """
            SELECT filename,status,created_at
            FROM uploads
            WHERE owner_id=?
            ORDER BY created_at DESC
            LIMIT 20
            """,
            (user["sub"],),
        ).fetchall()

        predictions = conn.execute(
            """
            SELECT
                p.customer_id,
                p.prediction,
                p.created_at
            FROM predictions p
            JOIN datasets d
                ON p.dataset_id=d.id
            WHERE d.owner_id=?
            ORDER BY p.created_at DESC
            LIMIT 20
            """,
            (user["sub"],),
        ).fetchall()

    events = (
        [
            {
                "who": "You",
                "what": (
                    f"uploaded {row['filename']} "
                    f"({row['status']})"
                ),
                "when": row["created_at"],
                "type": "upload",
            }
            for row in uploads
        ]
        +
        [
            {
                "who": "You",
                "what": (
                    f"ran {row['prediction']} "
                    f"for customer {row['customer_id']}"
                ),
                "when": row["created_at"],
                "type": "prediction",
            }
            for row in predictions
        ]
    )

    return sorted(
        events,
        key=lambda item: item["when"],
        reverse=True,
    )[:20]


# ============================================================
# NOTIFICATIONS
# ============================================================

@router.get("/notifications")
def notifications(
    user: dict = Depends(current_user),
):

    data = dashboard(user)

    return [
        {
            "title": item["title"],
            "description": item["description"],
            "priority": item["priority"],
            "created_at": datetime.now(
                timezone.utc
            ).isoformat(),
            "read": False,
        }
        for item in data["ai_insights"]
    ]


# ============================================================
# PREDICTION
# ============================================================

@router.post("/predict")
def predict(
    body: dict[str, Any],
    user: dict = Depends(current_user),
):

    customer_id = str(
        body.get("customer_id", "")
    )

    features = body.get(
        "features",
        {},
    )

    records = customers(
        customer_id,
        200,
        user,
    )

    customer = next(
        (
            x
            for x in records
            if x["id"] == customer_id
        ),
        None,
    )

    if not customer:

        raise HTTPException(
            404,
            "Customer not found in your uploaded data",
        )

    dataset, frame = load_dataset(
        customer["dataset_id"],
        user["sub"],
    )

    target = norm(
        list(frame.columns),
        [
            "churn",
            "churn_score",
            "churned",
            "target",
        ],
    )

    if not target:

        raise HTTPException(
            422,
            "A churn/target column is required "
            "to train predictions from this dataset",
        )

    numeric = [
        str(c)
        for c in frame.select_dtypes(
            include="number"
        ).columns
        if str(c) != target
    ]

    if not numeric:

        raise HTTPException(
            422,
            "The dataset needs numeric feature "
            "columns to train predictions",
        )

    import joblib

    model_dir = (
        Path(settings.upload_dir)
        / "models"
    )

    model_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    model_path = (
        model_dir
        / f"{dataset['id']}.joblib"
    )

    if model_path.exists():

        artifact = joblib.load(
            model_path
        )

        model = artifact["model"]
        numeric = artifact["features"]

    else:

        from sklearn.impute import SimpleImputer
        from sklearn.linear_model import LogisticRegression
        from sklearn.pipeline import make_pipeline

        y = (
            pd.to_numeric(
                frame[target],
                errors="coerce",
            )
            .fillna(0)
            >= 0.5
        ).astype(int)

        if y.nunique() < 2:

            raise HTTPException(
                422,
                "The uploaded target column "
                "needs both churn outcomes "
                "to train the model",
            )

        model = make_pipeline(
            SimpleImputer(
                strategy="median"
            ),
            LogisticRegression(
                max_iter=1000,
                class_weight="balanced",
            ),
        )

        X = frame[numeric].apply(
            pd.to_numeric,
            errors="coerce",
        )

        model.fit(X, y)

        joblib.dump(
            {
                "model": model,
                "features": numeric,
            },
            model_path,
        )

    values = (
        features
        or customer["payload"]
    )

    sample = pd.DataFrame(
        [
            {
                c: values.get(c)
                for c in numeric
            }
        ]
    )

    probability = float(
        model.predict_proba(
            sample[numeric].apply(
                pd.to_numeric,
                errors="coerce",
            )
        )[0][1]
    )

    confidence = round(
        max(
            probability,
            1 - probability,
        ),
        3,
    )

    prediction = (
        "high_churn_risk"
        if probability >= 0.5
        else "low_churn_risk"
    )

    pid = str(uuid.uuid4())

    coefficients = (
        model.named_steps[
            "logisticregression"
        ].coef_[0]
    )

    explanation = sorted(
        [
            {
                "feature": name,
                "contribution": round(
                    float(coef),
                    4,
                ),
            }
            for name, coef in zip(
                numeric,
                coefficients,
            )
        ],
        key=lambda item: abs(
            item["contribution"]
        ),
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
            )
            VALUES(?,?,?,?,?,?,?)
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
        "id": pid,
        "prediction": prediction,
        "probability": probability,
        "confidence": confidence,
        "explanation": explanation,
    }


@router.post("/predict/batch")
def predict_batch(
    body: dict[str, Any],
    user: dict = Depends(current_user),
):

    return [
        predict(
            {
                "customer_id": str(
                    item.get(
                        "customer_id",
                        "",
                    )
                ),
                "features": item.get(
                    "features",
                    {},
                ),
            },
            user,
        )
        for item in body.get(
            "items",
            [],
        )
    ]


@router.get("/predictions/history")
def prediction_history(
    user: dict = Depends(current_user),
):

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
            "explanation": decode_json(
                r["explanation_json"],
                [],
            ),
        }
        for r in rows
    ]


# ============================================================
# DOCUMENT UPLOAD / RAG INDEXING
# ============================================================

@router.post(
    "/documents",
    status_code=201,
)
async def upload_document(
    file: UploadFile = File(...),
    user: dict = Depends(current_user),
):

    if (
        not file.filename
        or Path(file.filename).suffix.lower()
        not in {
            ".pdf",
            ".docx",
            ".txt",
            ".md",
            ".markdown",
            ".json",
        }
    ):

        raise HTTPException(
            422,
            "Supported document files: "
            "PDF, DOCX, TXT, Markdown, JSON",
        )

    raw = await file.read()

    if not raw:

        raise HTTPException(
            422,
            "Uploaded file is empty",
        )

    checksum = hashlib.sha256(
        raw
    ).hexdigest()

    with connection() as conn:

        existing = conn.execute(
            """
            SELECT id,filename,chunks_json
            FROM documents
            WHERE owner_id=? AND checksum=?
            """,
            (
                user["sub"],
                checksum,
            ),
        ).fetchone()

    if existing:

        return {
            "document_id": existing["id"],
            "filename": existing["filename"],
            "chunks": len(
                decode_json(
                    existing["chunks_json"],
                    [],
                )
            ),
            "status": "indexed",
        }

    did = str(uuid.uuid4())

    base_dir = (
        Path(settings.upload_dir)
        / "documents"
    )

    base_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    path = (
        base_dir
        / f"{did}{Path(file.filename).suffix.lower()}"
    )

    path.write_bytes(raw)

    try:

        content = DocumentParser.extract_text(
            path
        )

    except Exception as exc:

        path.unlink(
            missing_ok=True
        )

        raise HTTPException(
            422,
            f"Unable to parse document: {exc}",
        ) from exc

    if not content.strip():

        path.unlink(
            missing_ok=True
        )

        raise HTTPException(
            422,
            "No readable text was found in this document",
        )

    chunks = DocumentChunker(
        chunk_size=900,
        overlap=150,
    ).chunk_text(content)

    upload_time = datetime.now(
        timezone.utc
    ).isoformat()

    logger.info(
        "Document upload started "
        "filename={} size_bytes={} collection={}",
        file.filename,
        len(raw),
        document_embeddings().collection_name,
    )

    try:

        document_embeddings().embed_chunks(
            [
                {
                    "text": chunk,
                    "document_id": did,
                    "owner_id": str(
                        user["sub"]
                    ),
                    "filename": file.filename,
                    "chunk_id": (
                        f"{did}:{index}"
                    ),
                    "upload_time": upload_time,
                    "checksum": checksum,
                }
                for index, chunk in enumerate(
                    chunks
                )
            ]
        )

    except Exception as exc:

        path.unlink(
            missing_ok=True
        )

        raise HTTPException(
            503,
            f"Document indexing is unavailable: {exc}",
        ) from exc

    with connection() as conn:

        conn.execute(
            """
            INSERT INTO documents(
                id,
                filename,
                path,
                content,
                chunks_json,
                checksum,
                indexed_at,
                owner_id,
                file_type,
                size_bytes
            )
            VALUES(?,?,?,?,?,?,?,?,?,?)
            """,
            (
                did,
                file.filename,
                str(path),
                content,
                json.dumps(chunks),
                checksum,
                datetime.now(
                    timezone.utc
                ).isoformat(),
                user["sub"],
                Path(
                    file.filename
                ).suffix.lower(),
                len(raw),
            ),
        )

        conn.execute(
            """
            INSERT INTO uploads(
                id,
                document_id,
                owner_id,
                filename,
                file_type,
                size_bytes,
                status
            )
            VALUES(?,?,?,?,?,?,?)
            """,
            (
                str(uuid.uuid4()),
                did,
                user["sub"],
                file.filename,
                Path(
                    file.filename
                ).suffix.lower(),
                len(raw),
                "indexed",
            ),
        )

    logger.info(
        "Document upload completed "
        "filename={} chunks_created={} "
        "collection={} document_id={}",
        file.filename,
        len(chunks),
        document_embeddings().collection_name,
        did,
    )

    return {
        "document_id": did,
        "filename": file.filename,
        "chunks": len(chunks),
        "status": "indexed",
    }


@router.get("/documents")
def list_documents(
    user: dict = Depends(current_user),
):

    with connection() as conn:

        rows = conn.execute(
            """
            SELECT
                id,
                filename,
                path,
                file_type,
                size_bytes,
                checksum,
                indexed_at,
                created_at
            FROM documents
            WHERE owner_id=?
            ORDER BY created_at DESC
            """,
            (user["sub"],),
        ).fetchall()

    return [
        {
            "id": row["id"],
            "filename": row["filename"],
            "path": row["path"],
            "file_type": row["file_type"],
            "size_bytes": row["size_bytes"],
            "checksum": row["checksum"],
            "indexed_at": row["indexed_at"],
            "created_at": row["created_at"],
        }
        for row in rows
    ]


@router.get("/documents/{document_id}")
def get_document(
    document_id: str,
    user: dict = Depends(current_user),
):

    with connection() as conn:

        row = conn.execute(
            """
            SELECT
                id,
                filename,
                path,
                file_type,
                size_bytes,
                checksum,
                indexed_at,
                content,
                created_at
            FROM documents
            WHERE id=? AND owner_id=?
            """,
            (
                document_id,
                user["sub"],
            ),
        ).fetchone()

    if not row:

        raise HTTPException(
            404,
            "Document not found",
        )

    return {
        "id": row["id"],
        "filename": row["filename"],
        "path": row["path"],
        "file_type": row["file_type"],
        "size_bytes": row["size_bytes"],
        "checksum": row["checksum"],
        "indexed_at": row["indexed_at"],
        "content": row["content"],
        "created_at": row["created_at"],
    }


@router.delete(
    "/documents/{document_id}",
    status_code=204,
)
def delete_document(
    document_id: str,
    user: dict = Depends(current_user),
):

    with connection() as conn:

        row = conn.execute(
            """
            SELECT path
            FROM documents
            WHERE id=? AND owner_id=?
            """,
            (
                document_id,
                user["sub"],
            ),
        ).fetchone()

        if not row:

            raise HTTPException(
                404,
                "Document not found",
            )

        conn.execute(
            """
            DELETE FROM documents
            WHERE id=? AND owner_id=?
            """,
            (
                document_id,
                user["sub"],
            ),
        )

    if row["path"]:

        Path(
            row["path"]
        ).unlink(
            missing_ok=True
        )

    document_embeddings().delete_document(
        document_id
    )


# ============================================================
# GROQ ANSWER GENERATION
# ============================================================

def generate_rag_answer(
    question: str,
    context: str,
) -> str:
    """
    Generate a concise answer using the user's Groq API.

    The important part is that we explicitly instruct Groq
    not to dump the retrieved context.
    """

    if not context.strip():

        return (
            "I couldn't find enough relevant information "
            "in the uploaded documents."
        )

    if not settings.groq_api_key:

        # Fallback when Groq is not configured.
        return context[:1200]

    # Strong answer-format instructions.
    # These are included in the question sent to Groq.
    constrained_question = f"""
Answer the user's question using ONLY the relevant information
from the provided document context.

USER QUESTION:
{question}

RULES:
- Answer the question directly.
- Be concise and specific.
- Do NOT repeat the document context.
- Do NOT summarize unrelated parts of the documents.
- Do NOT mention chunks, embeddings, retrieval, or similarity scores.
- Do NOT invent information that is not supported by the context.
- If the context does not contain enough information, say:
  "The uploaded documents do not contain enough information to answer this."
- Prefer 2-5 sentences.
- Use bullet points only when they make the answer clearer.
- Start immediately with the answer.

DOCUMENT CONTEXT:
{context}
""".strip()

    try:

        answer = GroqService(
            api_key=settings.groq_api_key,
            model=settings.groq_model,
        ).generate_answer(
            question=constrained_question,
            context=context,
        )

        answer = str(
            answer or ""
        ).strip()

        if not answer:

            return (
                "I couldn't generate an answer "
                "from the uploaded documents."
            )

        return answer

    except Exception as exc:

        logger.warning(
            "Groq generation failed for RAG query: {}",
            exc,
        )

        return (
            "I couldn't generate an answer "
            "from the uploaded documents."
        )


# ============================================================
# RAG QUERY
# ============================================================

@router.post("/rag/query")
@router.post("/rag/query")
def rag_query(body: dict[str, str], user: dict = Depends(current_user)):
    q = body.get("question", "").strip()

    if not q:
        raise HTTPException(422, "question is required")

    # First try structured dataset analysis.
    analytical = structured_answer(q, user["sub"])

    # If this is a dataset question, return the Pandas result
    # immediately. Do NOT send it to document RAG.
    if analytical:
        with connection() as conn:
            conn.execute(
                "INSERT INTO chat_history("
                "id,user_id,question,answer,sources_json,confidence"
                ") VALUES(?,?,?,?,?,?)",
                (
                    str(uuid.uuid4()),
                    user["sub"],
                    q,
                    analytical["answer"],
                    json.dumps(analytical["sources"]),
                    analytical["confidence"],
                ),
            )

        return analytical

    # Otherwise, treat it as a document/RAG question.
    matches = []

    try:
        matches = document_embeddings().similarity_search(
            q,
            top_k=5,
            owner_id=user["sub"],
        )
    except Exception as exc:
        raise HTTPException(
            503,
            f"Document retrieval is unavailable: {exc}",
        ) from exc

    if not matches:
        logger.info(
            "Copilot query found no document matches "
            "question={} collection={}",
            q,
            document_embeddings().collection_name,
        )

        return {
            "answer": (
                "No information exists in the uploaded "
                "documents relevant to this question."
            ),
            "confidence": 0.0,
            "sources": [],
            "citations": [],
            "chunks": [],
            "filename": None,
            "retrieved_chunks": 0,
            "similarity_score": 0.0,
        }

    context = build_rag_context(matches)

    answer = context[:4000]

    if settings.groq_api_key:
        try:
            answer = GroqService(
                api_key=settings.groq_api_key,
                model=settings.groq_model,
            ).generate_answer(q, context)

        except Exception as exc:
            logger.warning(
                "Groq generation failed for RAG query: {}",
                exc,
            )

            answer = (
                "I couldn't find enough information in the "
                "uploaded documents to answer this question."
            )

    confidence = round(
        sum(m["score"] for m in matches) / len(matches),
        2,
    )

    safe_matches = [
        document_embeddings().normalize_match(m)
        for m in matches
    ]

    best_match = safe_matches[0] if safe_matches else None

    citations = [
        {
            "filename": m["filename"],
            "chunk_id": m["chunk_id"],
            "document_id": m["document_id"],
        }
        for m in safe_matches
    ]

    sources = list(
        dict.fromkeys(
            f"{m['filename']} ({m['chunk_id']})"
            for m in safe_matches
        )
    )

    logger.info(
        "Copilot document retrieval question={} "
        "chunks_found={} filenames={} similarity_scores={} "
        "collection={}",
        q,
        len(matches),
        [m.get("filename") for m in safe_matches],
        [
            round(m.get("score", 0.0), 3)
            for m in safe_matches
        ],
        document_embeddings().collection_name,
    )

    with connection() as conn:
        conn.execute(
            "INSERT INTO chat_history("
            "id,user_id,question,answer,sources_json,confidence"
            ") VALUES(?,?,?,?,?,?)",
            (
                str(uuid.uuid4()),
                user["sub"],
                q,
                answer,
                json.dumps(sources),
                confidence,
            ),
        )

    return {
        "answer": answer,
        "confidence": confidence,
        "sources": sources,
        "citations": citations,
        "chunks": [
            {
                "document_id": m["document_id"],
                "chunk_id": m["chunk_id"],
                "filename": m["filename"],
                "score": round(m["score"], 3),
            }
            for m in safe_matches
        ],
        "filename": (
            best_match.get("filename")
            if best_match
            else None
        ),
        "retrieved_chunks": len(matches),
        "similarity_score": (
            round(best_match.get("score", 0.0), 3)
            if best_match
            else 0.0
        ),
    }

    # --------------------------------------------------------
    # 4. CSV-ONLY ANSWER
    #
    # This remains deterministic and accurate.
    # --------------------------------------------------------

    if analytical:

        with connection() as conn:

            conn.execute(
                """
                INSERT INTO chat_history(
                    id,
                    user_id,
                    question,
                    answer,
                    sources_json,
                    confidence
                )
                VALUES(?,?,?,?,?,?)
                """,
                (
                    str(uuid.uuid4()),
                    user["sub"],
                    q,
                    analytical["answer"],
                    json.dumps(
                        analytical["sources"]
                    ),
                    analytical["confidence"],
                ),
            )

        return analytical

    # --------------------------------------------------------
    # 5. No documents found.
    # --------------------------------------------------------

    if not matches:

        logger.info(
            "Copilot query found no document "
            "matches question={} collection={}",
            q,
            document_embeddings().collection_name,
        )

        return {
            "answer": (
                "No relevant information was found "
                "in the uploaded documents."
            ),
            "confidence": 0.0,
            "sources": [],
            "citations": [],
            "chunks": [],
            "filename": None,
            "retrieved_chunks": 0,
            "similarity_score": 0.0,
        }

    # --------------------------------------------------------
    # 6. RAG ONLY
    # --------------------------------------------------------

    context = build_rag_context(
        matches,
        max_chunks=3,
        max_chars_per_chunk=1200,
        max_total_chars=4000,
    )

    answer = generate_rag_answer(
        q,
        context,
    )

    safe_matches = [
        document_embeddings().normalize_match(m)
        for m in matches
    ]

    scores = [
        float(m.get("score", 0.0))
        for m in safe_matches
    ]

    confidence = round(
        sum(scores) / len(scores),
        2,
    ) if scores else 0.0

    best_match = (
        safe_matches[0]
        if safe_matches
        else None
    )

    citations = [
        {
            "filename": m["filename"],
            "chunk_id": m["chunk_id"],
            "document_id": m["document_id"],
        }
        for m in safe_matches
    ]

    sources = list(
        dict.fromkeys(
            [
                f"{m['filename']} "
                f"({m['chunk_id']})"
                for m in safe_matches
            ]
        )
    )

    logger.info(
        "Copilot document retrieval "
        "question={} chunks_found={} "
        "filenames={} similarity_scores={} "
        "collection={}",
        q,
        len(matches),
        [
            m.get("filename")
            for m in safe_matches
        ],
        [
            round(
                m.get(
                    "score",
                    0.0,
                ),
                3,
            )
            for m in safe_matches
        ],
        document_embeddings().collection_name,
    )

    with connection() as conn:

        conn.execute(
            """
            INSERT INTO chat_history(
                id,
                user_id,
                question,
                answer,
                sources_json,
                confidence
            )
            VALUES(?,?,?,?,?,?)
            """,
            (
                str(uuid.uuid4()),
                user["sub"],
                q,
                answer,
                json.dumps(sources),
                confidence,
            ),
        )

    return {
        "answer": answer,
        "confidence": confidence,
        "sources": sources,
        "citations": citations,

        "chunks": [
            {
                "document_id": m["document_id"],
                "chunk_id": m["chunk_id"],
                "filename": m["filename"],
                "score": round(
                    m["score"],
                    3,
                ),
            }
            for m in safe_matches
        ],

        "filename": (
            best_match.get("filename")
            if best_match
            else None
        ),

        "retrieved_chunks": len(matches),

        "similarity_score": (
            round(
                best_match.get(
                    "score",
                    0.0,
                ),
                3,
            )
            if best_match
            else 0.0
        ),
    }


# ============================================================
# RAG DEBUG
# ============================================================

@router.get("/rag/debug")
def rag_debug():

    emb = document_embeddings()

    return {
        "collection": emb.collection_name,
        "count": emb.collection.count(),
        "stats": emb.collection_stats(),
    }


# ============================================================
# RAG REINDEX
# ============================================================

@router.post("/rag/reindex")
def reindex_rag_documents(
    user: dict = Depends(current_user),
):

    try:

        result = document_embeddings().reindex_documents(
            owner_id=user["sub"]
        )

    except Exception as exc:

        logger.exception(
            "RAG reindex failed for owner {}",
            user["sub"],
        )

        raise HTTPException(
            503,
            f"RAG reindex is unavailable: {exc}",
        ) from exc

    return result


# ============================================================
# GLOBAL SEARCH
# ============================================================

@router.get("/search")
def search(
    q: str,
    user: dict = Depends(current_user),
):

    q = q.strip()

    if not q:

        raise HTTPException(
            422,
            "q is required",
        )

    pattern = f"%{q}%"

    results = []

    with connection() as conn:

        for row in conn.execute(
            """
            SELECT
                c.id,
                c.name,
                c.email
            FROM customers c
            JOIN datasets d
                ON d.id=c.dataset_id
            WHERE d.owner_id=?
              AND (
                  c.id LIKE ?
                  OR c.name LIKE ?
                  OR c.email LIKE ?
              )
            """,
            (
                user["sub"],
                pattern,
                pattern,
                pattern,
            ),
        ):

            results.append(
                {
                    "type": "customer",
                    "id": row["id"],
                    "title": (
                        row["name"]
                        or row["id"]
                    ),
                    "subtitle": row["email"],
                }
            )

        for row in conn.execute(
            """
            SELECT id,filename
            FROM datasets
            WHERE owner_id=?
              AND filename LIKE ?
            """,
            (
                user["sub"],
                pattern,
            ),
        ):

            results.append(
                {
                    "type": "dataset",
                    "id": row["id"],
                    "title": row["filename"],
                }
            )

        for row in conn.execute(
            """
            SELECT id,filename
            FROM documents
            WHERE owner_id=?
              AND (
                  filename LIKE ?
                  OR content LIKE ?
              )
            """,
            (
                user["sub"],
                pattern,
                pattern,
            ),
        ):

            results.append(
                {
                    "type": "document",
                    "id": row["id"],
                    "title": row["filename"],
                }
            )

        for row in conn.execute(
            """
            SELECT
                p.id,
                p.prediction,
                p.customer_id
            FROM predictions p
            JOIN datasets d
                ON p.dataset_id=d.id
            WHERE d.owner_id=?
              AND (
                  p.prediction LIKE ?
                  OR p.customer_id LIKE ?
              )
            """,
            (
                user["sub"],
                pattern,
                pattern,
            ),
        ):

            results.append(
                {
                    "type": "prediction",
                    "id": row["id"],
                    "title": row["prediction"],
                    "subtitle": row["customer_id"],
                }
            )

        for row in conn.execute(
            """
            SELECT id,question,answer
            FROM chat_history
            WHERE user_id=?
              AND (
                  question LIKE ?
                  OR answer LIKE ?
              )
            """,
            (
                user["sub"],
                pattern,
                pattern,
            ),
        ):

            results.append(
                {
                    "type": "chat",
                    "id": row["id"],
                    "title": row["question"],
                    "subtitle": row["answer"][:160],
                }
            )

    return {
        "query": q,
        "results": results[:100],
    }


# ============================================================
# DASHBOARD REPORT
# ============================================================

@router.get("/reports/dashboard")
def report_dashboard(
    format: str = "json",
    user: dict = Depends(current_user),
):

    data = dashboard(user)

    if format == "json":

        return data

    if format == "csv":

        stream = BytesIO(
            pd.DataFrame(
                [data]
            )
            .to_csv(index=False)
            .encode()
        )

        return StreamingResponse(
            stream,
            media_type="text/csv",
            headers={
                "Content-Disposition":
                    "attachment; "
                    "filename=dashboard-report.csv"
            },
        )

    if format == "xlsx":

        try:

            stream = BytesIO()

            pd.DataFrame(
                [data]
            ).to_excel(
                stream,
                index=False,
            )

            stream.seek(0)

            return StreamingResponse(
                stream,
                media_type=(
                    "application/vnd.openxmlformats-"
                    "officedocument.spreadsheetml.sheet"
                ),
                headers={
                    "Content-Disposition":
                        "attachment; "
                        "filename=dashboard-report.xlsx"
                },
            )

        except ImportError as exc:

            raise HTTPException(
                503,
                "Excel export dependency is unavailable",
            ) from exc

    raise HTTPException(
        422,
        "format must be json, csv, or xlsx",
    )