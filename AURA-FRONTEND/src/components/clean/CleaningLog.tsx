"use client";
import { motion } from "framer-motion";
import { Check } from "@/components/layout/pipeline-icons";
import { cn } from "@/lib/utils";
import type { CleanLogEntry } from "@/lib/types";

interface Props {
  log: CleanLogEntry[];
}

type Status = "ok" | "warn" | "error";

function deriveStatus(entry: CleanLogEntry): Status {
  if (entry.status) return entry.status;
  if (/FAILED|error/i.test(entry.detail)) return "error";
  if (/SKIPPED|warning/i.test(entry.detail)) return "warn";
  return "ok";
}

const statusClass: Record<Status, string> = {
  ok:    "bg-green/15 border-green/50 text-green",
  warn:  "bg-amber/15 border-amber/50 text-amber",
  error: "bg-red-500/15 border-red-500/50 text-red-400",
};

export function CleaningLog({ log }: Props) {
  if (!log || log.length === 0) {
    return (
      <div className="aura-card p-6">
        <p className="text-sm text-text-d">No cleaning steps recorded.</p>
      </div>
    );
  }

  // Extract quality score from last SchemaValidator entry if present
  const validator = log.find((e) => e.step === "Schema Validator");
  const scoreMatch = validator?.detail.match(/Quality score: ([\d.]+)\/100/);
  const score = scoreMatch ? parseFloat(scoreMatch[1]) : null;

  return (
    <div className="aura-card p-6 space-y-5">
      <div className="flex items-baseline justify-between">
        <h3 className="text-lg font-bricolage font-bold text-text">
          Cleaning Audit Trail
        </h3>
        {score !== null && (
          <div className="flex items-baseline gap-2">
            <span className="text-text-d text-xs uppercase tracking-widest">Quality</span>
            <span
              className="font-geist-mono font-bold text-2xl"
              style={{ color: score >= 80 ? "#10B981" : score >= 60 ? "#F59E0B" : "#EF4444" }}
            >
              {score}
            </span>
            <span className="text-text-d text-sm">/100</span>
          </div>
        )}
      </div>

      <div className="relative ps-2">
        <div
          className="absolute start-4 top-3 bottom-3 w-px opacity-40"
          style={{ background: "linear-gradient(180deg, #6C3FE5, #3B82F6, transparent)" }}
          aria-hidden="true"
        />

        <ol className="space-y-4">
          {log.map((entry, i) => {
            const status = deriveStatus(entry);
            return (
              <motion.li
                key={i}
                initial={{ x: -16, opacity: 0 }}
                animate={{ x: 0, opacity: 1 }}
                transition={{ delay: i * 0.08, ease: "easeOut", duration: 0.35 }}
                className="flex gap-3 items-start relative"
              >
                <div
                  className={cn(
                    "w-8 h-8 rounded-full flex items-center justify-center shrink-0 border-2 z-10 bg-bg",
                    statusClass[status],
                  )}
                >
                  <Check size={14} />
                </div>

                <div className="flex-1 pb-1 min-w-0">
                  <div className="flex items-baseline gap-2 flex-wrap">
                    <h4 className="font-bricolage font-bold text-sm text-text">
                      {entry.step}
                    </h4>
                    {entry.rows_changed ? (
                      <span className="text-[0.7rem] font-geist-mono text-text-d px-2 py-0.5 rounded bg-white/[0.04] border border-white/[0.06]">
                        {entry.rows_changed.toLocaleString()} rows
                      </span>
                    ) : null}
                  </div>

                  <p className="text-xs text-text-m font-geist-mono mt-1 leading-relaxed break-words">
                    {entry.detail}
                  </p>

                  {entry.affected_columns && entry.affected_columns.length > 0 && (
                    <div className="flex flex-wrap gap-1 mt-2">
                      {entry.affected_columns.slice(0, 6).map((col) => (
                        <span
                          key={col}
                          className="text-[0.7rem] px-2 py-0.5 rounded bg-purple/10 text-purple-l font-geist-mono border border-purple/20"
                        >
                          {col}
                        </span>
                      ))}
                      {entry.affected_columns.length > 6 && (
                        <span className="text-[0.7rem] text-text-d self-center">
                          +{entry.affected_columns.length - 6} more
                        </span>
                      )}
                    </div>
                  )}
                </div>
              </motion.li>
            );
          })}
        </ol>
      </div>
    </div>
  );
}
