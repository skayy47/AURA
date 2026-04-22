"use client";
import { useState, useCallback } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { cn } from "@/lib/utils";

interface Props { onFile: (f: File) => void; loading: boolean; }

export function UploadZone({ onFile, loading }: Props) {
  const [drag, setDrag] = useState(false);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setDrag(false);
    const f = e.dataTransfer.files[0];
    if (f) onFile(f);
  }, [onFile]);

  return (
    <motion.div
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      className={cn(
        "relative border rounded-lg p-16 text-center cursor-pointer transition-all duration-300",
        "bg-[radial-gradient(ellipse_at_center,rgba(108,63,229,0.07)_0%,rgba(4,7,18,0.98)_70%)]",
        drag
          ? "border-purple shadow-glow"
          : "border-[rgba(90,60,200,0.4)] hover:border-purple hover:shadow-glow-sm"
      )}
      onDragOver={(e) => { e.preventDefault(); setDrag(true); }}
      onDragLeave={() => setDrag(false)}
      onDrop={handleDrop}
    >
      {/* Glow orb */}
      <div className="absolute top-1/3 left-1/2 -translate-x-1/2 -translate-y-1/2 w-32 h-32
                      rounded-full bg-purple/10 blur-3xl pointer-events-none" />

      <AnimatePresence>
        {loading ? (
          <motion.div key="loading" initial={{ opacity: 0 }} animate={{ opacity: 1 }}
            className="flex flex-col items-center gap-3">
            <div className="w-12 h-12 rounded-full border-2 border-purple border-t-transparent animate-spin" />
            <p className="text-text-m text-sm">Processing file…</p>
          </motion.div>
        ) : (
          <motion.div key="idle" initial={{ opacity: 0 }} animate={{ opacity: 1 }}
            className="flex flex-col items-center gap-3">
            <div className="w-14 h-14 rounded-full bg-surface2 border border-[rgba(90,60,200,0.5)]
                            flex items-center justify-center text-2xl">↑</div>
            <div>
              <p className="text-text font-semibold text-lg">Drop your file here</p>
              <p className="text-text-d text-sm mt-1">or</p>
            </div>
            <label className="aura-btn cursor-pointer">
              Browse Files
              <input type="file" className="hidden"
                accept=".csv,.xlsx,.xls,.json,.parquet,.tsv"
                onChange={(e) => { const f = e.target.files?.[0]; if (f) onFile(f); }} />
            </label>
            <p className="text-text-d text-xs mt-1">
              Limit 200 MB · CSV · XLS · XLSX · JSON · PARQUET · TSV
            </p>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
}
