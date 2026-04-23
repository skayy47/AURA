"use client";
import { motion } from "framer-motion";

interface Props {
  data: Array<{ column: string; missing: number; pct: number }>;
  nRows: number;
}

export function AuraMissingHeatmap({ data, nRows }: Props) {
  const totalMissing = data.reduce((a, c) => a + c.missing, 0);

  return (
    <div className="aura-card p-6">
      <div className="flex items-baseline justify-between mb-4">
        <div>
          <h3 className="font-bricolage font-bold text-text text-lg">
            Missing Value Pattern
          </h3>
          <p className="text-xs text-text-d mt-0.5">
            {totalMissing.toLocaleString()} missing across {data.length} columns
          </p>
        </div>
      </div>

      <div className="space-y-1.5">
        {data.map((col, i) => {
          const pct = col.pct;
          return (
            <motion.div
              key={col.column}
              initial={{ opacity: 0, x: -10 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: i * 0.02 }}
              className="flex items-center gap-3 text-xs"
            >
              <span
                className="font-geist-mono text-text-m truncate shrink-0"
                style={{ width: 140 }}
                title={col.column}
              >
                {col.column}
              </span>
              <div className="flex-1 h-5 rounded bg-white/[0.04] border border-white/[0.05] overflow-hidden relative">
                {pct > 0 && (
                  <motion.div
                    initial={{ width: 0 }}
                    animate={{ width: `${Math.max(pct, 0.5)}%` }}
                    transition={{ delay: i * 0.02 + 0.1, duration: 0.5, ease: "easeOut" }}
                    className="h-full"
                    style={{
                      background:
                        pct > 50
                          ? "linear-gradient(90deg, #EF4444, #F59E0B)"
                          : pct > 10
                          ? "linear-gradient(90deg, #F59E0B, #6C3FE5)"
                          : "linear-gradient(90deg, #6C3FE5, #22D3EE)",
                    }}
                  />
                )}
              </div>
              <span
                className="font-geist-mono tabular-nums shrink-0 text-right"
                style={{ width: 64, color: pct > 0 ? "#F1F5F9" : "#475569" }}
              >
                {pct.toFixed(1)}%
              </span>
              <span
                className="font-geist-mono tabular-nums shrink-0 text-right text-text-d"
                style={{ width: 64 }}
              >
                {col.missing.toLocaleString()}/{nRows.toLocaleString()}
              </span>
            </motion.div>
          );
        })}
      </div>

      {totalMissing === 0 && (
        <div className="text-center py-6 text-text-d text-sm">
          No missing values detected — dataset is complete.
        </div>
      )}
    </div>
  );
}
