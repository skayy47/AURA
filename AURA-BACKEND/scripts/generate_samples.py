"""Generate the three AURA demo datasets that ship in static/samples/.

Each dataset is engineered to light up a *different* part of the AURA pipeline
(clean -> explore -> analyze -> branded PDF), driven by what the real engines
reward (see engines/semantics.py, exploration.py, analysis.py, cleaning.py):

  1. mena-saas-revenue  -> TIME-SERIES archetype. Rising-revenue trend (+>40%),
     strong revenue<->profit correlation, segment spread (Enterprise vs Startup),
     a handful of mega-deal outliers. Leads with a headline trend chart.

  2. mena-workforce     -> CROSS-SECTIONAL archetype (no temporal on purpose).
     bonus<->performance correlation, department/level salary spread. Leads with
     segment-comparison bars + a scatter.

  3. mena-retail-raw    -> the CLEANING showcase. Messy headers, mixed date
     formats, Yes/No/1/0 boolean chaos, heavy NaN, ~100 duplicate rows. Watch the
     quality score and audit trail do the talking; still yields a real dashboard
     after AURA fixes it.

Deterministic (SEED=42). Dimension coverage follows the tuple-coverage principle:
every categorical level is well populated so no chart group is degenerate.

Run:  python scripts/generate_samples.py
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

SEED = 42
rng = np.random.default_rng(SEED)

OUT = Path(__file__).parent.parent / "static" / "samples"
OUT.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------------------------
# 1. MENA SaaS Revenue  — time-series archetype
# ---------------------------------------------------------------------------
def make_saas_revenue() -> None:
    n = 600
    # Temporal axis: ~2.4 years so analyze() resamples monthly and reads the trend.
    order_date = pd.to_datetime("2023-01-01") + pd.to_timedelta(
        np.sort(rng.integers(0, 880, n)), unit="D"
    )
    t = np.linspace(0.0, 1.0, n)  # 0..1 along the timeline (already sorted)

    region = rng.choice(
        ["Gulf", "Levant", "North Africa", "Nile Valley"], n, p=[0.4, 0.25, 0.2, 0.15]
    )
    country = rng.choice(
        [
            "Saudi Arabia",
            "UAE",
            "Egypt",
            "Morocco",
            "Qatar",
            "Kuwait",
            "Jordan",
            "Bahrain",
        ],
        n,
    )
    product_line = rng.choice(
        ["Analytics Suite", "Support Plan", "Professional Services", "Hardware"],
        n,
        p=[0.4, 0.25, 0.2, 0.15],
    )
    channel = rng.choice(["Direct", "Partner", "Online", "Reseller"], n)
    segment = rng.choice(
        ["Enterprise", "Mid-Market", "SMB", "Startup"], n, p=[0.2, 0.3, 0.3, 0.2]
    )

    quantity = rng.integers(1, 40, n)
    unit_price = np.where(
        product_line == "Analytics Suite",
        rng.uniform(400, 2200, n),
        np.where(
            product_line == "Professional Services",
            rng.uniform(120, 900, n),
            np.where(
                product_line == "Hardware",
                rng.uniform(200, 1500, n),
                rng.uniform(40, 300, n),
            ),
        ),
    )
    discount = rng.uniform(0, 0.35, n)

    seg_factor = (
        pd.Series(segment)
        .map({"Enterprise": 2.6, "Mid-Market": 1.4, "SMB": 0.8, "Startup": 0.45})
        .to_numpy()
    )
    trend = 1.0 + 0.55 * t  # +55% growth across the window -> severity-3 trend insight
    revenue = quantity * unit_price * (1 - discount) * seg_factor * trend
    revenue *= rng.uniform(0.85, 1.15, n)  # organic noise

    margin = rng.uniform(0.12, 0.34, n)
    profit = revenue * margin  # strong revenue<->profit correlation
    marketing_spend = 0.12 * revenue + rng.normal(0, revenue.std() * 0.18, n)
    marketing_spend = np.clip(marketing_spend, 50, None)

    df = pd.DataFrame(
        {
            "order_id": [f"ORD-{i:05d}" for i in range(n)],
            "order_date": order_date,
            "region": region,
            "country": country,
            "product_line": product_line,
            "channel": channel,
            "segment": segment,
            "quantity": quantity,
            "unit_price_usd": unit_price.round(2),
            "discount_pct": discount.round(3),
            "revenue_usd": revenue.round(2),
            "profit_usd": profit.round(2),
            "marketing_spend_usd": marketing_spend.round(2),
        }
    )

    # ~10 mega-deal outliers (1.6% -> flagged AND surfaced as an outlier insight)
    mega_idx = rng.choice(n, size=10, replace=False)
    df.loc[mega_idx, "revenue_usd"] *= rng.uniform(6, 9, size=10)
    df.loc[mega_idx, "profit_usd"] = df.loc[mega_idx, "revenue_usd"] * 0.25

    # Planted gaps -> missing hotspots in the cleaning report
    df.loc[df.sample(frac=0.07, random_state=1).index, "discount_pct"] = np.nan
    df.loc[df.sample(frac=0.05, random_state=2).index, "profit_usd"] = np.nan

    # 20 exact duplicate rows
    df = pd.concat([df, df.sample(20, random_state=3)], ignore_index=True)

    df.to_csv(OUT / "mena-saas-revenue.csv", index=False)
    _report("mena-saas-revenue.csv", df)


# ---------------------------------------------------------------------------
# 2. MENA Workforce  — cross-sectional archetype (deliberately no temporal col)
# ---------------------------------------------------------------------------
def make_workforce() -> None:
    n = 500
    department = rng.choice(
        ["Engineering", "Product", "Sales", "Marketing", "Finance", "Operations", "HR"],
        n,
        p=[0.26, 0.12, 0.18, 0.12, 0.12, 0.12, 0.08],
    )
    level = rng.choice(
        ["Junior", "Mid", "Senior", "Lead", "Manager"],
        n,
        p=[0.28, 0.3, 0.24, 0.1, 0.08],
    )
    office = rng.choice(["Riyadh", "Dubai", "Cairo", "Casablanca", "Doha", "Amman"], n)
    remote = rng.choice(["Yes", "No"], n, p=[0.45, 0.55])

    tenure = rng.integers(0, 14, n)
    performance = np.clip(rng.normal(3.5, 0.8, n), 1.0, 5.0)
    satisfaction = np.clip(performance * 0.7 + rng.normal(1.0, 0.6, n), 1.0, 5.0)
    training_hours = rng.integers(0, 80, n)
    projects = rng.integers(1, 25, n)

    level_base = (
        pd.Series(level)
        .map(
            {
                "Junior": 42000,
                "Mid": 63000,
                "Senior": 92000,
                "Lead": 118000,
                "Manager": 150000,
            }
        )
        .to_numpy()
    )
    dept_mult = (
        pd.Series(department)
        .map(
            {
                "Engineering": 1.35,
                "Product": 1.3,
                "Finance": 1.15,
                "Sales": 1.05,
                "Marketing": 1.0,
                "Operations": 0.92,
                "HR": 0.9,
            }
        )
        .to_numpy()
    )
    salary = (
        level_base * dept_mult
        + tenure * 1500  # salary<->tenure link
        + performance * 3000  # mild salary<->performance link
    ) * rng.uniform(0.9, 1.1, n)

    # bonus is strongly performance-driven -> clean severity-3 correlation + scatter
    bonus = 1500 + performance * 4200 + rng.normal(0, 1500, n)
    bonus = np.clip(bonus, 0, None)

    df = pd.DataFrame(
        {
            "employee_id": [f"EMP-{i:04d}" for i in range(n)],
            "department": department,
            "level": level,
            "office": office,
            "remote": remote,
            "tenure_years": tenure,
            "salary_usd": salary.round(0),
            "performance_score": performance.round(2),
            "satisfaction_score": satisfaction.round(2),
            "training_hours": training_hours,
            # Keep cents: a whole-integer near-unique column trips AURA's
            # identifier heuristic and would be dropped from correlations.
            "bonus_usd": bonus.round(2),
            "projects_completed": projects,
        }
    )

    # A few executive-pay outliers
    out_idx = rng.choice(n, size=4, replace=False)
    df.loc[out_idx, "salary_usd"] *= rng.uniform(2.5, 3.5, size=4)

    # ~6% missing salary -> missing hotspot
    df.loc[df.sample(frac=0.06, random_state=4).index, "salary_usd"] = np.nan

    # 15 duplicate rows
    df = pd.concat([df, df.sample(15, random_state=5)], ignore_index=True)

    df.to_csv(OUT / "mena-workforce.csv", index=False)
    _report("mena-workforce.csv", df)


# ---------------------------------------------------------------------------
# 3. MENA Retail (raw)  — the cleaning showcase
# ---------------------------------------------------------------------------
def make_retail_raw() -> None:
    n = 400
    cities = ["Casablanca", "Rabat", "Marrakech", "Dubai", "Cairo", "Riyadh", "", None]
    # Consistent casing: AURA dedups case-variant rows but doesn't canonicalize
    # category labels, so mixed casing here would survive as noisy bars in the
    # final report. The cleaning story is carried by headers/dupes/dates/nulls.
    payment = ["Card", "Cash", "COD", "Wallet"]
    reps = [f"Rep {i:02d}" for i in range(1, 28)]

    qty = rng.integers(1, 18, n).astype(float)
    sale_amount = (qty * rng.uniform(15, 140, n)).round(2)

    # Mixed date formats — TypePromoter must unify these to datetime
    base_dates = pd.to_datetime("2024-01-01") + pd.to_timedelta(
        rng.integers(0, 400, n), unit="D"
    )
    fmts = ["%Y-%m-%d", "%d/%m/%Y", "%b %d %Y", "%Y/%m/%d"]
    order_date_raw = [
        d.strftime(rng.choice(fmts)) if rng.random() > 0.08 else "N/A"
        for d in base_dates
    ]

    # Boolean chaos — every token is bool-ish so it promotes cleanly to bool
    delivered = rng.choice(
        ["Yes", "No", "yes", "no", "YES", "Y", "N", "1", "0", "true"], n
    )

    df = pd.DataFrame(
        {
            "  Order ID  ": [f"OID{rng.integers(1000, 9999)}" for _ in range(n)],
            "Customer Name": rng.choice(
                ["Amine B.", "Sara L.", "Youssef K.", "Lina M.", "Omar R.", None], n
            ),
            "Order Date": order_date_raw,
            "Sale Amount ($)": sale_amount,
            "QTY": qty,
            "City": rng.choice(cities, n),
            "Payment Method": rng.choice(payment, n),
            "Delivered?": delivered,
            "Discount %": rng.uniform(0, 45, n).round(1),
            "Rating": rng.integers(1, 6, n).astype(float),
            "Sales Rep": rng.choice(reps, n),
        }
    )

    # Heavy, uneven missingness
    df.loc[df.sample(frac=0.15, random_state=6).index, "Sale Amount ($)"] = np.nan
    df.loc[df.sample(frac=0.10, random_state=7).index, "QTY"] = np.nan
    df.loc[df.sample(frac=0.32, random_state=8).index, "Rating"] = (
        np.nan
    )  # >=30% -> sev-3
    df.loc[df.sample(frac=0.08, random_state=9).index, "Discount %"] = np.nan

    # A few extreme sale outliers
    out_idx = rng.choice(n, size=6, replace=False)
    df.loc[out_idx, "Sale Amount ($)"] = rng.uniform(40000, 99999, size=6).round(2)

    # ~100 duplicate rows -> ~20% duplicate rate
    df = pd.concat([df, df.sample(100, random_state=10)], ignore_index=True)
    df = df.sample(frac=1, random_state=11).reset_index(drop=True)  # shuffle

    df.to_csv(OUT / "mena-retail-raw.csv", index=False)
    _report("mena-retail-raw.csv", df)


def _report(name: str, df: pd.DataFrame) -> None:
    print(f"{name:24s} -> {df.shape[0]:>4} rows x {df.shape[1]:>2} cols")


if __name__ == "__main__":
    make_saas_revenue()
    make_workforce()
    make_retail_raw()
    print(f"\nWrote 3 demo datasets to {OUT}")
