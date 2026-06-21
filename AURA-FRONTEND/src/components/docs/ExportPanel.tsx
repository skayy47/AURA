"use client";
import { useState } from "react";
import { useLocale, useTranslations } from "next-intl";
import { exportUrl } from "@/lib/api";

const DownloadIcon = ({ size = 18 }: { size?: number }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor"
    strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
    <polyline points="7 10 12 15 17 10" />
    <line x1="12" y1="15" x2="12" y2="3" />
  </svg>
);

export function ExportPanel({ sessionId }: { sessionId: string }) {
  const locale = useLocale();
  const t = useTranslations("docs");
  const [pdfState, setPdfState] = useState<"idle" | "loading" | "error">("idle");

  const formats = [
    { id: "csv", label: "CSV", desc: t("descCsv") },
    { id: "xlsx", label: "Excel", desc: t("descXlsx") },
    { id: "json", label: "JSON", desc: t("descJson") },
    { id: "parquet", label: "Parquet", desc: t("descParquet") },
  ] as const;

  const handlePdf = async () => {
    if (pdfState === "loading") return;
    setPdfState("loading");
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
      const res = await fetch(`${apiUrl}/api/export/pdf`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ session_id: sessionId, lang: locale }),
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const blob = await res.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = "aura_data_intelligence_report.pdf";
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
      setPdfState("idle");
    } catch {
      setPdfState("error");
      setTimeout(() => setPdfState("idle"), 3500);
    }
  };

  return (
    <div className="space-y-6">
      {/* Hero — Data Intelligence Report (PDF) */}
      <button
        onClick={handlePdf}
        disabled={pdfState === "loading"}
        className="group relative w-full text-start rounded-2xl p-6 overflow-hidden
          border border-cyan/30 hover:border-cyan/60 transition-all disabled:cursor-wait
          bg-gradient-to-br from-[rgba(0,229,255,0.08)] to-[rgba(139,92,246,0.08)]"
      >
        <div className="relative z-10 flex items-center gap-5">
          <div className="w-14 h-14 rounded-2xl grid place-items-center shrink-0
            bg-gradient-to-br from-cyan to-mint text-[#03121a]">
            <svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="currentColor"
              strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
              <polyline points="14 2 14 8 20 8" />
              <line x1="16" y1="13" x2="8" y2="13" />
              <line x1="16" y1="17" x2="8" y2="17" />
            </svg>
          </div>
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2">
              <h3 className="font-bricolage font-bold text-lg text-text">{t("reportTitle")}</h3>
              <span className="text-[0.6rem] font-bold uppercase tracking-wide px-2 py-0.5 rounded
                text-mint bg-[rgba(0,255,178,0.12)]">PDF</span>
            </div>
            <p className="text-text-m text-sm mt-0.5">
              {t("reportDesc")}
            </p>
          </div>
          <span className="shrink-0 inline-flex items-center gap-2 px-4 py-2.5 rounded-xl text-sm font-semibold
            text-[#03121a] bg-gradient-to-br from-cyan to-mint group-hover:-translate-y-0.5 transition-transform">
            {pdfState === "loading" ? (
              <span className="w-4 h-4 border-2 border-[#03121a]/40 border-t-[#03121a] rounded-full animate-spin" />
            ) : (
              <DownloadIcon size={16} />
            )}
            {pdfState === "loading" ? t("generating") : pdfState === "error" ? t("retry") : t("generate")}
          </span>
        </div>
        {pdfState === "error" && (
          <p className="relative z-10 mt-3 text-xs text-amber">
            {t("waking")}
          </p>
        )}
      </button>

      {/* Raw data exports */}
      <div>
        <p className="text-[0.7rem] font-bold tracking-[0.15em] uppercase text-text-d mb-3">
          {t("rawExports")}
        </p>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          {formats.map((f) => (
            <a
              key={f.id}
              href={exportUrl(sessionId, f.id)}
              download
              className="group aura-card p-4 flex flex-col gap-1.5 hover:border-cyan/40 transition-colors text-start"
            >
              <div className="flex items-center justify-between">
                <span className="font-semibold text-text">{f.label}</span>
                <span className="text-text-d group-hover:text-cyan transition-colors"><DownloadIcon size={16} /></span>
              </div>
              <p className="text-text-m text-xs">{f.desc}</p>
            </a>
          ))}
        </div>
      </div>
    </div>
  );
}
