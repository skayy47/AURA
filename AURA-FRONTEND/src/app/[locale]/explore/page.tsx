"use client";
import { useEffect, useState } from "react";
import { useTranslations } from "next-intl";
import { motion } from "framer-motion";
import { PipelineRoad } from "@/components/layout/PipelineRoad";
import { PageHeader } from "@/components/layout/PageHeader";
import { BarChart3 } from "@/components/layout/pipeline-icons";
import { EmptyState } from "@/components/ui/EmptyState";
import { MetricCard } from "@/components/ui/MetricCard";
import { NeonButton } from "@/components/ui/NeonButton";
import { AuraLoader } from "@/components/ui/AuraLoader";
import { InsightsStrip } from "@/components/explore/InsightsStrip";
import { AuraCorrelationHeatmap } from "@/components/explore/AuraCorrelationHeatmap";
import { AuraHistogram } from "@/components/explore/AuraHistogram";
import { AuraScatter } from "@/components/explore/AuraScatter";
import { AuraMissingHeatmap } from "@/components/explore/AuraMissingHeatmap";
import { AuraColumnProfile } from "@/components/explore/AuraColumnProfile";
import { ExportPDFButton } from "@/components/explore/ExportPDFButton";
import { fetchExplore, fetchAnalysis, type AnalysisInsight } from "@/lib/api";
import { useStore } from "@/lib/store";
import type { ChartRecommendation, ColumnProfile } from "@/lib/types";
import { cn } from "@/lib/utils";
import { useRouter } from "@/i18n/navigation";

const kindColor: Record<string, string> = {
  numeric:     "#6C3FE5",
  datetime:    "#22D3EE",
  categorical: "#3B82F6",
  boolean:     "#F59E0B",
  text:        "#94A3B8",
  id:          "#EC4899",
  unknown:     "#475569",
};

export default function ExplorePage() {
  const t = useTranslations("explore");
  const router = useRouter();
  const { sessionId, meta, exploreData, setExplore } = useStore();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedColumn, setSelectedColumn] = useState<ColumnProfile | null>(null);
  const [insights, setInsights] = useState<AnalysisInsight[]>([]);

  useEffect(() => {
    if (sessionId && !exploreData && !loading) {
      setLoading(true);
      fetchExplore(sessionId)
        .then((res) => setExplore(res))
        .catch((e) => setError(e.message))
        .finally(() => setLoading(false));
    }
  }, [sessionId, exploreData]);

  useEffect(() => {
    if (sessionId) {
      fetchAnalysis(sessionId)
        .then((res) => setInsights(res.insights ?? []))
        .catch(() => null);
    }
  }, [sessionId]);

  if (!meta || !sessionId) return <EmptyState />;

  const profile = exploreData?.profile;
  const recommendations = exploreData?.recommendations ?? [];

  return (
    <div>
      <PipelineRoad />
      <PageHeader
        icon={<BarChart3 size={28} className="text-blue" />}
        title={t("title")}
        subtitle={t("subtitle")}
      />

      {loading && (
        <div className="flex justify-center py-16">
          <AuraLoader label="Analyzing" />
        </div>
      )}

      {error && (
        <div className="mt-4 p-4 rounded-lg bg-red-500/10 border border-red-500/30 text-red-400 text-sm">
          {error}
        </div>
      )}

      {profile && (
        <div className="space-y-8 mt-4">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
            <MetricCard value={profile.n_rows} label={t("rowsLabel")} index={0} />
            <MetricCard value={profile.n_cols} label={t("colsLabel")} index={1} />
            <MetricCard
              value={profile.correlation?.top_pairs?.[0]?.r.toFixed(2) ?? "—"}
              label={t("topRLabel")}
              variant="purple"
              index={2}
            />
            <MetricCard
              value={`${profile.memory_mb.toFixed(2)} MB`}
              label={t("memoryLabel")}
              variant="blue"
              index={3}
            />
          </div>

          {insights.length > 0 && (
            <motion.div
              initial={{ opacity: 0, y: 14 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 }}
              className="aura-card p-6"
            >
              <div className="flex items-center gap-2 mb-4">
                <span className="w-1.5 h-1.5 rounded-full bg-cyan" style={{ boxShadow: "0 0 8px var(--cyan)" }} />
                <h3 className="font-bricolage font-bold text-text text-lg">AI Analyst — Key Findings</h3>
                <span className="text-[0.7rem] text-text-d ml-1">ranked by impact</span>
              </div>
              <div className="space-y-2.5">
                {insights.map((f, i) => {
                  const sev = f.severity === 3
                    ? { bar: "#fb7185", tag: "Critical", cls: "text-[#fb7185] bg-[rgba(251,113,133,0.12)]" }
                    : f.severity === 2
                    ? { bar: "#00e5ff", tag: "Notable", cls: "text-cyan bg-[rgba(0,229,255,0.12)]" }
                    : { bar: "#4a5878", tag: "Minor", cls: "text-text-m bg-white/[0.05]" };
                  return (
                    <div key={i} className="flex gap-3 items-start p-3 rounded-xl bg-white/[0.02] border border-white/[0.06]">
                      <span className="w-1 self-stretch rounded-full shrink-0" style={{ background: sev.bar }} />
                      <div className="flex-1 min-w-0">
                        <h4 className="text-sm font-semibold text-text">{f.title}</h4>
                        <p className="text-xs text-text-m mt-0.5 leading-relaxed">{f.detail}</p>
                      </div>
                      <span className={cn("text-[0.6rem] font-bold tracking-wide uppercase px-2 py-0.5 rounded-md shrink-0", sev.cls)}>
                        {sev.tag}
                      </span>
                    </div>
                  );
                })}
              </div>
            </motion.div>
          )}

          <InsightsStrip profile={profile} />

          <div
            className="grid gap-4"
            style={{ gridTemplateColumns: "repeat(auto-fit, minmax(480px, 1fr))" }}
          >
            {recommendations.map((rec, i) => (
              <ChartTile
                key={`${rec.type}-${i}`}
                rec={rec}
                profile={profile}
                delay={0.4 + i * 0.12}
              />
            ))}

            <motion.div
              initial={{ opacity: 0, y: 14 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.4 + recommendations.length * 0.12 }}
              style={{ gridColumn: "1 / -1" }}
            >
              <AuraMissingHeatmap data={profile.missing_by_col} nRows={profile.n_rows} />
            </motion.div>
          </div>

          <div className="aura-card p-6">
            <h3 className="font-bricolage font-bold text-text text-lg mb-4">
              {t("columnsHeading")}
            </h3>
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-2">
              {profile.columns.map((col) => (
                <button
                  key={col.name}
                  onClick={() => setSelectedColumn(col)}
                  className={cn(
                    "text-left p-2.5 rounded-lg border border-white/[0.06]",
                    "bg-white/[0.02] hover:bg-white/[0.05] hover:border-purple/30",
                    "transition-all duration-150 group"
                  )}
                >
                  <div className="flex items-center gap-2 mb-1">
                    <span
                      className="w-1.5 h-1.5 rounded-full shrink-0"
                      style={{ background: kindColor[col.kind] }}
                    />
                    <span className="text-xs font-geist-mono text-text truncate group-hover:text-text">
                      {col.name}
                    </span>
                  </div>
                  <p
                    className="text-[0.65rem] font-bold tracking-[0.1em] uppercase"
                    style={{ color: kindColor[col.kind] }}
                  >
                    {col.kind} · {col.missing_pct}% missing
                  </p>
                </button>
              ))}
            </div>
          </div>

          <div className="flex items-center justify-between pt-4 border-t border-white/[0.06]">
            <ExportPDFButton sessionId={sessionId} />
            <NeonButton onClick={() => router.push("/ai-chat")}>
              {t("nextChat")}
            </NeonButton>
          </div>
        </div>
      )}

      <AuraColumnProfile
        column={selectedColumn}
        profile={profile ?? null}
        onClose={() => setSelectedColumn(null)}
      />
    </div>
  );
}

interface ChartTileProps {
  rec: ChartRecommendation;
  profile: import("@/lib/types").DatasetProfile;
  delay: number;
}

function ChartTile({ rec, profile, delay }: ChartTileProps) {
  const fullWidth: React.CSSProperties = { gridColumn: "1 / -1" };

  switch (rec.type) {
    case "heatmap_corr": {
      if (!profile.correlation) return null;
      return (
        <motion.div initial={{ opacity: 0, y: 14 }} animate={{ opacity: 1, y: 0 }} transition={{ delay }} style={fullWidth}>
          <AuraCorrelationHeatmap data={profile.correlation} />
        </motion.div>
      );
    }
    case "histogram": {
      const colName = rec.column ?? "";
      const col = profile.columns.find((c) => c.name === colName);
      if (!col?.histogram?.length) return null;
      return (
        <motion.div initial={{ opacity: 0, y: 14 }} animate={{ opacity: 1, y: 0 }} transition={{ delay }}>
          <AuraHistogram title={`Distribution — ${colName}`} subtitle={rec.rationale} data={col.histogram} />
        </motion.div>
      );
    }
    case "scatter": {
      const points = (rec.points ?? []) as Array<{ x: number; y: number }>;
      if (!points.length) return null;
      return (
        <motion.div initial={{ opacity: 0, y: 14 }} animate={{ opacity: 1, y: 0 }} transition={{ delay }}>
          <AuraScatter title={`${rec.x} × ${rec.y}`} subtitle={rec.rationale} xLabel={rec.x ?? "x"} yLabel={(rec.y as string) ?? "y"} points={points} />
        </motion.div>
      );
    }
    case "bar_grouped": {
      const bars = rec.bars ?? [];
      if (!bars.length) return null;
      const binData = bars.map((b) => ({ bin: b.label, lo: 0, hi: 0, count: b.value }));
      return (
        <motion.div initial={{ opacity: 0, y: 14 }} animate={{ opacity: 1, y: 0 }} transition={{ delay }}>
          <AuraHistogram title={`${rec.y} by ${rec.x}`} subtitle={rec.rationale} data={binData} />
        </motion.div>
      );
    }
    case "timeseries": {
      const points = (rec.points ?? []) as Array<Record<string, any>>;
      if (!points.length) return null;
      const yCols = Array.isArray(rec.y) ? rec.y : [rec.y as string];
      const firstY = yCols[0];
      const simplified = points.map((p) => ({ bin: String(p.x).slice(0, 10), lo: 0, hi: 0, count: Number(p[firstY]) || 0 }));
      return (
        <motion.div initial={{ opacity: 0, y: 14 }} animate={{ opacity: 1, y: 0 }} transition={{ delay }} style={fullWidth}>
          <AuraHistogram title={`${firstY} over ${rec.x}`} subtitle={rec.rationale} data={simplified} />
        </motion.div>
      );
    }
    default:
      return null;
  }
}
