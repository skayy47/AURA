"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { useTranslations } from "next-intl";
import { useRouter } from "@/i18n/navigation";
import { RobotStage } from "./RobotStage";
import { useStore } from "@/lib/store";
import { uploadFile } from "@/lib/api";
import { Sparkles } from "@/components/layout/pipeline-icons";
import type { BotState } from "@/components/ai/AuraBot";

export function HeroV5() {
  const t = useTranslations("landing");
  const tErrors = useTranslations("errors");
  const router = useRouter();

  const setIngest = useStore((s) => s.setIngest);
  const setSession = useStore((s) => s.setSession);
  const setFirstRun = useStore((s) => s.setFirstRun);

  const [botState, setBotState] = useState<BotState>("idle");
  const [demoError, setDemoError] = useState<string | null>(null);

  const handleDemo = async () => {
    setBotState("thinking");
    setDemoError(null);
    try {
      const csvRes = await fetch("/aura_demo.csv");
      if (!csvRes.ok) throw new Error("Demo CSV not found in public/");
      const blob = await csvRes.blob();
      const file = new File([blob], "aura_demo.csv", { type: "text/csv" });
      const result = await uploadFile(file);
      setSession(result.session_id);
      setIngest(result.meta, result.preview, result.warnings ?? []);
      setFirstRun(true);
      setBotState("celebrate");
      setTimeout(() => router.push("/ingest"), 1100);
    } catch {
      setBotState("error");
      setDemoError(tErrors("networkDown"));
      setTimeout(() => setBotState("idle"), 2500);
    }
  };

  return (
    <section className="relative w-full min-h-[calc(100vh-56px)] grid grid-cols-12 gap-6 items-center pt-6 pb-24">
      {/* Robot — col-start-1 on lg, full width above */}
      <div className="col-span-12 lg:col-span-5 lg:col-start-1 flex justify-center lg:justify-start">
        <div className="relative w-[280px] sm:w-[340px] lg:w-[380px] aspect-[2/3] -ml-2 lg:-ml-6">
          <RobotStage state={botState} size={380} />
        </div>
      </div>

      {/* Headline + CTAs — col-end-13 on lg, full width above */}
      <div className="col-span-12 lg:col-span-7 lg:col-start-6 flex flex-col items-start text-start gap-7">
        <motion.div
          initial={{ opacity: 0, x: -10 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.18, duration: 0.6 }}
          className="eyebrow-mono"
        >
          [01] · {t("byline")}
        </motion.div>

        <motion.h1
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.25, duration: 0.7, ease: [0.22, 0.9, 0.3, 1] }}
          className="heading-display text-text"
        >
          {t("heroLine1")} <br className="hidden md:inline" />
          <span className="text-aurora-gradient">{t("heroLine2")}</span>
        </motion.h1>

        <motion.p
          initial={{ opacity: 0, y: 18 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.45, duration: 0.6 }}
          className="text-text-m text-lg lg:text-xl max-w-[560px] leading-relaxed"
        >
          {t("sub")}
        </motion.p>

        <motion.div
          initial={{ opacity: 0, y: 18 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.6, duration: 0.5 }}
          className="flex flex-wrap items-center gap-3 pt-2"
        >
          <button
            onClick={handleDemo}
            disabled={botState === "thinking"}
            className="group relative inline-flex items-center gap-2 px-7 py-3.5 rounded-full font-medium text-sm
                       bg-gradient-to-r from-purple to-cyan text-white
                       hover:opacity-95 transition disabled:opacity-60 disabled:cursor-not-allowed
                       shadow-[0_0_30px_rgba(108,63,237,0.45)]"
          >
            <Sparkles size={16} className="group-hover:animate-pulse" />
            {botState === "thinking" ? t("loading") : t("cta")}
          </button>
          <button
            onClick={() => router.push("/ingest")}
            className="px-7 py-3.5 rounded-full font-medium text-sm border border-white/15
                       text-text-m hover:text-text hover:border-cyan/40 transition"
          >
            {t("ctaSecondary")}
          </button>
        </motion.div>

        <AnimatePresence>
          {demoError && (
            <motion.p
              key="demo-err"
              initial={{ opacity: 0, y: 6 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: 6 }}
              className="text-sm text-amber font-geist-mono"
            >
              {demoError}
            </motion.p>
          )}
        </AnimatePresence>

        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.85, duration: 0.6 }}
          className="flex items-center gap-4 pt-6 text-text-d"
        >
          <span className="eyebrow-mono">{t("heroTrustline")}</span>
        </motion.div>
      </div>
    </section>
  );
}
