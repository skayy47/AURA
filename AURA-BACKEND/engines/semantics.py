"""Semantic column-role inference — the brain that makes AURA data-dependent.

Every other engine (exploration, analysis, AI suggestions, the report) should
ask THIS module "what is each column, really?" instead of naively grabbing
``numeric_cols[0]``. That is the difference between "row_id is rising over time"
(wrong) and "Profit is rising over time" (right).

Roles
-----
    identifier  row_id, order_id, uuid, sku — keys, never a measure
    measure     genuine numeric quantity — sales, profit, age, score
    dimension   low-cardinality category to slice by — segment, region
    temporal    datetime axis — order_date, ship_date
    geo         spatial column — postal_code, city, state, country, lat/lng
    boolean     two-state flag
    text        free / high-cardinality text — names, descriptions
    constant    a single repeated value (no analytical signal)

Pure pandas/numpy. No LLM. JSON-serializable output. Every column is wrapped
defensively and degrades to ``text`` on error.

Public entry point:
    infer_semantics(df, profile) -> dict
"""

from __future__ import annotations

import logging
import re
from typing import Any

import pandas as pd
from pandas.api.types import (
    is_bool_dtype,
    is_datetime64_any_dtype,
    is_integer_dtype,
    is_numeric_dtype,
)

logger = logging.getLogger(__name__)

# Roles
IDENTIFIER = "identifier"
MEASURE = "measure"
DIMENSION = "dimension"
TEMPORAL = "temporal"
GEO = "geo"
BOOLEAN = "boolean"
TEXT = "text"
CONSTANT = "constant"

# ---------------------------------------------------------------------------
# Name patterns (matched against a normalized snake_case column name)
# ---------------------------------------------------------------------------

_ID_RE = re.compile(
    r"(^|_)(id|ids|uuid|guid|key|code|sku|ref|reference|no|num|number|index|idx|hash|"
    r"isbn|ssn|account|acct)(_|$)|(^|_)id$|_id$|^id$"
)
_GEO_RE = re.compile(
    r"(^|_)(zip|zipcode|postal|postcode|post_code|lat|lat_?long|latitude|lon|lng|"
    r"long|longitude|country|state|province|city|region|county|district|"
    r"municipality|address|location|geo|geohash|fips|borough|ward|territory)(_|$)"
)
_TEMPORAL_NAME_RE = re.compile(
    r"(^|_)(date|datetime|timestamp|time|year|yr|month|quarter|week|day|period|"
    r"created|updated|modified|hire|order|ship|birth|dob)(_|$)"
)

# Measure-name boosts: business-relevant numeric quantities float to the top
# as the "primary" measure for trends, segments, and the headline chart.
_MEASURE_WEIGHTS: dict[str, float] = {
    "sales": 3.0,
    "revenue": 3.0,
    "profit": 3.0,
    "income": 2.5,
    "margin": 2.5,
    "amount": 2.5,
    "price": 2.2,
    "cost": 2.2,
    "value": 2.0,
    "total": 2.0,
    "spend": 2.2,
    "budget": 1.8,
    "balance": 2.0,
    "salary": 2.2,
    "wage": 2.0,
    "score": 1.8,
    "rating": 1.8,
    "rate": 1.5,
    "ratio": 1.4,
    "pct": 1.4,
    "percent": 1.4,
    "quantity": 1.6,
    "qty": 1.6,
    "count": 1.2,
    "volume": 1.6,
    "discount": 1.5,
    "age": 1.4,
    "weight": 1.3,
    "height": 1.2,
    "duration": 1.4,
    "gdp": 2.5,
    "population": 2.0,
    "temperature": 1.5,
    "tax": 1.6,
    "fee": 1.6,
}

# Dimension-name boosts: classic slice-by columns.
_DIMENSION_WEIGHTS: dict[str, float] = {
    "segment": 2.5,
    "category": 2.5,
    "subcategory": 2.0,
    "sub_category": 2.0,
    "type": 2.0,
    "group": 2.0,
    "class": 1.8,
    "status": 2.0,
    "tier": 1.8,
    "region": 2.2,
    "channel": 2.2,
    "department": 2.0,
    "dept": 2.0,
    "team": 1.8,
    "gender": 2.0,
    "sex": 2.0,
    "grade": 1.6,
    "level": 1.6,
    "mode": 1.8,
    "method": 1.6,
    "brand": 1.8,
    "industry": 1.8,
    "sector": 1.8,
    "plan": 1.8,
    "priority": 1.6,
    "label": 1.4,
    "stage": 1.6,
    "role": 1.6,
    "source": 1.6,
}

# Domain fingerprints — count keyword hits across all column names.
_DOMAIN_KEYWORDS: dict[str, set[str]] = {
    "sales / e-commerce": {
        "sales",
        "profit",
        "order",
        "customer",
        "product",
        "discount",
        "quantity",
        "revenue",
        "cart",
        "sku",
        "ship",
        "category",
    },
    "finance": {
        "balance",
        "credit",
        "debit",
        "transaction",
        "amount",
        "interest",
        "loan",
        "payment",
        "account",
        "asset",
        "liability",
        "tax",
        "invoice",
    },
    "human resources": {
        "employee",
        "salary",
        "department",
        "hire",
        "tenure",
        "attrition",
        "manager",
        "wage",
        "job",
        "title",
        "performance",
    },
    "marketing": {
        "campaign",
        "click",
        "impression",
        "conversion",
        "ctr",
        "channel",
        "lead",
        "engagement",
        "audience",
        "reach",
        "spend",
    },
    "healthcare": {
        "patient",
        "diagnosis",
        "treatment",
        "bmi",
        "blood",
        "dose",
        "disease",
        "hospital",
        "symptom",
        "mortality",
        "admission",
    },
    "real estate": {
        "price",
        "bedroom",
        "bathroom",
        "sqft",
        "property",
        "rent",
        "house",
        "listing",
        "lot",
        "garage",
        "neighborhood",
    },
    "education": {
        "student",
        "grade",
        "score",
        "exam",
        "course",
        "school",
        "gpa",
        "subject",
        "teacher",
        "attendance",
    },
}

_BOOL_TOKENS = {
    "true",
    "false",
    "yes",
    "no",
    "y",
    "n",
    "t",
    "f",
    "0",
    "1",
    "male",
    "female",
    "m",
    "on",
    "off",
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _norm(name: str) -> str:
    """Normalize a column name to snake_case-ish lowercase for matching."""
    s = re.sub(r"[^0-9a-zA-Z]+", "_", str(name)).strip("_").lower()
    return s


def _name_weight(name_norm: str, table: dict[str, float]) -> float:
    parts = set(name_norm.split("_"))
    weight = 0.0
    for kw, w in table.items():
        if kw in parts or kw in name_norm:
            weight = max(weight, w)
    return weight


def _looks_boolean(col_profile: dict, n_unique: int) -> bool:
    if n_unique > 2:
        return False
    tokens = {
        str(tv.get("value", "")).strip().lower()
        for tv in (col_profile.get("top_values") or [])
    }
    return bool(tokens) and tokens.issubset(_BOOL_TOKENS)


def _is_id_like_numeric(series: pd.Series, n_unique: int, n: int) -> bool:
    """True if a numeric column behaves like a key (monotonic index or ~unique
    integer code) rather than a quantity."""
    if n == 0:
        return False
    uniq_ratio = n_unique / n
    try:
        non_null = series.dropna()
        if is_integer_dtype(series) or (non_null % 1 == 0).all():
            # A near-unique integer column is almost always a key.
            if uniq_ratio >= 0.95:
                return True
            # A perfectly monotonic integer is a row index / sequence.
            if non_null.is_monotonic_increasing and uniq_ratio >= 0.6:
                return True
    except Exception:  # noqa: BLE001 - heuristic, never fatal
        return uniq_ratio >= 0.98
    return False


# ---------------------------------------------------------------------------
# Per-column classification
# ---------------------------------------------------------------------------


def _classify_column(series: pd.Series, col_profile: dict, n: int) -> dict[str, Any]:
    name = str(col_profile.get("name", series.name))
    name_norm = _norm(name)
    kind = col_profile.get("kind", "unknown")
    n_unique = int(col_profile.get("n_unique", series.nunique(dropna=True)))

    # 1. Constant — no signal
    if n_unique <= 1:
        return _role(CONSTANT, 1.0, "single repeated value", name_norm)

    # 2. Datetime dtype — always temporal
    if is_datetime64_any_dtype(series) or kind == "datetime":
        return _role(TEMPORAL, 1.0, "datetime values", name_norm)

    # 3. Boolean
    if (
        is_bool_dtype(series)
        or kind == "boolean"
        or _looks_boolean(col_profile, n_unique)
    ):
        return _role(BOOLEAN, 0.95, "two-state flag", name_norm)

    name_is_id = bool(_ID_RE.search(name_norm))
    name_is_geo = bool(_GEO_RE.search(name_norm))
    # A strong measure name (price, salary, amount, sales…) overrides the
    # uniqueness test: a high-cardinality continuous quantity is not a key,
    # even when its values happen to be near-unique whole numbers.
    strong_measure = _name_weight(name_norm, _MEASURE_WEIGHTS) >= 2.0

    # 4. Unique object / numeric key — row_id, fully-unique columns
    if kind == "id":
        return _role(IDENTIFIER, 0.97, "every value is unique", name_norm)
    if (
        is_numeric_dtype(series)
        and not strong_measure
        and _is_id_like_numeric(series, n_unique, n)
    ):
        return _role(IDENTIFIER, 0.9, "monotonic / unique integer key", name_norm)

    # 5. Geo wins over id-name (postal_code matches both "code" and "postal")
    if name_is_geo:
        return _role(GEO, 0.85, "geographic column", name_norm)

    # 6. Foreign-key identifiers — id-like NAME decides intent (customer_id,
    #    product_id, order_id) even when values repeat. Low-cardinality
    #    id-named columns (a coded category) fall through to dimension.
    if name_is_id and n_unique > 30:
        return _role(IDENTIFIER, 0.85, "id-like name, high cardinality", name_norm)

    # 7. Numeric quantity → measure
    if is_numeric_dtype(series):
        return _role(MEASURE, 0.9, "numeric quantity", name_norm)

    # 8. Object/categorical → dimension if chartable (≤50 levels), else text
    if 2 <= n_unique <= 50:
        return _role(DIMENSION, 0.85, f"{n_unique} distinct categories", name_norm)

    return _role(TEXT, 0.8, "free / high-cardinality text", name_norm)


def _role(role: str, confidence: float, reason: str, name_norm: str) -> dict[str, Any]:
    return {
        "role": role,
        "confidence": round(confidence, 2),
        "reason": reason,
        "_name_norm": name_norm,
    }


# ---------------------------------------------------------------------------
# Ranking
# ---------------------------------------------------------------------------


def _rank_measures(
    measure_names: list[str], col_by_name: dict[str, dict], roles: dict[str, dict]
) -> list[str]:
    scored: list[tuple[float, str]] = []
    for nm in measure_names:
        cp = col_by_name.get(nm, {})
        name_w = _name_weight(roles[nm]["_name_norm"], _MEASURE_WEIGHTS)
        mean = cp.get("mean")
        std = cp.get("std")
        cv = 0.0
        if isinstance(mean, (int, float)) and isinstance(std, (int, float)):
            cv = min(abs(std) / (abs(mean) + 1e-9), 3.0)
        score = name_w * 10.0 + cv
        scored.append((score, nm))
    scored.sort(key=lambda x: x[0], reverse=True)
    return [nm for _, nm in scored]


def _rank_dimensions(
    dimension_names: list[str], col_by_name: dict[str, dict], roles: dict[str, dict]
) -> list[str]:
    scored: list[tuple[float, str]] = []
    for nm in dimension_names:
        cp = col_by_name.get(nm, {})
        k = int(cp.get("n_unique", 0))
        # Ideal segmentation cardinality is ~2..12; decay outside that.
        if 2 <= k <= 12:
            card_score = 3.0
        elif 13 <= k <= 30:
            card_score = 2.0
        elif 31 <= k <= 50:
            card_score = 1.0
        else:
            card_score = 0.3
        name_w = _name_weight(roles[nm]["_name_norm"], _DIMENSION_WEIGHTS)
        scored.append((name_w * 5.0 + card_score, nm))
    scored.sort(key=lambda x: x[0], reverse=True)
    return [nm for _, nm in scored]


def _segmentable(
    primary_dimensions: list[str],
    geo_cols: list[str],
    col_by_name: dict[str, dict],
) -> list[str]:
    """Columns suitable for slicing a measure by. Ranked dimensions first, then
    low-cardinality geo (e.g. ``region`` with 4 values is a great slice even
    though its true role is geographic)."""
    out = list(primary_dimensions)
    geo_low = sorted(
        (
            g
            for g in geo_cols
            if 2 <= int(col_by_name.get(g, {}).get("n_unique", 99)) <= 24
        ),
        key=lambda g: int(col_by_name.get(g, {}).get("n_unique", 99)),
    )
    for g in geo_low:
        if g not in out:
            out.append(g)
    return out[:6]


# ---------------------------------------------------------------------------
# Archetype + domain
# ---------------------------------------------------------------------------


def _archetype(by_role: dict[str, list[str]]) -> dict[str, str]:
    has_t = bool(by_role[TEMPORAL])
    has_m = bool(by_role[MEASURE])
    has_d = bool(by_role[DIMENSION])
    has_g = bool(by_role[GEO])
    n_m = len(by_role[MEASURE])
    n_text = len(by_role[TEXT])

    if has_t and has_m:
        return {
            "archetype": "timeseries",
            "archetype_label": "Time-series / transactional",
            "archetype_blurb": "Records evolve over time — AURA leads with trends and period-over-period movement.",
        }
    if has_g and has_m:
        return {
            "archetype": "geospatial",
            "archetype_label": "Geospatial",
            "archetype_blurb": "Measures vary by place — AURA leads with regional breakdowns.",
        }
    if has_m and has_d:
        return {
            "archetype": "cross-sectional",
            "archetype_label": "Cross-sectional / segmented",
            "archetype_blurb": "Measures differ across categories — AURA leads with segment comparisons.",
        }
    if n_m >= 2:
        return {
            "archetype": "statistical",
            "archetype_label": "Statistical / numeric",
            "archetype_blurb": "Mostly numeric — AURA leads with distributions and correlations.",
        }
    if n_text >= 1 and not has_m:
        return {
            "archetype": "text",
            "archetype_label": "Text / categorical",
            "archetype_blurb": "Mostly text and categories — AURA leads with frequency and composition.",
        }
    return {
        "archetype": "mixed",
        "archetype_label": "Mixed",
        "archetype_blurb": "A mix of column types — AURA balances composition, distribution, and quality.",
    }


def _domain(name_norms: list[str]) -> dict[str, Any]:
    tokens: set[str] = set()
    for nm in name_norms:
        tokens.update(nm.split("_"))
    best, best_hits = None, 0
    for domain, kws in _DOMAIN_KEYWORDS.items():
        hits = len(tokens & kws)
        if hits > best_hits:
            best, best_hits = domain, hits
    if best is None or best_hits < 2:
        return {"domain": None, "domain_confidence": 0.0}
    return {"domain": best, "domain_confidence": round(min(best_hits / 5.0, 1.0), 2)}


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------


def infer_semantics(df: pd.DataFrame, profile: dict) -> dict[str, Any]:
    """Classify every column into a semantic role and derive primaries,
    archetype, and domain. Consumes the profile from ``profile_dataframe`` so
    it never recomputes per-column stats.
    """
    col_profiles: list[dict] = profile.get("columns", [])
    col_by_name = {str(c.get("name")): c for c in col_profiles}
    n = int(profile.get("n_rows", len(df)))

    roles: dict[str, dict] = {}
    for cp in col_profiles:
        nm = str(cp.get("name"))
        try:
            series = df[nm] if nm in df.columns else df.iloc[:, 0]
            roles[nm] = _classify_column(series, cp, n)
        except Exception as exc:  # noqa: BLE001 - never fatal
            logger.warning("Role inference failed for %s: %s", nm, exc)
            roles[nm] = _role(TEXT, 0.3, "fallback (inference error)", _norm(nm))

    by_role: dict[str, list[str]] = {
        IDENTIFIER: [],
        MEASURE: [],
        DIMENSION: [],
        TEMPORAL: [],
        GEO: [],
        BOOLEAN: [],
        TEXT: [],
        CONSTANT: [],
    }
    for nm, info in roles.items():
        by_role.setdefault(info["role"], []).append(nm)

    primary_measures = _rank_measures(by_role[MEASURE], col_by_name, roles)
    primary_dimensions = _rank_dimensions(by_role[DIMENSION], col_by_name, roles)
    segmentable_cols = _segmentable(primary_dimensions, by_role[GEO], col_by_name)
    temporal_cols = by_role[TEMPORAL]

    arch = _archetype(by_role)
    dom = _domain([info["_name_norm"] for info in roles.values()])

    # Strip the private name-norm helper before returning.
    public_roles = {
        nm: {k: v for k, v in info.items() if k != "_name_norm"}
        for nm, info in roles.items()
    }

    result: dict[str, Any] = {
        "roles": public_roles,
        "by_role": by_role,
        "primary_measures": primary_measures[:5],
        "primary_dimensions": primary_dimensions[:5],
        "segmentable_cols": segmentable_cols,
        "primary_temporal": temporal_cols[0] if temporal_cols else None,
        "measure_cols": by_role[MEASURE],
        "dimension_cols": by_role[DIMENSION],
        "temporal_cols": temporal_cols,
        "geo_cols": by_role[GEO],
        "id_cols": by_role[IDENTIFIER],
        "text_cols": by_role[TEXT],
        "boolean_cols": by_role[BOOLEAN],
        "counts": {role: len(cols) for role, cols in by_role.items()},
    }
    result.update(arch)
    result.update(dom)
    return result
