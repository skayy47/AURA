"""Localization for the branded PDF report (EN / FR).

Single source of truth for every human-facing string, label map, and
locale-aware number/date formatter used by ``services.pdf_renderer`` and
``templates/report.html.j2``. Keep the report fully bilingual from one place:
add a key here, reference ``labels.<key>`` in the template.

Public surface:
    normalize_lang(language)        -> "en" | "fr"
    labels_for(lang)               -> dict of static template strings
    archetype_for(code, lang)      -> (label, blurb)
    domain_for(domain, lang)       -> localized domain name
    role_labels_for(lang)          -> ordered list of role display names
    fmt_int(value, lang)           -> grouped integer string
    fmt_dec(value, lang, places)   -> grouped decimal string
    fmt_date(dt, lang)             -> localized date-time string
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

# ---------------------------------------------------------------------------
# Static template strings
# ---------------------------------------------------------------------------

LABELS: dict[str, dict[str, str]] = {
    "en": {
        "report_tag": "Data Intelligence Report",
        "rows_l": "rows",
        "cols_l": "cols",
        "generated": "Generated",
        "exec_summary": "Executive Summary",
        "ai_generated": "AI-generated",
        "auto_generated": "Auto-generated",
        "overview": "Dataset Overview",
        "m_rows": "Rows",
        "m_columns": "Columns",
        "m_missing": "Missing",
        "m_memory": "In-memory",
        "m_quality": "Quality /100",
        "dna_title": "Dataset DNA — Column Roles",
        "more": "more",
        "data_quality": "Data Quality",
        "q_missing": "Missing values",
        "q_duplicates": "Duplicate rows",
        "q_worst": "Worst column",
        "q_constant": "Constant columns",
        "findings": "Key Findings",
        "sev_critical": "Critical",
        "sev_notable": "Notable",
        "sev_minor": "Minor",
        "visual": "Visual Analysis",
        "correlations": "Correlations",
        "recommendations": "Recommendations",
        "appendix": "Column Appendix",
        "t_column": "Column",
        "t_type": "Type",
        "t_missing": "Missing",
        "t_unique": "Unique",
        "t_meantop": "Mean / Top",
        "footer_brand": "AURA · Universal Data Engine",
        "pct": "%",
    },
    "fr": {
        "report_tag": "Rapport d'Intelligence des Données",
        "rows_l": "lignes",
        "cols_l": "cols",
        "generated": "Généré le",
        "exec_summary": "Résumé Exécutif",
        "ai_generated": "Généré par IA",
        "auto_generated": "Généré automatiquement",
        "overview": "Aperçu du Jeu de Données",
        "m_rows": "Lignes",
        "m_columns": "Colonnes",
        "m_missing": "Manquantes",
        "m_memory": "En mémoire",
        "m_quality": "Qualité /100",
        "dna_title": "ADN du Jeu de Données — Rôles des Colonnes",
        "more": "de plus",
        "data_quality": "Qualité des Données",
        "q_missing": "Valeurs manquantes",
        "q_duplicates": "Lignes dupliquées",
        "q_worst": "Pire colonne",
        "q_constant": "Colonnes constantes",
        "findings": "Constats Clés",
        "sev_critical": "Critique",
        "sev_notable": "Notable",
        "sev_minor": "Mineur",
        "visual": "Analyse Visuelle",
        "correlations": "Corrélations",
        "recommendations": "Recommandations",
        "appendix": "Annexe des Colonnes",
        "t_column": "Colonne",
        "t_type": "Type",
        "t_missing": "Manquantes",
        "t_unique": "Uniques",
        "t_meantop": "Moyenne / Fréquent",
        "footer_brand": "AURA · Moteur Universel de Données",
        "pct": " %",
    },
}

# Semantic archetype label + blurb, keyed by the code from engines.semantics.
ARCHETYPE: dict[str, dict[str, tuple[str, str]]] = {
    "en": {
        "timeseries": (
            "Time-series / transactional",
            "Records evolve over time — AURA leads with trends and period-over-period movement.",
        ),
        "geospatial": (
            "Geospatial",
            "Measures vary by place — AURA leads with regional breakdowns.",
        ),
        "cross-sectional": (
            "Cross-sectional / segmented",
            "Measures differ across categories — AURA leads with segment comparisons.",
        ),
        "statistical": (
            "Statistical / numeric",
            "Mostly numeric — AURA leads with distributions and correlations.",
        ),
        "text": (
            "Text / categorical",
            "Mostly text and categories — AURA leads with frequency and composition.",
        ),
        "mixed": (
            "Mixed",
            "A mix of column types — AURA balances composition, distribution, and quality.",
        ),
    },
    "fr": {
        "timeseries": (
            "Séries temporelles / transactionnel",
            "Les enregistrements évoluent dans le temps — AURA met en avant les tendances et les variations d'une période à l'autre.",
        ),
        "geospatial": (
            "Géospatial",
            "Les mesures varient selon le lieu — AURA met en avant les ventilations régionales.",
        ),
        "cross-sectional": (
            "Transversal / segmenté",
            "Les mesures diffèrent selon les catégories — AURA met en avant les comparaisons par segment.",
        ),
        "statistical": (
            "Statistique / numérique",
            "Principalement numérique — AURA met en avant les distributions et les corrélations.",
        ),
        "text": (
            "Texte / catégoriel",
            "Principalement du texte et des catégories — AURA met en avant la fréquence et la composition.",
        ),
        "mixed": (
            "Mixte",
            "Un mélange de types de colonnes — AURA équilibre composition, distribution et qualité.",
        ),
    },
}

DOMAIN: dict[str, dict[str, str]] = {
    "en": {
        "sales / e-commerce": "sales / e-commerce",
        "finance": "finance",
        "human resources": "human resources",
        "marketing": "marketing",
        "healthcare": "healthcare",
        "real estate": "real estate",
        "education": "education",
    },
    "fr": {
        "sales / e-commerce": "ventes / e-commerce",
        "finance": "finance",
        "human resources": "ressources humaines",
        "marketing": "marketing",
        "healthcare": "santé",
        "real estate": "immobilier",
        "education": "éducation",
    },
}

# Display names for the five semantic roles surfaced in the Dataset DNA section,
# in the same order build_report_context emits them.
ROLE_LABELS: dict[str, list[str]] = {
    "en": ["Measures", "Dimensions", "Temporal", "Geographic", "Identifiers"],
    "fr": ["Mesures", "Dimensions", "Temporel", "Géographique", "Identifiants"],
}

_FR_MONTHS = [
    "janvier",
    "février",
    "mars",
    "avril",
    "mai",
    "juin",
    "juillet",
    "août",
    "septembre",
    "octobre",
    "novembre",
    "décembre",
]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def normalize_lang(language: str | None) -> str:
    """Collapse any locale string to the supported ``"en"`` / ``"fr"``."""
    return "fr" if str(language or "en").strip().lower().startswith("fr") else "en"


def labels_for(lang: str) -> dict[str, str]:
    return LABELS.get(lang, LABELS["en"])


def archetype_for(code: str | None, lang: str) -> tuple[str | None, str | None]:
    table = ARCHETYPE.get(lang, ARCHETYPE["en"])
    if code in table:
        return table[code]
    return None, None


def domain_for(domain: str | None, lang: str) -> str | None:
    if not domain:
        return None
    return DOMAIN.get(lang, DOMAIN["en"]).get(domain, domain)


def role_labels_for(lang: str) -> list[str]:
    return ROLE_LABELS.get(lang, ROLE_LABELS["en"])


def fmt_int(value: Any, lang: str = "en") -> Any:
    """Group an integer (1234567 -> '1,234,567' / '1 234 567'). Pass non-numbers through."""
    try:
        n = int(round(float(value)))
    except (TypeError, ValueError):
        return value
    s = f"{n:,}"
    if lang == "fr":
        s = s.replace(",", " ")
    return s


def fmt_dec(value: Any, lang: str = "en", places: int = 2) -> Any:
    """Group a decimal with locale separators. Pass non-numbers through."""
    try:
        f = float(value)
    except (TypeError, ValueError):
        return value
    s = f"{f:,.{places}f}"
    if lang == "fr":
        s = s.replace(",", " ").replace(".", ",")
    return s


def fmt_date(dt: datetime, lang: str = "en") -> str:
    """Localized date-time string for the report cover/footer."""
    if lang == "fr":
        return f"{dt.day} {_FR_MONTHS[dt.month - 1]} {dt.year} à {dt:%H:%M} UTC"
    return dt.strftime("%B %d, %Y at %H:%M UTC")
