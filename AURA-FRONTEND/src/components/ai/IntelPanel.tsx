"use client";
import { useMemo } from "react";
import { motion } from "framer-motion";
import { AuraBot, type BotState } from "./AuraBot";
import { useStore } from "@/lib/store";
import { cn } from "@/lib/utils";

interface IntelPanelProps {
  botState: BotState;
  onSuggestionClick: (q: string) => void;
  onHistoryClick: (index: number) => void;
  onBotClick?: () => void;
  disabled?: boolean;
}

const STATUS_LABEL: Record<BotState, string> = {
  idle: "Standing by",
  listening: "Listening...",
  thinking: "Analyzing...",
  speaking: "Responding...",
  celebrate: "Got it.",
  error: "Recovering",
};

function parseQualityScore(detail: string | undefined): number | null {
  if (!detail) return null;
  const m = detail.match(/Quality score:\s*([\d.]+)\s*\/\s*100/i);
  return m ? Math.round(parseFloat(m[1])) : null;
}

function buildSuggestions(meta: any, exploreData: any): string[] {
  const numericCols: string[] = meta?.estimated_numeric_cols ?? [];
  const firstNumeric = numericCols[0];

  const topPair = exploreData?.profile?.correlation?.top_pairs?.[0];

  const suggestions: string[] = [];
  suggestions.push("What columns have the most missing values?");

  if (topPair && Math.abs(topPair.r) >= 0.3) {
    suggestions.push(`Why is ${topPair.col_a} correlated with ${topPair.col_b}?`);
  } else {
    suggestions.push("Show me correlations above 0.7");
  }

  if (firstNumeric) {
    suggestions.push(`Are there outliers in ${firstNumeric}?`);
  } else {
    suggestions.push("Which columns look most problematic?");
  }

  suggestions.push("Summarize this dataset in 3 sentences");
  return suggestions;
}

function MicroMetric({ label, value, color, index }: { label: string; value: string; color: string; index: number }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 6 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.1 + index * 0.05, duration: 0.3 }}
      className={cn(
        "rounded-xl px-3 py-2.5 border border-white/[0.06]",
        "bg-gradient-to-b from-white/[0.04] to-transparent",
        "transition-shadow duration-300 hover:shadow-[0_0_18px_rgba(108,63,229,0.12)]"
      )}
    >
      <p className="text-[0.6rem] tracking-[0.12em] uppercase text-text-d font-bold mb-0.5">{label}</p>
      <p className="font-geist-mono font-bold text-lg leading-none tabular-nums" style={{ color }}>{value}</p>
    </motion.div>
  );
}

export function IntelPanel({ botState, onSuggestionClick, onHistoryClick, onBotClick, disabled }: IntelPanelProps) {
  const { meta, cleanResult, exploreData, chatHistory } = useStore();

  const qualityScore = useMemo(() => {
    const log = cleanResult?.log ?? [];
    const validatorEntry = log.find((e: any) =>
      typeof e.step === "string" && e.step.toLowerCase().includes("schema")
    );
    return parseQualityScore(validatorEntry?.detail);
  }, [cleanResult]);

  const suggestions = useMemo(() => buildSuggestions(meta, exploreData), [meta, exploreData]);

  const userMessages = useMemo(() => {
    return chatHistory
      .map((m, i) => ({ message: m, index: i }))
      .filter(({ message }) => message.role === "user");
  }, [chatHistory]);

  const lastUserIdx = userMessages.length > 0 ? userMessages[userMessages.length - 1].index : -1;

  return (
    <aside
      className="w-[320px] shrink-0 h-full flex flex-col bg-[#070C1A] border-e border-border overflow-hidden"
      aria-label="AI Chat intelligence panel"
    >
      <div className="px-5 pt-5 pb-3 flex flex-col items-center border-b border-border">
        <div className="relative">
          <div className="absolute -inset-3 rounded-full bg-gradient-to-br from-aurora-purple/20 via-aurora-cyan/15 to-transparent blur-xl pointer-events-none" />
          <AuraBot state={botState} size={140} onClick={onBotClick} ariaLabel={`AURA bot - ${STATUS_LABEL[botState]}`} />
        </div>
        <p className="font-geist-mono text-[0.7rem] tracking-[0.12em] uppercase text-text-d mt-1">
          {STATUS_LABEL[botState]}
        </p>
      </div>

      <div className="flex-1 overflow-y-auto custom-scrollbar px-5 py-4 space-y-6">

        <section>
          <div className="h-[2px] bg-gradient-to-r from-aurora-purple via-aurora-cyan to-transparent mb-3 rounded-full" />
          <p className="font-bricolage font-bold text-[0.65rem] tracking-[0.15em] uppercase text-text-m mb-3">
            Dataset Vitals
          </p>

          {meta ? (
            <>
              <div className="grid grid-cols-2 gap-2 mb-3">
                <MicroMetric label="Rows" value={meta.n_rows.toLocaleString()} color="#10B981" index={0} />
                <MicroMetric label="Columns" value={meta.n_cols.toString()} color="#3B82F6" index={1} />
                <MicroMetric
                  label="Quality"
                  value={qualityScore !== null ? `${qualityScore}%` : "—"}
                  color="#8B5CF6"
                  index={2}
                />
                <MicroMetric
                  label="Missing"
                  value={meta.missing_total.toLocaleString()}
                  color={meta.missing_total > 0 ? "#F59E0B" : "#10B981"}
                  index={3}
                />
              </div>
              <p className="font-geist-mono text-[0.7rem] text-text-d truncate" title={meta.name}>
                {meta.name}
              </p>
            </>
          ) : (
            <p className="text-text-d text-xs">No dataset loaded.</p>
          )}
        </section>

        {userMessages.length > 0 && (
          <section>
            <p className="font-bricolage font-bold text-[0.65rem] tracking-[0.15em] uppercase text-text-m mb-3">
              Suggested Questions
            </p>
            <div className="space-y-2">
              {suggestions.map((q, i) => {
                const dot = i % 3 === 0 ? "#8b5cf6" : i % 3 === 1 ? "#00e5ff" : "#3b82f6";
                return (
                  <motion.button
                    key={i}
                    initial={{ opacity: 0, x: -6 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: 0.15 + i * 0.06, duration: 0.3 }}
                    onClick={() => !disabled && onSuggestionClick(q)}
                    disabled={disabled}
                    className="group w-full text-start flex items-start gap-2 rounded-xl p-3 bg-[rgba(11,20,38,0.7)] border border-border hover:border-cyan/45 hover:bg-[rgba(11,20,38,0.95)] transition-colors disabled:opacity-50 disabled:cursor-not-allowed cursor-pointer"
                  >
                    <span
                      className="mt-1 w-1.5 h-1.5 rounded-full shrink-0"
                      style={{ backgroundColor: dot, boxShadow: `0 0 6px ${dot}` }}
                    />
                    <p className="text-[0.78rem] leading-snug text-text font-medium group-hover:text-white">
                      {q}
                    </p>
                  </motion.button>
                );
              })}
            </div>
          </section>
        )}

        {userMessages.length > 0 && (
          <section>
            <p className="font-bricolage font-bold text-[0.65rem] tracking-[0.15em] uppercase text-text-m mb-3">
              Conversation
            </p>
            <ul className="space-y-1">
              {userMessages.map(({ message, index }) => {
                const isLast = index === lastUserIdx;
                const truncated = message.content.length > 70
                  ? message.content.slice(0, 70).trim() + "…"
                  : message.content;
                return (
                  <li key={index}>
                    <button
                      onClick={() => onHistoryClick(index)}
                      className={cn(
                        "w-full text-start relative ps-3 pe-2 py-1.5 rounded-e text-[0.78rem] leading-snug",
                        "transition-colors hover:bg-surface2/60",
                        isLast ? "text-text" : "text-text-m"
                      )}
                    >
                      {isLast && (
                        <span className="absolute start-0 top-1.5 bottom-1.5 w-[3px] rounded-full bg-purple" />
                      )}
                      <span className="block truncate">{truncated}</span>
                    </button>
                  </li>
                );
              })}
            </ul>
          </section>
        )}

      </div>
    </aside>
  );
}
