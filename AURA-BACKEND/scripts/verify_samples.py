"""Run each demo dataset through AURA's real pipeline and print proof it shines.

This is the acceptance test for scripts/generate_samples.py: it exercises the
exact engines the product uses (ingestion -> cleaning -> profiling -> semantics
-> analysis) and reports the cleaning audit trail, quality score, inferred
archetype/domain, recommended charts, and ranked insights for each sample.

Run from AURA-BACKEND:  python scripts/verify_samples.py
"""

from __future__ import annotations

import sys
from pathlib import Path

# Make the script self-contained: backend root on the path, UTF-8 stdout so the
# audit trail's arrows/×/— never crash a bare Windows (cp1252) console.
sys.path.insert(0, str(Path(__file__).parent.parent))
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from engines.analysis import analyze  # noqa: E402
from engines.cleaning import CleaningOrchestrator  # noqa: E402
from engines.exploration import profile_dataframe, recommend_charts  # noqa: E402
from engines.ingestion import load_file_bytes  # noqa: E402
from engines.semantics import infer_semantics  # noqa: E402

SAMPLES = Path(__file__).parent.parent / "static" / "samples"
FILES = ["mena-saas-revenue.csv", "mena-workforce.csv", "mena-retail-raw.csv"]


def line(char: str = "-", n: int = 78) -> None:
    print(char * n)


def verify(fname: str) -> None:
    path = SAMPLES / fname
    ingest = load_file_bytes(path.read_bytes(), fname)
    raw = ingest.df
    rb, cb = raw.shape

    cleaned, report = CleaningOrchestrator().clean(raw.copy())
    ra, ca = cleaned.shape

    quality = ""
    for step in report.steps:
        if "Quality score" in step.get("detail", ""):
            quality = step["detail"]

    profile = profile_dataframe(cleaned)
    sem = infer_semantics(cleaned, profile)
    charts = recommend_charts(cleaned, profile, sem)
    result = analyze(cleaned, profile, meta_name=fname, semantics=sem, language="en")

    line("=")
    print(f"  {fname}")
    line("=")
    print(f"  raw {rb}x{cb}  ->  cleaned {ra}x{ca}")
    print(f"  archetype : {sem.get('archetype_label')}  |  domain: {sem.get('domain')}")
    print(f"  primary measures   : {sem.get('primary_measures')[:4]}")
    print(f"  segmentable cols   : {sem.get('segmentable_cols')}")
    print(f"  primary temporal   : {sem.get('primary_temporal')}")
    print(f"  {quality}")
    print()
    print("  Cleaning audit trail:")
    for s in report.steps:
        print(f"    - [{s['step']}] {s['detail']}")
    print()
    print(f"  Recommended charts ({len(charts)}):")
    for c in charts:
        print(f"    - {c['type']:14s} {c['title']}  (priority {c['priority']})")
    print()
    print(f"  Ranked insights ({len(result['insights'])}):")
    sev_label = {3: "CRIT", 2: "note", 1: "minor"}
    for ins in result["insights"]:
        print(f"    - [{sev_label.get(ins['severity'], '?')}] {ins['title']}")
    corr = result["correlations"]
    if corr:
        top = corr[0]
        print(
            f"\n  Strongest measure correlation: {top['col_a']} x {top['col_b']} r={top['r']}"
        )
    print()


if __name__ == "__main__":
    for f in FILES:
        verify(f)
