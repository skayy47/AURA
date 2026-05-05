"use client";

import { useTranslations } from "next-intl";
import { AuraBot } from "@/components/ai/AuraBot";
import { DataConstellation } from "@/components/ai/DataConstellation";
import { GlowCard } from "@/components/ui/GlowCard";
import { Upload, Sparkles, Bot } from "@/components/layout/pipeline-icons";
import { useRouter } from "@/i18n/navigation";
import { useState } from "react";
import { useStore } from "@/lib/store";
import { uploadFile } from "@/lib/api";
import { motion, AnimatePresence } from "framer-motion";

export default function LandingPage() {
  const t = useTranslations("landing");
  const tErrors = useTranslations("errors");
  const router = useRouter();
  const setIngest  = useStore((s) => s.setIngest);
  const setSession = useStore((s) => s.setSession);
  const setFirstRun = useStore((s) => s.setFirstRun);

  const [botState, setBotState] = useState<"idle" | "thinking" | "celebrate" | "error">("idle");
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
      setTimeout(() => router.push("/clean"), 1200);
    } catch {
      setBotState("error");
      setDemoError(tErrors("networkDown"));
      setTimeout(() => setBotState("idle"), 2500);
    }
  };

  return (
    <div className="flex flex-col items-center">
      {/* Hero — full viewport height minus TopBar, content centred */}
      <section className="flex flex-col items-center text-center w-full max-w-3xl min-h-[calc(100vh-56px)] justify-center pb-12">

        <div className="w-[320px] h-[320px] mb-10 relative flex items-center justify-center">
          {/* Data constellation — orbiting particles behind the bot */}
          <DataConstellation className="absolute inset-0 w-full h-full" />

          {/* Thinking ring */}
          {botState === "thinking" && (
            <motion.div
              className="absolute -inset-4 rounded-full border-2 border-dashed border-cyan/50"
              animate={{ rotate: 360 }}
              transition={{ duration: 4, repeat: Infinity, ease: "linear" }}
            />
          )}

          <AuraBot size={320} state={botState} />
        </div>

        <h1 className="font-brand text-5xl md:text-6xl text-text mb-6 tracking-tight leading-tight">
          {t("hero")}
        </h1>

        <p className="text-text-m text-lg max-w-[520px] mb-10 leading-relaxed">
          {t("sub")}
        </p>

        <div className="flex items-center gap-6">
          <button
            onClick={handleDemo}
            disabled={botState === "thinking"}
            className="group relative px-8 py-3 rounded-full bg-surface2 font-medium text-text border border-purple hover:border-cyan transition-all overflow-hidden disabled:opacity-60 disabled:cursor-not-allowed"
          >
            <div className="absolute inset-0 bg-gradient-to-r from-purple/20 to-cyan/20 opacity-0 group-hover:opacity-100 transition-opacity" />
            <span className="relative z-10 flex items-center gap-2">
              <Sparkles size={18} className="text-cyan group-hover:animate-pulse" />
              {botState === "thinking" ? t("loading") : t("cta")}
            </span>
          </button>

          <button
            onClick={() => router.push("/ingest")}
            className="group relative px-8 py-3 rounded-full bg-transparent font-medium text-text-m hover:text-text border border-border hover:border-text-d transition-colors"
          >
            {t("ctaSecondary")}
          </button>
        </div>

        <AnimatePresence>
          {demoError && (
            <motion.p
              key="demo-err"
              initial={{ opacity: 0, y: 6 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: 6 }}
              className="mt-5 text-sm text-amber font-geist-mono"
            >
              {demoError}
            </motion.p>
          )}
        </AnimatePresence>

        <div className="mt-14 text-xs uppercase tracking-widest bg-gradient-to-r from-purple-l via-cyan to-blue bg-clip-text text-transparent">
          {t("byline")}
        </div>
      </section>

      <section className="grid grid-cols-1 md:grid-cols-3 gap-6 w-full max-w-5xl pb-16">
        <motion.div initial={{ opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }} transition={{ delay: 0.1 }}>
          <GlowCard accent="cyan" intensity="low" className="h-full">
            <div className="bg-[#0A1022] w-12 h-12 rounded-full flex items-center justify-center mb-6 border border-cyan/30 text-cyan">
              <Upload size={20} />
            </div>
            <h3 className="font-brand text-lg text-text mb-3">{t("smartIngestion")}</h3>
            <p className="text-text-m text-sm leading-relaxed">{t("smartIngestionBody")}</p>
          </GlowCard>
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }} transition={{ delay: 0.2 }}>
          <GlowCard accent="purple" intensity="low" className="h-full">
            <div className="bg-[#0A1022] w-12 h-12 rounded-full flex items-center justify-center mb-6 border border-purple/30 text-purple">
              <Sparkles size={20} />
            </div>
            <h3 className="font-brand text-lg text-text mb-3">{t("automatedCleaning")}</h3>
            <p className="text-text-m text-sm leading-relaxed">{t("automatedCleaningBody")}</p>
          </GlowCard>
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }} transition={{ delay: 0.3 }}>
          <GlowCard accent="blue" intensity="low" className="h-full">
            <div className="bg-[#0A1022] w-12 h-12 rounded-full flex items-center justify-center mb-6 border border-blue/30 text-blue">
              <Bot size={20} />
            </div>
            <h3 className="font-brand text-lg text-text mb-3">{t("aiAnalysis")}</h3>
            <p className="text-text-m text-sm leading-relaxed">{t("aiAnalysisBody")}</p>
          </GlowCard>
        </motion.div>
      </section>
    </div>
  );
}
