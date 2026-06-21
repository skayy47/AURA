"use client";
import { useState } from "react";
import { useTranslations, useLocale } from "next-intl";
import { motion, AnimatePresence } from "framer-motion";

interface Props {
  sessionId: string;
}

type State = "idle" | "loading" | "error";

export function ExportPDFButton({ sessionId }: Props) {
  const t = useTranslations("actions");
  const tErrors = useTranslations("errors");
  const locale = useLocale();
  const [state, setState] = useState<State>("idle");

  const handleExport = async () => {
    if (state === "loading") return;
    setState("loading");
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
      const res = await fetch(`${apiUrl}/api/export/pdf`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ session_id: sessionId, lang: locale }),
      });
      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err.detail ?? `HTTP ${res.status}`);
      }
      const blob = await res.blob();
      const url  = URL.createObjectURL(blob);
      const a    = document.createElement("a");
      a.href     = url;
      a.download = "aura_report.pdf";
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
      setState("idle");
    } catch {
      setState("error");
      setTimeout(() => setState("idle"), 3000);
    }
  };

  return (
    <div className="relative inline-flex items-center">
      <button
        onClick={handleExport}
        disabled={state === "loading"}
        className={`
          group relative flex items-center gap-2 px-5 py-2.5 rounded-full text-sm font-medium
          border transition-all duration-200 overflow-hidden
          ${state === "error"
            ? "border-red-500/50 text-red-400 bg-red-500/10"
            : "border-purple/40 text-text-m hover:text-text hover:border-purple/70 bg-purple/5 hover:bg-purple/10"}
          disabled:opacity-60 disabled:cursor-not-allowed
        `}
      >
        {/* loading shimmer */}
        {state === "loading" && (
          <motion.span
            className="absolute inset-0 bg-gradient-to-r from-transparent via-purple/20 to-transparent"
            animate={{ x: ["-100%", "100%"] }}
            transition={{ duration: 1.2, repeat: Infinity, ease: "linear" }}
          />
        )}

        {/* PDF icon */}
        <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="shrink-0">
          <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
          <polyline points="14 2 14 8 20 8" />
          <line x1="16" x2="8" y1="13" y2="13" />
          <line x1="16" x2="8" y1="17" y2="17" />
        </svg>

        <span className="relative z-10">
          {state === "loading"
            ? t("generating")
            : state === "error"
            ? tErrors("renderTimeout")
            : t("exportPdf")}
        </span>
      </button>

      {/* tooltip on error */}
      <AnimatePresence>
        {state === "error" && (
          <motion.span
            initial={{ opacity: 0, y: 4 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 4 }}
            className="absolute top-full mt-1 start-0 text-[10px] text-red-400 whitespace-nowrap"
          >
            {tErrors("renderTimeout")}
          </motion.span>
        )}
      </AnimatePresence>
    </div>
  );
}
