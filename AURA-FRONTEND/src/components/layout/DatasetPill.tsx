"use client";
import { useStore } from "@/lib/store";
import { motion, AnimatePresence } from "framer-motion";

export function DatasetPill() {
  const meta = useStore((s) => s.meta);
  const cleanResult = useStore((s) => s.cleanResult);

  if (!meta) return null;

  const isCleaned = !!cleanResult;
  const status = isCleaned ? "Cleaned" : "Raw";

  return (
    <AnimatePresence>
      <motion.div
        initial={{ y: 20, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        exit={{ y: 20, opacity: 0 }}
        className="fixed bottom-6 start-6 z-50 flex items-center gap-3 px-4 py-2 bg-[#070C1A] border border-border rounded-full shadow-aura-sm backdrop-blur-md text-sm font-mono"
      >
        <span>📊</span>
        <span className="text-text max-w-[150px] truncate" title={meta.name}>{meta.name}</span>
        <span className="text-text-d">·</span>
        <span className="text-text-m">{isCleaned ? cleanResult.rows_after : meta.n_rows}×{isCleaned ? cleanResult.cols_after : meta.n_cols}</span>
        <span className="text-text-d">·</span>
        <span className={isCleaned ? "text-green-400" : "text-amber-400"}>{status}</span>
      </motion.div>
    </AnimatePresence>
  );
}
