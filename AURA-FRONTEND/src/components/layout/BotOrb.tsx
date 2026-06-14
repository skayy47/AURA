"use client";
import { useTranslations } from "next-intl";
import { useStore } from "@/lib/store";
import { AuraBot } from "@/components/ai/AuraBot";
import { usePathname } from "@/i18n/navigation";
import { motion, AnimatePresence } from "framer-motion";
import { useState, useEffect } from "react";

export function BotOrb() {
  const t = useTranslations("bot");
  const pathname = usePathname();
  const firstRun = useStore((s) => s.firstRun);
  const meta = useStore((s) => s.meta);
  const cleanResult = useStore((s) => s.cleanResult);
  const exploreData = useStore((s) => s.exploreData);

  const [isOpen, setIsOpen] = useState(false);
  const [pulsing, setPulsing] = useState(false);

  useEffect(() => {
    if (firstRun && meta) {
      const timer = setTimeout(() => setIsOpen(false), 5000);
      return () => clearTimeout(timer);
    }
  }, [pathname, firstRun, meta]);

  useEffect(() => {
    setPulsing(true);
    const timer = setTimeout(() => setPulsing(false), 400);
    return () => clearTimeout(timer);
  }, [pathname]);

  if (pathname === "/ai-chat") return null;
  if (pathname === "/") return null;

  let state: "idle" | "listening" | "thinking" | "speaking" | "celebrate" | "error" = "idle";
  let tooltip = t("idle");

  if (pathname === "/ingest") {
    if (meta) {
      state = "idle";
      tooltip = firstRun
        ? t("ingestLoaded", { n: meta.missing_total })
        : t("ingestReady");
    } else {
      tooltip = t("ingestProcessing");
    }
  } else if (pathname === "/clean") {
    if (cleanResult) {
      state = "celebrate";
      tooltip = firstRun
        ? t("cleanDone", { score: 94 })
        : t("cleanReady", { score: 94 });
    } else {
      tooltip = firstRun
        ? t("cleanRunPrompt")
        : t("cleanRunning");
    }
  } else if (pathname === "/explore") {
    if (exploreData) {
      tooltip = firstRun
        ? t("exploreReady", {
            n: exploreData.profile.n_cols,
            corr: exploreData.profile.correlation?.top_pairs?.length || 0,
          })
        : t("exploreReady2");
    } else {
      state = "thinking";
      tooltip = t("exploreProfiling");
    }
  } else if (pathname === "/docs") {
    tooltip = t("docsReady");
  }

  return (
    <div className="fixed bottom-6 end-6 z-50 flex flex-col items-end gap-3">
      <AnimatePresence>
        {(isOpen || (firstRun && meta)) && (
          <motion.div
            initial={{ opacity: 0, scale: 0.9, y: 10 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.9, y: 10 }}
            className="bg-surface2 border border-border rounded-xl p-3 shadow-aura-lg max-w-[280px] relative"
          >
            <p className="text-sm text-text">{tooltip}</p>
            <div className="absolute end-4 -bottom-2 w-4 h-4 bg-surface2 border-r border-b border-border transform rotate-45" />
          </motion.div>
        )}
      </AnimatePresence>

      <motion.button
        layoutId="aura-bot-companion"
        onClick={() => setIsOpen(!isOpen)}
        animate={{ scale: pulsing ? 1.15 : 1.0, y: [0, -2, 0] }}
        transition={{ y: { repeat: Infinity, duration: 4, ease: "easeInOut" }, scale: { type: "spring" } }}
        className="w-12 h-12 rounded-full overflow-hidden relative cursor-pointer group flex-shrink-0"
      >
        <div className="absolute inset-0 rounded-full border border-border group-hover:border-purple/50 transition-colors z-10" />
        <div className="absolute -inset-4 bg-surface" />
        <div className="absolute inset-0 bg-surface flex items-start justify-center pt-1 overflow-hidden rounded-full">
          <div className="w-[120px] h-[120px] absolute -top-[14px]">
            <AuraBot size={120} state={state} />
          </div>
        </div>
        <div className="absolute -inset-[1px] rounded-full bg-gradient-to-r from-purple via-cyan to-blue opacity-0 group-hover:opacity-100 blur-[2px] transition-opacity -z-10" />
      </motion.button>
    </div>
  );
}
