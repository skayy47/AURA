"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { useTranslations } from "next-intl";
import { useRouter } from "@/i18n/navigation";
import { useStore } from "@/lib/store";
import { Sparkles } from "@/components/layout/pipeline-icons";

const MESSY_ROWS = [
  { id: "001", customer: " Aïcha  Benali", date: "13/02/2026", amount: "129,90 MAD", status: "shipped" },
  { id: "001", customer: "Aïcha Benali",   date: "13/02/2026", amount: "129,90",     status: "Shipped" },
  { id: "002", customer: "Yousef AlAmin",  date: "2026-02-14", amount: "329 SAR",    status: "" },
  { id: "003", customer: "lara hadid",     date: "n/a",        amount: "—",          status: "pending" },
  { id: "004", customer: "Omar Said   ",   date: "15-feb-26",  amount: "189.50",     status: "Delivered" },
];

const CLEAN_ROWS = [
  { id: "001", customer: "Aïcha Benali",  date: "2026-02-13", amount: 129.90, status: "shipped"   },
  { id: "002", customer: "Yousef Al Amin",date: "2026-02-14", amount: 329.00, status: "pending"   },
  { id: "003", customer: "Lara Hadid",    date: null,         amount: null,   status: "pending"   },
  { id: "004", customer: "Omar Said",     date: "2026-02-15", amount: 189.50, status: "delivered" },
];

const CLEAN_LOG_KEYS = [
  { tag: "[01]", key: "cleanLog1" },
  { tag: "[02]", key: "cleanLog2" },
  { tag: "[03]", key: "cleanLog3" },
  { tag: "[04]", key: "cleanLog4" },
  { tag: "[05]", key: "cleanLog5" },
] as const;

export function LiveDemoStrip() {
  const t = useTranslations("landing");
  const router = useRouter();
  const setIngest = useStore((s) => s.setIngest);
  const setSession = useStore((s) => s.setSession);
  const setFirstRun = useStore((s) => s.setFirstRun);

  const [phase, setPhase] = useState<"messy" | "running" | "clean">("messy");
  const [loadingReal, setLoadingReal] = useState(false);

  const playPreview = () => {
    setPhase("running");
    setTimeout(() => setPhase("clean"), 1500);
  };

  const reset = () => setPhase("messy");

  const launchReal = async () => {
    setLoadingReal(true);
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
      const res = await fetch(`${apiUrl}/api/samples/mena-retail-raw/load`, { method: "POST" });
      if (!res.ok) throw new Error();
      const result = await res.json();
      setSession(result.session_id);
      setIngest(result.meta, result.preview, result.warnings ?? []);
      setFirstRun(true);
      router.push("/ingest");
    } catch {
      setLoadingReal(false);
    }
  };

  return (
    <section className="relative w-full max-w-6xl mx-auto px-6 py-24">
      <motion.div
        initial={{ opacity: 0, y: 16 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true, margin: "-100px" }}
        transition={{ duration: 0.5 }}
        className="text-center mb-12"
      >
        <p className="eyebrow-mono mb-3">[03] · {t("demoEyebrow")}</p>
        <h2 className="heading-display-lg text-text mb-4">{t("demoTitle")}</h2>
        <p className="text-text-m max-w-2xl mx-auto">{t("demoSub")}</p>
      </motion.div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-5 lg:gap-6 relative">
        {/* Messy panel */}
        <DemoPanel
          label={t("demoMessyLabel")}
          dimmed={phase === "clean"}
          highlight={phase === "messy" || phase === "running"}
        >
          <table className="w-full font-geist-mono text-[0.72rem]">
            <thead>
              <tr className="text-text-d">
                <th className="text-start py-2 px-2 font-medium">id</th>
                <th className="text-start py-2 px-2 font-medium">customer</th>
                <th className="text-start py-2 px-2 font-medium">date</th>
                <th className="text-start py-2 px-2 font-medium">amount</th>
                <th className="text-start py-2 px-2 font-medium">status</th>
              </tr>
            </thead>
            <tbody>
              {MESSY_ROWS.map((r, i) => (
                <tr key={i} className="border-t border-white/[0.04] text-text-m">
                  <td className="py-2 px-2">{r.id}</td>
                  <td className="py-2 px-2 text-amber">{r.customer || "—"}</td>
                  <td className="py-2 px-2 text-amber">{r.date || "—"}</td>
                  <td className="py-2 px-2 text-amber">{r.amount}</td>
                  <td className="py-2 px-2">{r.status || <span className="text-text-d">∅</span>}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </DemoPanel>

        {/* Clean panel */}
        <DemoPanel
          label={t("demoCleanLabel")}
          dimmed={phase === "messy"}
          highlight={phase === "clean"}
        >
          <table className="w-full font-geist-mono text-[0.72rem]">
            <thead>
              <tr className="text-text-d">
                <th className="text-start py-2 px-2 font-medium">id</th>
                <th className="text-start py-2 px-2 font-medium">customer</th>
                <th className="text-start py-2 px-2 font-medium">date</th>
                <th className="text-start py-2 px-2 font-medium">amount</th>
                <th className="text-start py-2 px-2 font-medium">status</th>
              </tr>
            </thead>
            <tbody>
              <AnimatePresence>
                {(phase === "clean" ? CLEAN_ROWS : []).map((r, i) => (
                  <motion.tr
                    key={r.id}
                    initial={{ opacity: 0, x: -8 }}
                    animate={{ opacity: 1, x: 0 }}
                    exit={{ opacity: 0 }}
                    transition={{ delay: i * 0.06 }}
                    className="border-t border-white/[0.04] text-text"
                  >
                    <td className="py-2 px-2 text-cyan">{r.id}</td>
                    <td className="py-2 px-2">{r.customer}</td>
                    <td className="py-2 px-2">{r.date ?? <span className="text-text-d">null</span>}</td>
                    <td className="py-2 px-2">{r.amount?.toFixed(2) ?? <span className="text-text-d">null</span>}</td>
                    <td className="py-2 px-2 text-green">{r.status}</td>
                  </motion.tr>
                ))}
                {phase === "messy" && (
                  <motion.tr key="placeholder" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
                    <td colSpan={5} className="py-12 px-2 text-center text-text-d text-xs uppercase tracking-widest">
                      {t("demoIdle")}
                    </td>
                  </motion.tr>
                )}
                {phase === "running" && (
                  <motion.tr key="running" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
                    <td colSpan={5} className="py-12 px-2 text-center text-cyan text-xs uppercase tracking-widest animate-pulse">
                      {t("demoRunning")}
                    </td>
                  </motion.tr>
                )}
              </AnimatePresence>
            </tbody>
          </table>
        </DemoPanel>
      </div>

      {/* Action row */}
      <div className="flex flex-col sm:flex-row items-center justify-center gap-4 mt-10">
        {phase !== "clean" ? (
          <button
            onClick={playPreview}
            disabled={phase === "running"}
            className="inline-flex items-center gap-2 px-6 py-3 rounded-full text-sm font-medium
                       bg-gradient-to-r from-purple to-cyan text-white shadow-[0_0_24px_rgba(108,63,237,0.4)]
                       hover:opacity-95 transition disabled:opacity-60 disabled:cursor-not-allowed"
          >
            <Sparkles size={16} />
            {phase === "running" ? t("demoRunningCta") : t("demoCleanItCta")}
          </button>
        ) : (
          <>
            <button
              onClick={launchReal}
              disabled={loadingReal}
              className="inline-flex items-center gap-2 px-6 py-3 rounded-full text-sm font-medium
                         bg-gradient-to-r from-purple to-cyan text-white shadow-[0_0_24px_rgba(108,63,237,0.4)]
                         hover:opacity-95 transition disabled:opacity-60 disabled:cursor-not-allowed"
            >
              <Sparkles size={16} />
              {loadingReal ? t("loading") : t("demoLaunchReal")}
            </button>
            <button onClick={reset} className="text-sm text-text-d hover:text-text-m transition underline-offset-4 hover:underline">
              {t("demoReset")}
            </button>
          </>
        )}
      </div>

      {/* Cleaning log — appears only after clean */}
      <AnimatePresence>
        {phase === "clean" && (
          <motion.ul
            initial={{ opacity: 0, y: 14 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0 }}
            transition={{ delay: 0.2, duration: 0.4 }}
            className="mt-10 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-3 max-w-5xl mx-auto"
          >
            {CLEAN_LOG_KEYS.map((step, i) => (
              <motion.li
                key={i}
                initial={{ opacity: 0, y: 8 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.25 + i * 0.06 }}
                className="font-geist-mono text-[0.7rem] text-text-m px-3 py-2 rounded-md border border-white/[0.06] bg-surface/40"
              >
                <span className="text-cyan">{step.tag}</span> {t(step.key)}
              </motion.li>
            ))}
          </motion.ul>
        )}
      </AnimatePresence>
    </section>
  );
}

function DemoPanel({
  label,
  dimmed,
  highlight,
  children,
}: {
  label: string;
  dimmed: boolean;
  highlight: boolean;
  children: React.ReactNode;
}) {
  return (
    <motion.div
      animate={{ opacity: dimmed ? 0.45 : 1, scale: highlight ? 1 : 0.985 }}
      transition={{ duration: 0.35 }}
      className={`relative rounded-2xl border ${
        highlight ? "border-cyan/40 shadow-[0_0_28px_rgba(34,211,238,0.18)]" : "border-white/[0.06]"
      } bg-[rgba(7,12,26,0.7)] backdrop-blur-md overflow-hidden`}
    >
      <div className="flex items-center gap-2 px-4 py-2.5 border-b border-white/[0.05]">
        <span className="w-2 h-2 rounded-full bg-amber/70" />
        <span className="w-2 h-2 rounded-full bg-purple/70" />
        <span className="w-2 h-2 rounded-full bg-cyan/70" />
        <span className="ml-3 eyebrow-mono">{label}</span>
      </div>
      <div className="p-3">{children}</div>
    </motion.div>
  );
}
