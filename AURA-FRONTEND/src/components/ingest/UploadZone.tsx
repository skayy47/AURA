"use client";
import { useState, useCallback } from "react";
import { useTranslations } from "next-intl";
import { motion, AnimatePresence } from "framer-motion";
import { cn } from "@/lib/utils";
import { AuraLoader } from "@/components/ui/AuraLoader";

interface Props { onFile: (f: File) => void; loading: boolean; }

export function UploadZone({ onFile, loading }: Props) {
  const t = useTranslations("ingest");
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
      <div className="absolute top-1/3 left-1/2 -translate-x-1/2 -translate-y-1/2 w-32 h-32
                      rounded-full bg-purple/10 blur-3xl pointer-events-none" />

      <AnimatePresence>
        {loading ? (
          <motion.div key="loading" initial={{ opacity: 0 }} animate={{ opacity: 1 }}
            className="flex flex-col items-center gap-3">
            <AuraLoader label={t("processingFile")} />
          </motion.div>
        ) : (
          <motion.div key="idle" initial={{ opacity: 0 }} animate={{ opacity: 1 }}
            className="flex flex-col items-center gap-3">
            <div className="w-14 h-14 rounded-full bg-surface2 border border-[rgba(90,60,200,0.5)]
                            flex items-center justify-center text-2xl">↑</div>
            <div>
              <p className="text-text font-semibold text-lg">{t("dropHere")}</p>
              <p className="text-text-d text-sm mt-1">or</p>
            </div>
            <label className="aura-btn-neon cursor-pointer">
              <span>{t("browseFiles")}</span>
              <input type="file" className="hidden"
                accept=".csv,.xlsx,.xls,.json,.parquet,.tsv"
                onChange={(e) => { const f = e.target.files?.[0]; if (f) onFile(f); }} />
            </label>
            <p className="text-text-d text-xs mt-1">{t("limitNote")}</p>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
}
