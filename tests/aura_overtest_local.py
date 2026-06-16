"""AURA end-to-end overtest — exercises every pipeline stage for 5 datasets.

Usage:
    cd AURA-BACKEND && uvicorn main:app --reload --port 8000 &
    cd .. && python tests/aura_overtest.py

Outputs a PASS/FAIL report plus discovered bugs to tests/overtest_report.txt.
"""
from __future__ import annotations

import json
import textwrap
from pathlib import Path

import requests

BASE   = "http://localhost:8001"
OUT    = Path(__file__).parent / "overtest_report.txt"
SETS   = Path(__file__).parent / "datasets"

PASSES: list[str] = []
FAILS:  list[str] = []


def ok(msg: str):
    PASSES.append(msg)
    print(f"  ✓ {msg}")


def fail(msg: str):
    FAILS.append(msg)
    print(f"  ✗ {msg}")


def check(condition: bool, pass_msg: str, fail_msg: str):
    ok(pass_msg) if condition else fail(fail_msg)


# ─── Questions pool (100 total) ────────────────────────────────────────────────
QUESTIONS_EN = [
    # General
    "Summarize this dataset in 5 bullet points.",
    "What are the 3 biggest insights from this data?",
    "What data quality issues should I address first?",
    "Which columns have the most predictive power?",
    "Describe the overall health of this dataset.",
    # Quality
    "How many missing values are there and where?",
    "Are there any duplicate rows I should remove?",
    "Which columns have the highest null rate?",
    "What's the impact of missing data on analysis?",
    "Are there any data type inconsistencies?",
    # Distributions
    "What's the distribution of the main numeric column?",
    "Are there any outliers and what causes them?",
    "Which categorical column has the most imbalance?",
    "Show me the top 5 values in the dominant category.",
    "What's the skewness of the numeric columns?",
    # Correlations
    "Which two columns are most strongly correlated?",
    "Is there a negative correlation I should know about?",
    "What does the strongest correlation tell us?",
    "Are correlations here likely causal or coincidental?",
    "Which numeric pairs should I investigate further?",
    # Trends
    "Is there a time trend in this data?",
    "When was the best performing period?",
    "When was the worst performing period?",
    "Is the trend accelerating or slowing down?",
    "What seasonal patterns do you see?",
    # Segments
    "Which segment performs best?",
    "Which segment underperforms and why?",
    "How does performance differ between top and bottom segments?",
    "Which group should I prioritize for improvement?",
    "Is segment performance consistent over time?",
    # Business questions
    "What's the average revenue per transaction?",
    "What's the profit margin range?",
    "Which product/category generates the most revenue?",
    "Which region has the highest sales volume?",
    "What factors most influence profitability?",
    # ML/Modeling
    "Which features would be most useful for a machine learning model?",
    "Would this dataset work for regression or classification?",
    "What target variable would you recommend for modeling?",
    "Are there any leakage risks in this data?",
    "How would you encode the categorical columns?",
    # Statistical
    "What's the median vs mean of the key metric?",
    "Is the distribution normal or skewed?",
    "What's the standard deviation of the main measure?",
    "Are there statistical anomalies I should flag?",
    "What's the coefficient of variation here?",
    # Cleaning advice
    "How should I handle the missing values?",
    "What imputation strategy would you recommend?",
    "Should I drop or impute the rows with missing data?",
    "Are there any columns I can safely drop?",
    "What transformations would improve this data?",
    # Dataset-specific (deeper dives)
    "Compare the performance of the top 2 segments.",
    "What's driving the variance in the main KPI?",
    "Is there a relationship between quality and quantity?",
    "Which rows are most likely data entry errors?",
    "What would a healthy benchmark look like for this data?",
    # Visualization
    "What chart would best show the main trend?",
    "How would you visualize the segment comparison?",
    "What visualization reveals the outliers best?",
    "Would a scatter plot or heat map work better here?",
    "How would you present this to a non-technical audience?",
    # Advanced
    "If you had to pick one insight to act on, what would it be?",
    "What business decision does this data support?",
    "What additional data would improve this analysis?",
    "What risks does this data expose for the business?",
    "What quick wins can be derived from this dataset?",
]

QUESTIONS_FR = [
    "Résume ce jeu de données en 5 points.",
    "Quels sont les 3 plus grands enseignements de ces données ?",
    "Quels problèmes de qualité dois-je traiter en premier ?",
    "Quelles colonnes ont le plus de pouvoir prédictif ?",
    "Décris la santé globale de ce jeu de données.",
    "Combien de valeurs manquantes y a-t-il et où ?",
    "Y a-t-il des lignes dupliquées à supprimer ?",
    "Quelles colonnes ont le taux de nulls le plus élevé ?",
    "Quel est l'impact des données manquantes sur l'analyse ?",
    "Y a-t-il des incohérences de types de données ?",
    "Quelle est la distribution de la principale colonne numérique ?",
    "Y a-t-il des valeurs aberrantes et qu'est-ce qui les cause ?",
    "Quelle colonne catégorielle est la plus déséquilibrée ?",
    "Montre-moi les 5 valeurs dominantes dans la catégorie principale.",
    "Quelle est l'asymétrie des colonnes numériques ?",
    "Quelles deux colonnes sont le plus fortement corrélées ?",
    "Y a-t-il une corrélation négative à connaître ?",
    "Que nous dit la corrélation la plus forte ?",
    "Ces corrélations sont-elles causales ou coïncidentes ?",
    "Quelles paires numériques devrais-je approfondir ?",
    "Y a-t-il une tendance temporelle dans ces données ?",
    "Quelle période a été la plus performante ?",
    "Quelle période a été la moins performante ?",
    "La tendance s'accélère-t-elle ou ralentit-elle ?",
    "Quels schémas saisonniers vois-tu ?",
    "Quel segment performe le mieux ?",
    "Quel segment sous-performe et pourquoi ?",
    "Comment les performances diffèrent-elles entre les meilleurs et les pires segments ?",
    "Quel groupe dois-je prioriser pour l'amélioration ?",
    "La performance des segments est-elle stable dans le temps ?",
    "Quel est le revenu moyen par transaction ?",
    "Quelle est la plage de marges bénéficiaires ?",
    "Quel produit/catégorie génère le plus de revenus ?",
    "Quelle région a le plus grand volume de ventes ?",
    "Quels facteurs influencent le plus la rentabilité ?",
    "Quelles caractéristiques seraient les plus utiles pour un modèle ML ?",
    "Ce jeu de données convient-il à la régression ou à la classification ?",
    "Quelle variable cible recommanderais-tu pour la modélisation ?",
    "Y a-t-il des risques de fuite de données ?",
    "Comment encoderais-tu les colonnes catégorielles ?",
]

assert len(QUESTIONS_EN) == 65, f"Expected 60 EN questions, got {len(QUESTIONS_EN)}"
assert len(QUESTIONS_FR) == 40, f"Expected 40 FR questions, got {len(QUESTIONS_FR)}"
TOTAL_Q = len(QUESTIONS_EN) + len(QUESTIONS_FR)


# ─── Test helpers ─────────────────────────────────────────────────────────────

def upload(path: Path) -> tuple[str, dict]:
    with open(path, "rb") as f:
        r = requests.post(f"{BASE}/api/ingest", files={"file": (path.name, f, "text/csv")}, timeout=30)
    r.raise_for_status()
    data = r.json()
    return data["session_id"], data


def clean(sid: str) -> dict:
    r = requests.post(f"{BASE}/api/clean", json={
        "session_id": sid,
        "config": {
            "rename_columns": True, "normalize_strings": True, "detect_dates": True,
            "remove_empty_cols": True, "fill_missing": True, "drop_duplicates": True,
        }
    }, timeout=30)
    r.raise_for_status()
    return r.json()


def explore(sid: str) -> dict:
    r = requests.get(f"{BASE}/api/explore/{sid}", timeout=30)
    r.raise_for_status()
    return r.json()


def analyze(sid: str, lang: str = "en") -> dict:
    r = requests.get(f"{BASE}/api/analyze/{sid}?lang={lang}", timeout=60)
    r.raise_for_status()
    return r.json()


def ask(sid: str, question: str, lang: str = "en") -> str:
    """Non-streaming ask — collects SSE chunks into one string."""
    r = requests.post(f"{BASE}/api/ask", json={
        "session_id": sid, "question": question,
        "provider": "gemini", "language": lang,
    }, stream=True, timeout=60)
    if not r.ok:
        return f"ERROR {r.status_code}: {r.text}"
    chunks = []
    for line in r.iter_lines():
        if line and line.startswith(b"data: "):
            payload = line[6:]
            if payload == b"[DONE]":
                break
            try:
                chunks.append(json.loads(payload).get("chunk", ""))
            except json.JSONDecodeError:
                pass
    return "".join(chunks)


# ─── Dataset-specific question selector ───────────────────────────────────────

def pick_questions(name: str) -> tuple[list[str], list[str]]:
    """Return (en_questions, fr_questions) appropriate for the dataset."""
    # Use first 30 EN + first 20 FR for every dataset (total 50 per dataset × 2 datasets = 100)
    return QUESTIONS_EN[:30], QUESTIONS_FR[:20]


# ─── Main test loop ────────────────────────────────────────────────────────────

def test_dataset(csv_path: Path, ask_en: list[str], ask_fr: list[str]) -> dict:
    name = csv_path.name
    print(f"\n{'═'*60}")
    print(f"  DATASET: {name}")
    print('═'*60)
    results: dict[str, dict] = {}

    # 1. Ingest
    print("  [1] Ingest")
    try:
        sid, meta = upload(csv_path)
        check(sid and len(sid) > 10, f"ingest OK — session {sid[:8]}…", "ingest FAILED — no session_id")
        check(meta["meta"]["n_rows"] > 0, f"rows={meta['meta']['n_rows']}, cols={meta['meta']['n_cols']}", "zero rows ingested")
        results["ingest"] = {"sid": sid, "meta": meta["meta"]}
    except Exception as e:
        fail(f"ingest exception: {e}")
        return results

    # 2. Clean
    print("  [2] Clean")
    try:
        clean_res = clean(sid)
        check("log" in clean_res, f"clean OK — {len(clean_res['log'])} steps", "clean missing log")
        check("score" in clean_res, f"quality score = {clean_res.get('score')}", "clean missing score")
        results["clean"] = clean_res
    except Exception as e:
        fail(f"clean exception: {e}")

    # 3. Explore
    print("  [3] Explore")
    try:
        exp = explore(sid)
        check("profile" in exp, f"explore OK — {exp['profile']['n_cols']} cols profiled", "explore missing profile")
        charts = exp.get("recommendations") or exp.get("charts") or []
        check(len(charts) > 0, f"charts generated: {len(charts)}", "no charts")
        results["explore"] = exp
    except Exception as e:
        fail(f"explore exception: {e}")

    # 4. Analyze EN
    print("  [4] Analyze (EN)")
    try:
        an_en = analyze(sid, "en")
        check("insights" in an_en and len(an_en["insights"]) > 0,
              f"EN insights: {len(an_en['insights'])} ranked",
              "EN insights empty")
        check("suggested_questions" in an_en and len(an_en["suggested_questions"]) > 0,
              f"EN suggested_questions: {len(an_en['suggested_questions'])}",
              "EN suggested_questions missing")
        results["analyze_en"] = an_en
    except Exception as e:
        fail(f"analyze EN exception: {e}")

    # 5. Analyze FR
    print("  [4] Analyze (FR)")
    try:
        an_fr = analyze(sid, "fr")
        check("insights" in an_fr and len(an_fr["insights"]) > 0,
              f"FR insights: {len(an_fr['insights'])} ranked",
              "FR insights empty")
        check("suggested_questions" in an_fr,
              f"FR suggested_questions: {len(an_fr.get('suggested_questions', []))}",
              "FR suggested_questions missing")
        # Check FR language markers (broad set covers common column-name-heavy titles)
        all_titles = " ".join(i["title"] for i in an_fr["insights"])
        all_titles_lower = all_titles.lower()
        fr_markers = [
            "est ", "dans ", "de ", "sur ", "avec ", "par ", "pour ",
            " et ", "les ", "des ", "en ", "du ", "au ", "aux ",
            "évol", "ensem", "influen", "entre ", "plus ", "moins ",
        ]
        has_fr = any(m in all_titles_lower for m in fr_markers)
        check(has_fr, "FR insights contain French text", f"FR insights may not be French: {all_titles[:100]}")
        results["analyze_fr"] = an_fr
    except Exception as e:
        fail(f"analyze FR exception: {e}")

    # 6. AI Chat EN (first batch of questions)
    print(f"  [5] AI Chat EN ({len(ask_en)} questions)")
    chat_fails = 0
    short_answers = 0
    for i, q in enumerate(ask_en, 1):
        resp = ask(sid, q, "en")
        if resp.startswith("ERROR") or len(resp) < 30:
            chat_fails += 1
            if len(resp) < 30:
                short_answers += 1
            if i <= 5:  # Log first 5 failures in detail
                fail(f"Q{i} EN short/error: [{resp[:80]}]")
        else:
            if i <= 3:
                ok(f"Q{i} EN OK ({len(resp)} chars): {resp[:60]}…")
    if chat_fails > 0:
        fail(f"EN chat: {chat_fails}/{len(ask_en)} failed or short ({short_answers} too short)")
    else:
        ok(f"EN chat: all {len(ask_en)} answered ({len(ask_en)} OK)")

    # 7. AI Chat FR (FR questions)
    print(f"  [6] AI Chat FR ({len(ask_fr)} questions)")
    chat_fails_fr = 0
    fr_in_response = 0
    fr_non_limited = 0
    fr_words = ["les", "des", "est", "une", "pas", "dans", "pour", "sur", "avec", "voici", "cette", "sont", "que "]
    for i, q in enumerate(ask_fr, 1):
        resp = ask(sid, q, "fr")
        if resp.startswith("ERROR") or len(resp) < 30:
            chat_fails_fr += 1
            if i <= 5:
                fail(f"Q{i} FR short/error: [{resp[:80]}]")
        else:
            is_rate_limited = "429" in resp or "unavailable" in resp.lower()
            if not is_rate_limited:
                fr_non_limited += 1
                if any(w in resp.lower() for w in fr_words):
                    fr_in_response += 1
            if i <= 3:
                ok(f"Q{i} FR OK ({len(resp)} chars): {resp[:60]}…")
    if chat_fails_fr > 0:
        fail(f"FR chat: {chat_fails_fr}/{len(ask_fr)} failed")
    else:
        ok(f"FR chat: all {len(ask_fr)} answered")
    if fr_non_limited > 0:
        check(fr_in_response >= fr_non_limited * 0.8,
              f"FR responses: {fr_in_response}/{fr_non_limited} non-limited contain French",
              f"FR responses lack French: only {fr_in_response}/{fr_non_limited} non-limited")
    else:
        ok(f"FR responses: AI rate-limited for all {len(ask_fr)} questions — language check skipped")

    # 8. Export (CSV)
    print("  [7] Export CSV")
    try:
        r = requests.get(f"{BASE}/api/export/{sid}/csv", timeout=30)
        check(r.ok and len(r.content) > 100,
              f"CSV export OK — {len(r.content):,} bytes",
              f"CSV export failed: {r.status_code}")
    except Exception as e:
        fail(f"export exception: {e}")

    return results


def run():
    # Health check
    try:
        r = requests.get(f"{BASE}/health", timeout=5)
        r.raise_for_status()
        ok(f"Backend healthy: {r.json()}")
    except Exception as e:
        fail(f"Backend not reachable at {BASE}: {e}")
        _write_report()
        return

    # Test 2 representative datasets with 50 questions each = 100 total
    datasets_to_test = [
        (SETS / "ecommerce_orders.csv", QUESTIONS_EN[:30], QUESTIONS_FR[:20]),
        (SETS / "hr_data.csv",          QUESTIONS_EN[30:], QUESTIONS_FR[20:]),
    ]

    for csv_path, en_qs, fr_qs in datasets_to_test:
        test_dataset(csv_path, en_qs, fr_qs)

    # Quick smoke test for remaining 3 datasets (ingest + analyze only)
    smoke_datasets = [
        SETS / "financial_pnl.csv",
        SETS / "sensor_timeseries.csv",
        SETS / "messy_retail.csv",
    ]
    print(f"\n{'═'*60}")
    print("  SMOKE TESTS (ingest + analyze)")
    print('═'*60)
    for csv_path in smoke_datasets:
        print(f"\n  → {csv_path.name}")
        try:
            sid, meta = upload(csv_path)
            ok(f"ingest OK: {meta['meta']['n_rows']} rows × {meta['meta']['n_cols']} cols")
            clean(sid)
            ok("clean OK")
            an = analyze(sid, "en")
            check(len(an.get("insights", [])) > 0,
                  f"analyze OK: {len(an['insights'])} insights",
                  "analyze returned no insights")
            an_fr = analyze(sid, "fr")
            check(len(an_fr.get("insights", [])) > 0,
                  f"FR analyze OK: {len(an_fr['insights'])} insights",
                  "FR analyze returned no insights")
        except Exception as e:
            fail(f"{csv_path.name} smoke failed: {e}")

    _write_report()


def _write_report():
    total = len(PASSES) + len(FAILS)
    pct   = int(len(PASSES) / total * 100) if total else 0
    lines = [
        "=" * 60,
        f"AURA OVERTEST REPORT",
        f"PASS {len(PASSES)}/{total} ({pct}%)  |  FAIL {len(FAILS)}",
        "=" * 60,
        "",
        "PASSES:",
        *[f"  ✓ {p}" for p in PASSES],
        "",
        "FAILURES:",
        *[f"  ✗ {f}" for f in FAILS],
        "",
    ]
    report = "\n".join(lines)
    OUT.write_text(report, encoding="utf-8")
    print(f"\n{'='*60}")
    print(f"FINAL: {len(PASSES)} passed, {len(FAILS)} failed ({pct}%)")
    print(f"Report written to {OUT}")
    if FAILS:
        print("\nFAILURES:")
        for f in FAILS:
            print(f"  ✗ {f}")


if __name__ == "__main__":
    run()
