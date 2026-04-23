"use client";
import { motion, AnimatePresence } from "framer-motion";
import { AuraHistogram } from "./AuraHistogram";
import type { ColumnProfile, DatasetProfile } from "@/lib/types";

interface Props {
  column: ColumnProfile | null;
  profile: DatasetProfile | null;
  onClose: () => void;
}

const kindColors: Record<string, string> = {
  numeric:     "#6C3FE5",
  datetime:    "#22D3EE",
  categorical: "#3B82F6",
  boolean:     "#F59E0B",
  text:        "#94A3B8",
  id:          "#EC4899",
  unknown:     "#475569",
};

function StatBox({ label, value }: { label: string; value: string | number }) {
  return (
    <div className="rounded-lg border border-white/[0.06] bg-white/[0.03] p-3">
      <p className="text-[0.6rem] font-bold tracking-[0.12em] uppercase text-text-d mb-1">
        {label}
      </p>
      <p className="font-geist-mono font-bold text-sm text-text tabular-nums break-all">
        {typeof value === "number" ? value.toLocaleString(undefined, { maximumFractionDigits: 3 }) : value}
      </p>
    </div>
  );
}

function topCorrelationsFor(col: string, profile: DatasetProfile): Array<{ other: string; r: number }> {
  if (!profile.correlation) return [];
  return profile.correlation.top_pairs
    .filter((p) => p.col_a === col || p.col_b === col)
    .slice(0, 5)
    .map((p) => ({ other: p.col_a === col ? p.col_b : p.col_a, r: p.r }));
}

export function AuraColumnProfile({ column, profile, onClose }: Props) {
  return (
    <AnimatePresence>
      {column && profile && (
        <>
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
            className="fixed inset-0 bg-black/50 backdrop-blur-sm z-40"
          />
          <motion.aside
            initial={{ x: "100%" }}
            animate={{ x: 0 }}
            exit={{ x: "100%" }}
            transition={{ type: "spring", stiffness: 300, damping: 32 }}
            className="fixed right-0 top-0 h-full w-full max-w-[440px] bg-[#0A1022] border-l border-white/[0.08] z-50 overflow-y-auto custom-scrollbar"
          >
            <div className="sticky top-0 bg-[#0A1022] border-b border-white/[0.06] p-5 z-10 flex items-start justify-between gap-3">
              <div>
                <p
                  className="text-[0.65rem] font-bold tracking-[0.12em] uppercase mb-1"
                  style={{ color: kindColors[column.kind] ?? "#94A3B8" }}
                >
                  {column.kind} · {column.dtype}
                </p>
                <h2 className="font-bricolage font-bold text-xl text-text break-all">
                  {column.name}
                </h2>
              </div>
              <button
                onClick={onClose}
                className="text-text-m hover:text-text text-2xl leading-none px-2"
                aria-label="Close"
              >
                ×
              </button>
            </div>

            <div className="p-5 space-y-5">
              {/* Top stats */}
              <div className="grid grid-cols-2 gap-2">
                <StatBox label="Missing" value={`${column.missing_pct}%`} />
                <StatBox label="Unique" value={column.n_unique} />
                {column.kind === "numeric" && column.mean !== undefined && (
                  <>
                    <StatBox label="Mean" value={column.mean} />
                    <StatBox label="Median" value={column.median!} />
                    <StatBox label="Std" value={column.std!} />
                    <StatBox label="Skew" value={column.skewness!} />
                    <StatBox label="Min" value={column.min!} />
                    <StatBox label="Max" value={column.max!} />
                  </>
                )}
                {column.kind === "datetime" && column.date_min && (
                  <>
                    <StatBox label="From" value={column.date_min.slice(0, 10)} />
                    <StatBox label="To" value={column.date_max!.slice(0, 10)} />
                    <StatBox label="Days" value={column.date_range_days ?? 0} />
                  </>
                )}
              </div>

              {/* Numeric histogram */}
              {column.histogram && column.histogram.length > 0 && (
                <div className="-mx-1">
                  <AuraHistogram
                    title="Distribution"
                    subtitle={`${column.histogram.length} bins · ${column.n_unique.toLocaleString()} unique`}
                    data={column.histogram}
                  />
                </div>
              )}

              {/* Top values */}
              {column.top_values.length > 0 && column.kind !== "numeric" && (
                <div>
                  <p className="text-[0.65rem] font-bold tracking-[0.12em] uppercase text-text-d mb-2">
                    Top values
                  </p>
                  <div className="space-y-1.5">
                    {column.top_values.slice(0, 10).map((tv) => {
                      const max = column.top_values[0].count || 1;
                      return (
                        <div key={tv.value} className="flex items-center gap-3 text-xs">
                          <span className="font-geist-mono text-text-m truncate flex-1" title={tv.value}>
                            {tv.value}
                          </span>
                          <div className="w-32 h-4 rounded bg-white/[0.04] overflow-hidden">
                            <div
                              className="h-full bg-gradient-to-r from-purple to-cyan"
                              style={{ width: `${(tv.count / max) * 100}%` }}
                            />
                          </div>
                          <span className="font-geist-mono text-text-d tabular-nums w-14 text-right">
                            {tv.count.toLocaleString()}
                          </span>
                        </div>
                      );
                    })}
                  </div>
                </div>
              )}

              {/* Correlations */}
              {column.kind === "numeric" && (
                (() => {
                  const corrs = topCorrelationsFor(column.name, profile);
                  if (!corrs.length) return null;
                  return (
                    <div>
                      <p className="text-[0.65rem] font-bold tracking-[0.12em] uppercase text-text-d mb-2">
                        Strongest correlations
                      </p>
                      <div className="space-y-1">
                        {corrs.map((c) => (
                          <div key={c.other} className="flex items-center justify-between text-xs font-geist-mono">
                            <span className="text-purple-l truncate mr-3">{c.other}</span>
                            <span
                              className="tabular-nums font-bold"
                              style={{ color: c.r >= 0 ? "#A78BFA" : "#FCA5A5" }}
                            >
                              r = {c.r.toFixed(3)}
                            </span>
                          </div>
                        ))}
                      </div>
                    </div>
                  );
                })()
              )}

              {/* Smart recommendations */}
              <div className="pt-4 border-t border-white/[0.06]">
                <p className="text-[0.65rem] font-bold tracking-[0.12em] uppercase text-text-d mb-2">
                  Recommendations
                </p>
                <ul className="space-y-1.5 text-xs text-text-m">
                  {column.kind === "id" && (
                    <li>✦ Likely an ID column — exclude from ML features</li>
                  )}
                  {column.missing_pct > 50 && (
                    <li>⚠ Over 50% missing — consider dropping this column</li>
                  )}
                  {column.missing_pct > 0 && column.missing_pct <= 50 && (
                    <li>✦ {column.missing_pct}% missing — imputed during Clean step</li>
                  )}
                  {column.kind === "numeric" && column.skewness !== undefined && Math.abs(column.skewness) > 1 && (
                    <li>✦ Skewed distribution (skew={column.skewness.toFixed(2)}) — consider log transform</li>
                  )}
                  {column.kind === "categorical" && column.n_unique > 50 && (
                    <li>⚠ High cardinality ({column.n_unique}) — consider bucketing</li>
                  )}
                  {column.kind === "boolean" && (
                    <li>✦ Binary feature — ready for ML as-is</li>
                  )}
                </ul>
              </div>
            </div>
          </motion.aside>
        </>
      )}
    </AnimatePresence>
  );
}
