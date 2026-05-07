"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { useTranslations } from "next-intl";
import { useRouter } from "@/i18n/navigation";
import { useStore } from "@/lib/store";
import { uploadFile } from "@/lib/api";
import { Sparkles } from "@/components/layout/pipeline-icons";

export function FinalCTA() {
  const t = useTranslations("landing");
  const tErrors = useTranslations("errors");
  const router = useRouter();
  const setIngest = useStore((s) => s.setIngest);
  const setSession = useStore((s) => s.setSession);
  const setFirstRun = useStore((s) => s.setFirstRun);

  const [loading, setLoading] = useState(false);
  const [err, setErr] = useState<string | null>(null);

  const handle = async () => {
    setLoading(true);
    setErr(null);
    try {
      const csvRes = await fetch("/aura_demo.csv");
      if (!csvRes.ok) throw new Error();
      const blob = await csvRes.blob();
      const file = new File([blob], "aura_demo.csv", { type: "text/csv" });
      const result = await uploadFile(file);
      setSession(result.session_id);
      setIngest(result.meta, result.preview, result.warnings ?? []);
      setFirstRun(true);
      router.push("/ingest");
    } catch {
      setErr(tErrors("networkDown"));
      setLoading(false);
    }
  };

  return (
    <section className="relative w-full max-w-6xl mx-auto px-6 py-24">
      <motion.div
        initial={{ opacity: 0, y: 24 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true, margin: "-100px" }}
        transition={{ duration: 0.55 }}
        className="relative overflow-hidden rounded-3xl border border-purple/40
                   bg-gradient-to-br from-[rgba(108,63,237,0.18)] via-[rgba(34,211,238,0.10)] to-[rgba(59,130,246,0.18)]
                   px-8 py-14 lg:py-20 text-center"
      >
        {/* Aurora blobs inside the panel */}
        <div className="absolute -top-1/2 -start-1/4 w-[60%] h-[140%] rounded-full bg-purple/30 blur-[120px] pointer-events-none" />
        <div className="absolute -bottom-1/2 -end-1/4 w-[55%] h-[140%] rounded-full bg-cyan/25 blur-[120px] pointer-events-none" />

        <div className="relative z-10 max-w-3xl mx-auto">
          <p className="eyebrow-mono mb-4">[09] · {t("ctaEyebrow")}</p>
          <h2 className="heading-display text-text mb-5">{t("finalCtaTitle")}</h2>
          <p className="text-text-m text-lg mb-8 max-w-xl mx-auto leading-relaxed">{t("finalCtaSub")}</p>

          <button
            onClick={handle}
            disabled={loading}
            className="inline-flex items-center gap-2 px-8 py-4 rounded-full font-medium
                       bg-gradient-to-r from-purple to-cyan text-white shadow-[0_0_40px_rgba(108,63,237,0.55)]
                       hover:opacity-95 transition disabled:opacity-60 disabled:cursor-not-allowed"
          >
            <Sparkles size={18} />
            {loading ? t("loading") : t("finalCtaButton")}
          </button>

          {err && <p className="mt-5 text-sm text-amber font-geist-mono">{err}</p>}

          <p className="mt-6 text-xs text-text-d font-geist-mono uppercase tracking-widest">
            {t("finalCtaMicro")}
          </p>
        </div>
      </motion.div>
    </section>
  );
}
