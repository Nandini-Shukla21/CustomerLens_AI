from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from app.config import Settings
from app.models.response_models import DashboardResponse
from app.services.chat_service import ChatService


class DashboardService:
    """Service for dashboard summary and dynamic dataset analytics."""

    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.chat_service = ChatService()

        # Uploaded CSV files are stored in the backend/uploads directory.
        self.uploads_dir = Path(__file__).resolve().parents[2] / "uploads"
        self.uploads_dir.mkdir(parents=True, exist_ok=True)

    # ============================================================
    # EXISTING DASHBOARD METHODS
    # ============================================================

    def get_dashboard_summary(self) -> DashboardResponse:
        """Return a lightweight dashboard payload."""

        overview = self.chat_service.get_dashboard_overview()

        return DashboardResponse(
            message="Dashboard overview generated",
            metrics={
                "total_customers": overview["total_customers"],
                "revenue": overview["revenue"],
                "average_spend": overview["average_spend"],
                "churn": overview["churn"],
                "fraud_alerts": overview["fraud_alerts"],
            },
        )

    def get_dashboard_overview(self) -> dict[str, object]:
        """Return the existing Recharts-ready overview payload."""
        return self.chat_service.get_dashboard_overview()

    # ============================================================
    # DATASET DISCOVERY
    # ============================================================

    def get_available_datasets(self) -> dict[str, object]:
        """
        Return all uploaded CSV datasets.

        Example response:

        {
            "datasets": [
                {
                    "name": "employee_survey.csv",
                    "rows": 3025,
                    "columns": 23
                },
                {
                    "name": "customers.csv",
                    "rows": 793,
                    "columns": 5
                }
            ]
        }
        """

        datasets: list[dict[str, Any]] = []

        if not self.uploads_dir.exists():
            return {
                "datasets": [],
                "count": 0,
            }

        for csv_file in sorted(self.uploads_dir.glob("*.csv")):
            try:
                df = pd.read_csv(csv_file)

                datasets.append(
                    {
                        "name": csv_file.name,
                        "rows": int(len(df)),
                        "columns": int(len(df.columns)),
                    }
                )

            except Exception:
                # Ignore files that cannot be read as valid CSV files.
                continue

        return {
            "datasets": datasets,
            "count": len(datasets),
        }

    # ============================================================
    # DATASET ANALYSIS
    # ============================================================

    def get_dataset_dashboard(self, dataset_name: str) -> dict[str, object]:
        """
        Analyze one selected CSV dataset and return chart-ready data.

        The analysis is completely dynamic and does not depend on
        specific column names.
        """

        dataset_path = self._get_safe_dataset_path(dataset_name)

        if not dataset_path.exists():
            raise FileNotFoundError(
                f"Dataset '{dataset_name}' was not found."
            )

        try:
            df = pd.read_csv(dataset_path)
        except Exception as exc:
            raise ValueError(
                f"Unable to read dataset '{dataset_name}': {exc}"
            ) from exc

        if df.empty:
            raise ValueError(
                f"Dataset '{dataset_name}' is empty."
            )

        # --------------------------------------------------------
        # Clean column names
        # --------------------------------------------------------

        df.columns = [
            str(column).strip()
            for column in df.columns
        ]

        # --------------------------------------------------------
        # Detect column types
        # --------------------------------------------------------

        numeric_columns = df.select_dtypes(
            include=["number"]
        ).columns.tolist()

        categorical_columns = df.select_dtypes(
            include=["object", "category", "bool"]
        ).columns.tolist()

        # Some columns may be stored as objects even though they
        # contain numbers. Try to detect those as well.
        for column in df.columns:
            if column in numeric_columns:
                continue

            if column in categorical_columns:
                continue

            converted = pd.to_numeric(
                df[column],
                errors="coerce",
            )

            if converted.notna().sum() >= max(
                1,
                int(len(df) * 0.8),
            ):
                numeric_columns.append(column)

        # --------------------------------------------------------
        # Basic dataset information
        # --------------------------------------------------------

        missing_values = int(
            df.isna().sum().sum()
        )

        duplicate_rows = int(
            df.duplicated().sum()
        )

        dataset_info = {
            "name": dataset_path.name,
            "rows": int(len(df)),
            "columns": int(len(df.columns)),
            "numeric_columns": numeric_columns,
            "categorical_columns": categorical_columns,
            "missing_values": missing_values,
            "duplicate_rows": duplicate_rows,
        }

        # --------------------------------------------------------
        # Generate charts
        # --------------------------------------------------------

        charts: list[dict[str, object]] = []

        # ========================================================
        # CHART 1 — Categorical distribution
        # ========================================================

        if categorical_columns:

            category_column = self._select_best_categorical_column(
                df,
                categorical_columns,
            )

            value_counts = (
                df[category_column]
                .fillna("Missing")
                .astype(str)
                .value_counts()
                .head(10)
            )

            chart_data = [
                {
                    "name": str(index),
                    "value": int(value),
                }
                for index, value in value_counts.items()
            ]

            charts.append(
                {
                    "id": "categorical_distribution",
                    "title": f"{category_column} Distribution",
                    "type": "bar",
                    "xKey": "name",
                    "yKey": "value",
                    "data": chart_data,
                    "column": category_column,
                }
            )

        # ========================================================
        # CHART 2 — Numeric average by column
        # ========================================================

        if numeric_columns:

            numeric_summary: list[dict[str, object]] = []

            for column in numeric_columns[:10]:

                numeric_series = pd.to_numeric(
                    df[column],
                    errors="coerce",
                )

                if numeric_series.notna().sum() == 0:
                    continue

                numeric_summary.append(
                    {
                        "name": str(column),
                        "value": round(
                            float(numeric_series.mean()),
                            2,
                        ),
                    }
                )

            if numeric_summary:

                charts.append(
                    {
                        "id": "numeric_averages",
                        "title": "Average Numeric Values",
                        "type": "bar",
                        "xKey": "name",
                        "yKey": "value",
                        "data": numeric_summary,
                    }
                )

        # ========================================================
        # CHART 3 — Distribution of first useful numeric column
        # ========================================================

        if numeric_columns:

            numeric_column = self._select_best_numeric_column(
                df,
                numeric_columns,
            )

            series = pd.to_numeric(
                df[numeric_column],
                errors="coerce",
            ).dropna()

            if not series.empty:

                histogram_data = self._create_histogram(
                    series
                )

                charts.append(
                    {
                        "id": "numeric_distribution",
                        "title": f"{numeric_column} Distribution",
                        "type": "bar",
                        "xKey": "name",
                        "yKey": "value",
                        "data": histogram_data,
                        "column": numeric_column,
                    }
                )

        # ========================================================
        # CHART 4 — Missing values by column
        # ========================================================

        missing_by_column = (
            df.isna()
            .sum()
            .sort_values(
                ascending=False
            )
            .head(10)
        )

        missing_chart_data = [
            {
                "name": str(index),
                "value": int(value),
            }
            for index, value in missing_by_column.items()
            if int(value) > 0
        ]

        if missing_chart_data:

            charts.append(
                {
                    "id": "missing_values",
                    "title": "Missing Values by Column",
                    "type": "bar",
                    "xKey": "name",
                    "yKey": "value",
                    "data": missing_chart_data,
                }
            )

        # ========================================================
        # If there are not enough charts, create a column summary
        # ========================================================

        if len(charts) < 3:

            column_summary = [
                {
                    "name": str(column),
                    "value": int(
                        df[column].nunique(
                            dropna=True
                        )
                    ),
                }
                for column in df.columns[:15]
            ]

            charts.append(
                {
                    "id": "unique_values",
                    "title": "Unique Values by Column",
                    "type": "bar",
                    "xKey": "name",
                    "yKey": "value",
                    "data": column_summary,
                }
            )

        # Only return a maximum of four charts.
        charts = charts[:4]

        # --------------------------------------------------------
        # Column-level summary
        # --------------------------------------------------------

        column_details: list[dict[str, object]] = []

        for column in df.columns:

            series = df[column]

            if column in numeric_columns:

                numeric_series = pd.to_numeric(
                    series,
                    errors="coerce",
                )

                column_details.append(
                    {
                        "name": str(column),
                        "type": "numeric",
                        "missing": int(series.isna().sum()),
                        "unique": int(
                            series.nunique(
                                dropna=True
                            )
                        ),
                        "mean": self._safe_float(
                            numeric_series.mean()
                        ),
                        "min": self._safe_float(
                            numeric_series.min()
                        ),
                        "max": self._safe_float(
                            numeric_series.max()
                        ),
                    }
                )

            else:

                column_details.append(
                    {
                        "name": str(column),
                        "type": "categorical",
                        "missing": int(series.isna().sum()),
                        "unique": int(
                            series.nunique(
                                dropna=True
                            )
                        ),
                    }
                )

        # --------------------------------------------------------
        # Return complete dashboard payload
        # --------------------------------------------------------

        return {
            "dataset": dataset_info,
            "charts": charts,
            "columns": column_details,
        }

    # ============================================================
    # HELPER METHODS
    # ============================================================

    def _get_safe_dataset_path(
        self,
        dataset_name: str,
    ) -> Path:
        """
        Safely resolve a dataset path inside the uploads directory.
        """

        requested_path = (
            self.uploads_dir / dataset_name
        ).resolve()

        uploads_root = (
            self.uploads_dir.resolve()
        )

        try:
            requested_path.relative_to(
                uploads_root
            )
        except ValueError as exc:
            raise ValueError(
                "Invalid dataset path."
            ) from exc

        return requested_path

    def _select_best_categorical_column(
        self,
        df: pd.DataFrame,
        columns: list[str],
    ) -> str:
        """
        Select a useful categorical column.

        Preference is given to columns with a reasonable number
        of unique values, rather than ID-like columns.
        """

        candidates: list[tuple[str, int]] = []

        for column in columns:

            unique_count = int(
                df[column].nunique(
                    dropna=True
                )
            )

            if unique_count <= 30:
                candidates.append(
                    (
                        column,
                        unique_count,
                    )
                )

        if candidates:

            # Prefer a column with more than one category
            # but not an extremely high cardinality.
            candidates.sort(
                key=lambda item: (
                    item[1] > 1,
                    item[1] <= 15,
                    -item[1],
                ),
                reverse=True,
            )

            return candidates[0][0]

        return columns[0]

    def _select_best_numeric_column(
        self,
        df: pd.DataFrame,
        columns: list[str],
    ) -> str:
        """
        Select a useful numeric column.

        Avoid ID-like columns where possible.
        """

        for column in columns:

            unique_count = int(
                df[column].nunique(
                    dropna=True
                )
            )

            # Avoid columns that look like IDs.
            column_lower = column.lower()

            if (
                "id" not in column_lower
                and unique_count > 1
            ):
                return column

        return columns[0]

    def _create_histogram(
        self,
        series: pd.Series,
    ) -> list[dict[str, object]]:
        """
        Create a simple histogram using Pandas.
        """

        if series.empty:
            return []

        minimum = float(series.min())
        maximum = float(series.max())

        # Constant-value column.
        if minimum == maximum:

            return [
                {
                    "name": self._format_number(
                        minimum
                    ),
                    "value": int(len(series)),
                }
            ]

        # Use up to 10 bins for a clean dashboard.
        bins_count = min(
            10,
            max(
                5,
                int(series.nunique()),
            ),
        )

        try:

            categories = pd.cut(
                series,
                bins=bins_count,
                include_lowest=True,
            )

            counts = (
                categories
                .value_counts()
                .sort_index()
            )

            result: list[dict[str, object]] = []

            for interval, count in counts.items():

                result.append(
                    {
                        "name": str(interval),
                        "value": int(count),
                    }
                )

            return result

        except Exception:
            return []

    @staticmethod
    def _safe_float(
        value: Any,
    ) -> float | None:
        """Convert a Pandas numeric value safely to float."""

        try:

            if pd.isna(value):
                return None

            return round(
                float(value),
                2,
            )

        except (TypeError, ValueError):
            return None

    @staticmethod
    def _format_number(
        value: float,
    ) -> str:
        """Format a numeric value for chart labels."""

        if value.is_integer():
            return str(int(value))

        return f"{value:.2f}"