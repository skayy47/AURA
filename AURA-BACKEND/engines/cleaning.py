"""Production-grade cleaning pipeline — the Cleaning Team.

Each cleaner is an isolated BaseCleaner implementation. The CleaningOrchestrator
runs them in a deterministic order. Every step emits a structured entry into
CleaningReport so the UI can render an audit trail.

Public surface:
    CleaningConfig            - per-step toggles (Pydantic-friendly dataclass)
    CleaningReport            - accumulated log of changes
    BaseCleaner               - ABC for individual cleaners
    ColumnNormalizer,
    EmptyDropper,
    StringCleaner,
    TypePromoter,
    DuplicateHandler,
    MissingValueImputer,
    OutlierFlagger,
    SchemaValidator           - concrete cleaners
    CleaningOrchestrator      - runs the team
    clean_dataframe(df, cfg)  - legacy wrapper (Streamlit compat)
"""
from __future__ import annotations

import logging
import re
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any

import pandas as pd
from pandas.api.types import (
    is_datetime64_any_dtype,
    is_numeric_dtype,
    is_string_dtype,
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Config + Report
# ---------------------------------------------------------------------------

@dataclass
class CleaningConfig:
    rename_columns: bool = True
    normalize_strings: bool = True
    detect_dates: bool = True      # controls the full TypePromoter
    remove_empty_cols: bool = True
    fill_missing: bool = True
    drop_duplicates: bool = True


@dataclass
class CleaningReport:
    steps: list[dict[str, Any]] = field(default_factory=list)

    def log(
        self,
        step: str,
        affected: list[str],
        detail: str,
        rows_changed: int = 0,
        status: str = "ok",
    ) -> None:
        self.steps.append({
            "step": step,
            "affected_columns": list(affected),
            "detail": detail,
            "rows_changed": int(rows_changed),
            "status": status,
        })


# ---------------------------------------------------------------------------
# Base
# ---------------------------------------------------------------------------

class BaseCleaner(ABC):
    name: str

    @abstractmethod
    def run(self, df: pd.DataFrame, report: CleaningReport) -> pd.DataFrame:
        ...


# ---------------------------------------------------------------------------
# 1. ColumnNormalizer
# ---------------------------------------------------------------------------

class ColumnNormalizer(BaseCleaner):
    name = "Column Normalizer"

    _non_word = re.compile(r"[^\w\s]", flags=re.UNICODE)
    _ws = re.compile(r"\s+")
    _multi_under = re.compile(r"_+")

    def run(self, df: pd.DataFrame, report: CleaningReport) -> pd.DataFrame:
        original = [str(c) for c in df.columns]
        df = df.copy()

        new_cols: list[str] = []
        seen: dict[str, bool] = {}
        for idx, col in enumerate(original):
            clean = self._normalize_one(col) or f"col_{idx}"
            base = clean
            counter = 1
            while clean in seen:
                clean = f"{base}_{counter}"
                counter += 1
            seen[clean] = True
            new_cols.append(clean)

        df.columns = new_cols
        changed = [(o, n) for o, n in zip(original, new_cols) if o != n]
        examples = ", ".join(f"{o}→{n}" for o, n in changed[:3])
        detail = (
            f"Renamed {len(changed)} column(s) to snake_case."
            + (f" Examples: {examples}" if changed else " All columns already clean.")
        )
        report.log(self.name, [n for _, n in changed], detail)
        return df

    def _normalize_one(self, col: str) -> str:
        clean = col.strip()
        clean = self._non_word.sub("", clean)
        clean = self._ws.sub("_", clean).lower()
        clean = self._multi_under.sub("_", clean).strip("_")
        return clean


# ---------------------------------------------------------------------------
# 2. EmptyDropper
# ---------------------------------------------------------------------------

class EmptyDropper(BaseCleaner):
    name = "Empty Dropper"

    def __init__(self, col_threshold: float = 1.0, row_threshold: float = 1.0) -> None:
        self.col_threshold = col_threshold
        self.row_threshold = row_threshold

    def run(self, df: pd.DataFrame, report: CleaningReport) -> pd.DataFrame:
        before_rows = len(df)

        if df.shape[1] == 0:
            report.log(self.name, [], "No columns to evaluate.")
            return df

        null_rate_cols = df.isnull().mean()
        cols_to_drop = null_rate_cols[null_rate_cols >= self.col_threshold].index.tolist()
        df = df.drop(columns=cols_to_drop)

        if df.shape[1] > 0:
            null_rate_rows = df.isnull().mean(axis=1)
            df = df[null_rate_rows < self.row_threshold].reset_index(drop=True)

        rows_dropped = before_rows - len(df)
        detail = (
            f"Dropped {len(cols_to_drop)} empty column(s) "
            f"and {rows_dropped} empty row(s)."
        )
        report.log(
            self.name,
            [str(c) for c in cols_to_drop],
            detail,
            rows_changed=rows_dropped,
        )
        return df


# ---------------------------------------------------------------------------
# 3. StringCleaner
# ---------------------------------------------------------------------------

class StringCleaner(BaseCleaner):
    name = "String Cleaner"

    _ws = re.compile(r"\s+")

    def run(self, df: pd.DataFrame, report: CleaningReport) -> pd.DataFrame:
        df = df.copy()
        affected: list[str] = []

        for col in df.select_dtypes(include=["object", "string"]).columns:
            before = df[col].copy()
            cleaned = (
                df[col].astype(str)
                .str.strip()
                .str.replace(self._ws, " ", regex=True)
            )
            cleaned = cleaned.replace(
                {"nan": pd.NA, "None": pd.NA, "NaT": pd.NA, "": pd.NA, "null": pd.NA, "NULL": pd.NA}
            )
            df[col] = cleaned
            if not before.equals(df[col]):
                affected.append(str(col))

        detail = (
            f"Stripped whitespace and normalized null strings in {len(affected)} column(s)."
            if affected else "No string normalization needed."
        )
        report.log(self.name, affected, detail)
        return df


# ---------------------------------------------------------------------------
# 4. TypePromoter
# ---------------------------------------------------------------------------

class TypePromoter(BaseCleaner):
    name = "Type Promoter"
    DATE_THRESHOLD = 0.75
    NUMERIC_THRESHOLD = 0.90
    BOOL_THRESHOLD = 0.95

    _bool_truthy = {"true", "yes", "y", "t", "1"}
    _bool_falsy = {"false", "no", "n", "f", "0"}

    def run(self, df: pd.DataFrame, report: CleaningReport) -> pd.DataFrame:
        df = df.copy()
        promoted: dict[str, str] = {}

        for col in df.select_dtypes(include="object").columns:
            series = df[col].dropna()
            if series.empty:
                continue

            s_str = series.astype(str).str.strip()
            s_lower = s_str.str.lower()

            # Boolean check
            all_bool_vals = self._bool_truthy | self._bool_falsy
            if s_lower.isin(all_bool_vals).mean() >= self.BOOL_THRESHOLD:
                bool_map = {
                    **{k: True for k in self._bool_truthy},
                    **{k: False for k in self._bool_falsy},
                }
                df[col] = (
                    df[col].astype("object").astype(str).str.lower().str.strip().map(bool_map)
                )
                promoted[str(col)] = "→ bool"
                continue

            # Numeric check — allow thousands-separator commas
            numeric_probe = pd.to_numeric(
                s_str.str.replace(",", "", regex=False), errors="coerce"
            )
            if numeric_probe.notna().mean() >= self.NUMERIC_THRESHOLD:
                df[col] = pd.to_numeric(
                    df[col].astype(str).str.replace(",", "", regex=False),
                    errors="coerce",
                )
                promoted[str(col)] = "→ numeric"
                continue

            # Datetime check
            try:
                dates = pd.to_datetime(s_str, errors="coerce", format="mixed")
            except Exception:
                dates = pd.to_datetime(s_str, errors="coerce")
            if dates.notna().mean() >= self.DATE_THRESHOLD:
                try:
                    df[col] = pd.to_datetime(df[col], errors="coerce", format="mixed")
                except Exception:
                    df[col] = pd.to_datetime(df[col], errors="coerce")
                promoted[str(col)] = "→ datetime"
                continue

            # Category for low-cardinality strings
            try:
                n_unique = series.nunique()
                if n_unique > 0 and n_unique <= 100 and n_unique / max(len(series), 1) < 0.05:
                    df[col] = df[col].astype("category")
                    promoted[str(col)] = "→ category"
            except Exception:
                continue

        examples = ", ".join(f"{c} {t}" for c, t in list(promoted.items())[:5])
        if len(promoted) > 5:
            examples += f" ... +{len(promoted) - 5} more"
        detail = (
            f"Promoted {len(promoted)} column(s): {examples}"
            if promoted else "No type promotions needed."
        )
        report.log(self.name, list(promoted.keys()), detail)
        return df


# ---------------------------------------------------------------------------
# 5. DuplicateHandler
# ---------------------------------------------------------------------------

class DuplicateHandler(BaseCleaner):
    name = "Duplicate Handler"

    def run(self, df: pd.DataFrame, report: CleaningReport) -> pd.DataFrame:
        before = len(df)

        # Phase 1: exact duplicates
        df = df.drop_duplicates().reset_index(drop=True)
        exact_removed = before - len(df)

        # Phase 2: case-variant duplicates on string columns
        str_cols = df.select_dtypes(include="object").columns.tolist()
        near_removed = 0
        if str_cols:
            normalized = df.copy()
            for c in str_cols:
                normalized[c] = (
                    normalized[c].astype(str).str.lower().str.strip()
                )
            dup_mask = normalized.duplicated(keep="first")
            near_removed = int(dup_mask.sum())
            if near_removed:
                df = df[~dup_mask].reset_index(drop=True)

        total_removed = before - len(df)
        detail = (
            f"Removed {exact_removed} exact + {near_removed} case-variant duplicate(s). "
            f"{total_removed} row(s) eliminated total."
        )
        report.log(self.name, [], detail, rows_changed=total_removed)
        return df


# ---------------------------------------------------------------------------
# 6. MissingValueImputer
# ---------------------------------------------------------------------------

class MissingValueImputer(BaseCleaner):
    name = "Missing Value Imputer"

    def run(self, df: pd.DataFrame, report: CleaningReport) -> pd.DataFrame:
        df = df.copy()
        detail_parts: list[str] = []
        affected: list[str] = []

        n_rows = max(len(df), 1)

        for col in df.columns:
            series = df[col]
            n_missing = int(series.isna().sum())
            if n_missing == 0:
                continue

            missing_rate = n_missing / n_rows
            if missing_rate > 0.5:
                # >50% missing — don't invent data; EmptyDropper handles truly empty
                continue

            if is_numeric_dtype(series):
                non_null = series.dropna()
                if len(non_null) == 0:
                    continue
                try:
                    skewness = abs(non_null.skew()) if len(non_null) > 3 else 0
                except Exception:
                    skewness = 0
                if skewness > 1.0:
                    fill_val = float(non_null.median())
                    strategy = f"median={fill_val:.2f}"
                else:
                    fill_val = float(non_null.mean())
                    strategy = f"mean={fill_val:.2f}"
                df[col] = series.fillna(fill_val)

            elif is_datetime64_any_dtype(series):
                df[col] = series.ffill().bfill()
                strategy = "ffill+bfill"

            elif hasattr(series, "cat") or is_string_dtype(series):
                try:
                    mode = series.mode(dropna=True)
                except Exception:
                    mode = pd.Series(dtype=object)
                if not mode.empty:
                    fill_val = mode.iloc[0]
                    df[col] = series.fillna(fill_val)
                    strategy = f"mode='{fill_val}'"
                else:
                    df[col] = series.fillna("Unknown")
                    strategy = "→ 'Unknown'"
            else:
                continue

            affected.append(str(col))
            detail_parts.append(f"{col} ({n_missing} gaps, {strategy})")

        if detail_parts:
            shown = "; ".join(detail_parts[:4])
            if len(detail_parts) > 4:
                shown += f" +{len(detail_parts) - 4} more"
        else:
            shown = "No missing values found."

        report.log(self.name, affected, shown)
        return df


# ---------------------------------------------------------------------------
# 7. OutlierFlagger
# ---------------------------------------------------------------------------

class OutlierFlagger(BaseCleaner):
    name = "Outlier Flagger"
    IQR_MULTIPLIER = 3.0

    def run(self, df: pd.DataFrame, report: CleaningReport) -> pd.DataFrame:
        df = df.copy()
        flagged_cols: list[str] = []
        total_outliers = 0
        n_rows = len(df)

        if n_rows == 0:
            report.log(self.name, [], "No rows to evaluate.")
            return df

        for col in df.select_dtypes(include="number").columns:
            # Don't treat existing boolean flags as candidates
            if str(col).endswith("_outlier"):
                continue
            series = df[col].dropna()
            if len(series) < 10:
                continue
            Q1 = series.quantile(0.25)
            Q3 = series.quantile(0.75)
            IQR = Q3 - Q1
            if IQR == 0:
                continue
            lower = Q1 - self.IQR_MULTIPLIER * IQR
            upper = Q3 + self.IQR_MULTIPLIER * IQR
            outlier_mask = (df[col] < lower) | (df[col] > upper)
            n_outliers = int(outlier_mask.sum())
            if 0 < n_outliers < 0.1 * n_rows:
                flag_col = f"{col}_outlier"
                df[flag_col] = outlier_mask.fillna(False).astype(bool)
                flagged_cols.append(str(col))
                total_outliers += n_outliers

        if flagged_cols:
            detail = (
                f"Flagged {total_outliers} extreme outlier(s) (IQR×{self.IQR_MULTIPLIER}) "
                f"across {len(flagged_cols)} column(s). Added `_outlier` flag columns — data NOT removed."
            )
        else:
            detail = "No extreme outliers detected."
        report.log(self.name, flagged_cols, detail, rows_changed=total_outliers)
        return df


# ---------------------------------------------------------------------------
# 8. SchemaValidator
# ---------------------------------------------------------------------------

class SchemaValidator(BaseCleaner):
    name = "Schema Validator"

    def run(self, df: pd.DataFrame, report: CleaningReport) -> pd.DataFrame:
        n_rows, n_cols = df.shape
        denom = n_rows * n_cols

        missing_rate = float(df.isnull().sum().sum() / denom) if denom > 0 else 0.0
        dup_rate = float(df.duplicated().sum() / n_rows) if n_rows > 0 else 0.0

        object_rate = (
            df.select_dtypes(include="object").shape[1] / max(n_cols, 1)
        )

        score = 100.0
        score -= min(missing_rate * 200, 40)
        score -= min(dup_rate * 100, 20)
        score -= 10 if object_rate > 0.8 else 0
        score = round(max(score, 0.0), 1)

        detail = (
            f"Quality score: {score}/100 | "
            f"Missing rate: {missing_rate:.1%} | "
            f"Duplicate rate: {dup_rate:.1%} | "
            f"Final shape: {n_rows:,} rows × {n_cols} cols"
        )
        report.log(self.name, [], detail)
        return df


# ---------------------------------------------------------------------------
# Orchestrator
# ---------------------------------------------------------------------------

_CONFIG_MAP = {
    "Column Normalizer":       "rename_columns",
    "Empty Dropper":           "remove_empty_cols",
    "String Cleaner":          "normalize_strings",
    "Type Promoter":           "detect_dates",   # proxy — covers full type promotion
    "Duplicate Handler":       "drop_duplicates",
    "Missing Value Imputer":   "fill_missing",
}


class CleaningOrchestrator:
    """Runs the cleaning team in the correct sequence."""

    @classmethod
    def default_team(cls) -> list[BaseCleaner]:
        return [
            ColumnNormalizer(),
            EmptyDropper(col_threshold=1.0, row_threshold=1.0),
            StringCleaner(),
            TypePromoter(),
            DuplicateHandler(),
            MissingValueImputer(),
            OutlierFlagger(),
            SchemaValidator(),
        ]

    def __init__(self, team: list[BaseCleaner] | None = None) -> None:
        self.team = team if team is not None else self.default_team()

    def clean(
        self,
        df: pd.DataFrame,
        config: CleaningConfig | None = None,
    ) -> tuple[pd.DataFrame, CleaningReport]:
        report = CleaningReport()
        cfg = config or CleaningConfig()

        for cleaner in self.team:
            if not self._is_enabled(cleaner, cfg):
                continue
            try:
                df = cleaner.run(df, report)
                logger.info("[%s] done — %s rows × %s cols", cleaner.name, *df.shape)
            except Exception as exc:  # never hard-crash the pipeline
                logger.exception("[%s] failed: %s", cleaner.name, exc)
                report.log(
                    cleaner.name, [], f"SKIPPED due to error: {exc}", status="error",
                )

        return df, report

    @staticmethod
    def _is_enabled(cleaner: BaseCleaner, config: CleaningConfig) -> bool:
        config_key = _CONFIG_MAP.get(cleaner.name)
        if config_key is None:
            return True  # validators always run
        return bool(getattr(config, config_key, True))


# ---------------------------------------------------------------------------
# Legacy wrapper — keeps the Streamlit app importing `clean_dataframe`
# ---------------------------------------------------------------------------

def clean_dataframe(
    df: pd.DataFrame,
    config: CleaningConfig | None = None,
) -> tuple[pd.DataFrame, list[dict]]:
    """Backward-compatible entry point. Returns (cleaned_df, log_list)."""
    orchestrator = CleaningOrchestrator()
    cleaned, report = orchestrator.clean(df.copy(), config)
    return cleaned, report.steps
