"use client";
import { useLocale } from "next-intl";
import { motion } from "framer-motion";
import type { DatasetProfile } from "@/lib/types";

interface Props {
  profile: DatasetProfile;
}

function buildInsights(profile: DatasetProfile, isFr: boolean): string[] {
  const insights: string[] = [];

  const top = profile.correlation?.top_pairs?.[0];
  if (top && Math.abs(top.r) >= 0.3) {
    if (isFr) {
      const strength = Math.abs(top.r) > 0.7 ? "Fort" : Math.abs(top.r) > 0.4 ? "Modéré" : "Faible";
      insights.push(`${strength} signal : ${top.col_a} × ${top.col_b} (r=${top.r.toFixed(2)})`);
    } else {
      const strength = Math.abs(top.r) > 0.7 ? "Strong" : Math.abs(top.r) > 0.4 ? "Moderate" : "Weak";
      insights.push(`${strength} signal: ${top.col_a} × ${top.col_b} (r=${top.r.toFixed(2)})`);
    }
  }

  const totalCells = profile.n_rows * profile.n_cols;
  if (totalCells > 0 && profile.missing_total > 0) {
    const pct = (profile.missing_total / totalCells) * 100;
    if (isFr) {
      insights.push(`${pct.toFixed(1)} % des cellules manquantes — ${profile.missing_total.toLocaleString()} valeurs nulles`);
    } else {
      insights.push(`${pct.toFixed(1)}% of cells missing — ${profile.missing_total.toLocaleString()} null values`);
    }
  }

  const dateCol = profile.columns.find((c) => c.kind === "datetime" && c.date_range_days !== undefined);
  if (dateCol && dateCol.date_min && dateCol.date_max) {
    const dmin = dateCol.date_min.slice(0, 10);
    const dmax = dateCol.date_max.slice(0, 10);
    if (isFr) {
      insights.push(`${dateCol.date_range_days} jours de données — ${dmin} → ${dmax}`);
    } else {
      insights.push(`${dateCol.date_range_days} days of data — ${dmin} → ${dmax}`);
    }
  }

  if (profile.duplicate_rows > 0) {
    if (isFr) {
      insights.push(`${profile.duplicate_rows.toLocaleString()} doublon${profile.duplicate_rows !== 1 ? "s" : ""} détecté${profile.duplicate_rows !== 1 ? "s" : ""}`);
    } else {
      insights.push(`${profile.duplicate_rows.toLocaleString()} duplicate row${profile.duplicate_rows !== 1 ? "s" : ""} detected`);
    }
  }

  const idCols = profile.columns.filter((c) => c.kind === "id");
  if (idCols.length) {
    const names = idCols.slice(0, 2).map((c) => c.name).join(", ") + (idCols.length > 2 ? "…" : "");
    if (isFr) {
      insights.push(`${idCols.length} colonne${idCols.length !== 1 ? "s" : ""} identifiant : ${names}`);
    } else {
      insights.push(`${idCols.length} ID-like column${idCols.length !== 1 ? "s" : ""}: ${names}`);
    }
  }

  if (profile.memory_mb > 0.001) {
    if (isFr) {
      insights.push(`Taille en mémoire : ${profile.memory_mb.toFixed(2)} Mo`);
    } else {
      insights.push(`In-memory size: ${profile.memory_mb.toFixed(2)} MB`);
    }
  }

  return insights;
}

export function InsightsStrip({ profile }: Props) {
  const locale = useLocale();
  const isFr = locale.startsWith("fr");
  const insights = buildInsights(profile, isFr);
  if (!insights.length) return null;

  return (
    <div className="flex flex-wrap gap-2">
      {insights.map((text, i) => (
        <motion.div
          key={i}
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: i * 0.08 + 0.1, duration: 0.35 }}
          className="px-3 py-1.5 rounded-full bg-purple/10 border border-purple/20 text-xs text-purple-l font-geist-mono"
        >
          <span className="text-cyan me-1.5">✦</span>
          {text}
        </motion.div>
      ))}
    </div>
  );
}
