"""Generate diverse synthetic datasets for AURA end-to-end QA."""
import random
from pathlib import Path

import numpy as np
import pandas as pd

SEED = 42
rng = np.random.default_rng(SEED)
random.seed(SEED)

OUT = Path(__file__).parent / "datasets"
OUT.mkdir(exist_ok=True)


# ─── 1. E-commerce orders (strong correlations, trend, segments) ───────────────
def make_ecommerce():
    n = 2000
    dates = pd.date_range("2022-01-01", periods=n, freq="12h")
    category = rng.choice(["Electronics", "Clothing", "Home", "Beauty", "Sports"], n, p=[0.3, 0.25, 0.2, 0.15, 0.1])
    region   = rng.choice(["North", "South", "East", "West"], n)
    quantity = rng.integers(1, 10, n)
    price    = np.where(category == "Electronics", rng.uniform(200, 2000, n),
               np.where(category == "Clothing",    rng.uniform(20,  200, n),
               np.where(category == "Home",        rng.uniform(30,  500, n),
               np.where(category == "Beauty",      rng.uniform(10,  150, n),
                                                   rng.uniform(15,  300, n)))))
    discount = rng.uniform(0, 0.4, n)
    revenue  = price * quantity * (1 - discount)
    # Inject trend: revenue grows ~30% over 2 years
    trend    = np.linspace(1.0, 1.3, n)
    revenue  *= trend
    profit   = revenue * rng.uniform(0.05, 0.35, n)
    # Missing values in 8% of rows
    mask_price    = rng.random(n) < 0.05
    mask_discount = rng.random(n) < 0.08
    price[mask_price] = np.nan
    discount[mask_discount] = np.nan
    df = pd.DataFrame({
        "order_id": [f"ORD-{i:05d}" for i in range(n)],
        "order_date": dates,
        "category": category,
        "region": region,
        "quantity": quantity,
        "unit_price": price.round(2),
        "discount_pct": discount.round(3),
        "revenue": revenue.round(2),
        "profit": profit.round(2),
    })
    # Add 50 duplicates
    dupes = df.sample(50, random_state=0)
    df = pd.concat([df, dupes], ignore_index=True)
    df.to_csv(OUT / "ecommerce_orders.csv", index=False)
    print(f"ecommerce_orders.csv — {len(df)} rows")


# ─── 2. HR dataset (salary analysis, performance, department segments) ──────────
def make_hr():
    n = 800
    dept = rng.choice(["Engineering", "Sales", "Marketing", "HR", "Finance", "Operations"], n,
                      p=[0.30, 0.20, 0.15, 0.10, 0.15, 0.10])
    level = rng.choice(["Junior", "Mid", "Senior", "Lead", "Manager"], n, p=[0.25, 0.30, 0.25, 0.12, 0.08])
    base_salary = {
        "Junior": 45000, "Mid": 65000, "Senior": 90000, "Lead": 115000, "Manager": 140000,
    }
    dept_mult = {
        "Engineering": 1.3, "Finance": 1.1, "Sales": 1.05, "Marketing": 1.0, "HR": 0.95, "Operations": 0.90,
    }
    salary = np.array([
        base_salary[level[i]] * dept_mult[dept[i]] * rng.uniform(0.85, 1.15)
        for i in range(n)
    ])
    perf_score  = rng.uniform(2.0, 5.0, n).round(1)
    tenure_yrs  = rng.integers(0, 15, n)
    satisfaction = np.clip(perf_score / 5 * rng.uniform(0.7, 1.3, n), 1.0, 5.0).round(1)
    attrition   = (rng.random(n) < (0.3 - satisfaction * 0.04)).astype(int)
    # Missing salary for 6% of rows
    mask = rng.random(n) < 0.06
    salary = salary.astype(float)
    salary[mask] = np.nan
    df = pd.DataFrame({
        "employee_id": [f"EMP-{i:04d}" for i in range(n)],
        "department": dept,
        "level": level,
        "salary_usd": salary.round(0),
        "performance_score": perf_score,
        "tenure_years": tenure_yrs,
        "satisfaction_score": satisfaction,
        "attrition": attrition,
    })
    df.to_csv(OUT / "hr_data.csv", index=False)
    print(f"hr_data.csv — {len(df)} rows")


# ─── 3. Quarterly financial P&L (time trend, dominance in region) ────────────
def make_financial():
    rows = []
    regions = ["MENA", "Europe", "Americas", "APAC"]
    products = ["SaaS", "Support", "Professional Services", "Hardware"]
    for year in range(2020, 2025):
        for q in range(1, 5):
            for region in regions:
                for product in products:
                    base_rev = {
                        "MENA": 500_000, "Europe": 1_200_000,
                        "Americas": 1_800_000, "APAC": 900_000,
                    }[region] * {"SaaS": 1.5, "Support": 0.6, "Professional Services": 0.8, "Hardware": 0.4}[product]
                    growth = 1 + (year - 2020) * 0.08 + q * 0.01
                    revenue = base_rev * growth * rng.uniform(0.9, 1.1)
                    cogs    = revenue * rng.uniform(0.25, 0.45)
                    opex    = revenue * rng.uniform(0.20, 0.35)
                    ebitda  = revenue - cogs - opex
                    rows.append({
                        "period": f"{year}-Q{q}",
                        "year": year,
                        "quarter": q,
                        "region": region,
                        "product_line": product,
                        "revenue_usd": round(revenue, 0),
                        "cogs_usd": round(cogs, 0),
                        "opex_usd": round(opex, 0),
                        "ebitda_usd": round(ebitda, 0),
                        "margin_pct": round(ebitda / revenue * 100, 1),
                    })
    df = pd.DataFrame(rows)
    # 4% missing margin
    mask = rng.random(len(df)) < 0.04
    df.loc[mask, "margin_pct"] = np.nan
    df.to_csv(OUT / "financial_pnl.csv", index=False)
    print(f"financial_pnl.csv — {len(df)} rows")


# ─── 4. IoT sensor time-series (temporal analysis, outliers) ──────────────────
def make_sensors():
    n = 1500
    dates = pd.date_range("2024-01-01", periods=n, freq="H")
    sensors = rng.choice(["sensor_A", "sensor_B", "sensor_C"], n)
    # Temperature with daily cycle
    hours = np.arange(n) % 24
    temp  = 20 + 8 * np.sin(2 * np.pi * hours / 24) + rng.normal(0, 1.5, n)
    # Humidity inversely correlated with temp
    humidity = 80 - 1.5 * (temp - 20) + rng.normal(0, 3, n)
    # Pressure with slow drift
    pressure = 1013 + np.linspace(0, 8, n) + rng.normal(0, 2, n)
    # Power consumption correlated with temp
    power = 50 + 3 * np.maximum(0, temp - 22) + rng.normal(0, 4, n)
    # Inject outliers (2%)
    outlier_idx = rng.choice(n, size=30, replace=False)
    temp[outlier_idx] += rng.choice([-25, 25], size=30)
    # Missing 5%
    for arr in [temp, humidity, pressure]:
        mask = rng.random(n) < 0.05
        arr = arr.astype(float)
        arr[mask] = np.nan
    df = pd.DataFrame({
        "timestamp": dates,
        "sensor_id": sensors,
        "temperature_c": temp.round(2),
        "humidity_pct": np.clip(humidity, 10, 100).round(1),
        "pressure_hpa": pressure.round(1),
        "power_kw": np.maximum(0, power).round(2),
    })
    df.to_csv(OUT / "sensor_timeseries.csv", index=False)
    print(f"sensor_timeseries.csv — {len(df)} rows")


# ─── 5. Messy retail (heavy NaN, duplicates, mixed types, bad column names) ───
def make_messy():
    n = 600
    df = pd.DataFrame({
        "Customer ID":        [f"C{rng.integers(1000, 9999)}" for _ in range(n)],
        "  Product Name  ":   rng.choice(["Widget A", "widget a", "WIDGET A", "Widget B", "Widget C", None], n),
        "Sale Amount ($)":    np.where(rng.random(n) < 0.15, np.nan, rng.uniform(5, 500, n).round(2)),
        "QUANTITY":           np.where(rng.random(n) < 0.10, np.nan, rng.integers(1, 20, n)),
        "Date":               [
            rng.choice(["2024-01-15", "15/01/2024", "Jan 15 2024", "2024/01/15", None])
            for _ in range(n)
        ],
        "City":               rng.choice(["Casablanca", "Rabat", "Marrakech", "Fes", "", None], n),
        "Rating":             np.where(rng.random(n) < 0.20, np.nan, rng.integers(1, 6, n)),
        "Return?":            rng.choice(["Yes", "No", "yes", "no", "YES", "1", "0", None], n),
    })
    # Add 80 duplicate rows
    dupes = df.sample(80, random_state=42)
    df = pd.concat([df, dupes], ignore_index=True)
    df.to_csv(OUT / "messy_retail.csv", index=False)
    print(f"messy_retail.csv — {len(df)} rows")


if __name__ == "__main__":
    make_ecommerce()
    make_hr()
    make_financial()
    make_sensors()
    make_messy()
    print(f"\nAll datasets written to {OUT}/")
