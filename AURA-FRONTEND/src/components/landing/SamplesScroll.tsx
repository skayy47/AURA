"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { useTranslations } from "next-intl";
import { useRouter } from "@/i18n/navigation";
import { useStore } from "@/lib/store";

const SAMPLES = [
  {
    n: "01",
    slug: "sales-mess",
    accent: "from-amber to-purple",
    rows: 40,
    cols: 11,
    nameKey: "samplesSalesName",
    descKey: "samplesSalesDesc",
    breakKey: "samplesSalesBreak",
    tags: ["duplicates", "outliers", "nulls"],
  },
  {
    n: "02",
    slug: "climate-sensors",
    accent: "from-purple to-cyan",
    rows: 44,
    cols: 12,
    nameKey: "samplesClimateName",
    descKey: "samplesClimateDesc",
    breakKey: "samplesClimateBreak",
    tags: ["time-series", "MENA", "sensors"],
  },
  {
    n: "03",
    slug: "mena-orders",
    accent: "from-cyan to-blue",
    rows: 50,
    cols: 13,
    nameKey: "samplesMenaName",
    descKey: "samplesMenaDesc",
    breakKey: "samplesMenaBreak",
    tags: ["e-commerce", "MENA", "clean"],
  },
] as const;

export function SamplesScroll() {
  const t = useTranslations("landing");
  const router = useRouter();
  const setIngest = useStore((s) => s.setIngest);
  const setSession = useStore((s) => s.setSession);
  const setFirstRun = useStore((s) => s.setFirstRun);
  const [loading, setLoading] = useState<string | null>(null);

  const load = async (slug: string) => {
    setLoading(slug);
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
      const res = await fetch(`${apiUrl}/api/samples/${slug}/load`, { method: "POST" });
      if (!res.ok) throw new Error();
      const result = await res.json();
      setSession(result.session_id);
      setIngest(result.meta, result.preview, result.warnings ?? []);
      setFirstRun(true);
      router.push("/ingest");
    } catch {
      setLoading(null);
    }
  };

  return (
    <section className="relative w-full max-w-6xl mx-auto px-6 py-24">
      <motion.div
        initial={{ opacity: 0, y: 16 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true, margin: "-100px" }}
        transition={{ duration: 0.5 }}
        className="flex flex-col md:flex-row md:items-end md:justify-between gap-6 mb-12"
      >
        <div>
          <p className="eyebrow-mono mb-3">[05] · {t("samplesEyebrow")}</p>
          <h2 className="heading-display-lg text-text max-w-xl">{t("samplesV5Title")}</h2>
        </div>
        <p className="text-text-m max-w-md">{t("samplesV5Sub")}</p>
      </motion.div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
        {SAMPLES.map((s, i) => (
          <motion.article
            key={s.slug}
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, margin: "-60px" }}
            transition={{ delay: i * 0.08, duration: 0.5 }}
            className="bento-card p-6 flex flex-col h-full group"
          >
            <div className="flex items-center justify-between mb-5">
              <span className="eyebrow-mono text-text">[{s.n}]</span>
              <span className={`text-[0.65rem] font-mono px-2 py-0.5 rounded-full bg-gradient-to-r ${s.accent} text-white opacity-90`}>
                {t("samplesStressBadge")}
              </span>
            </div>

            <h3 className="font-bricolage font-bold text-text text-xl mb-2">{t(s.nameKey)}</h3>
            <p className="text-text-m text-sm mb-4 leading-relaxed">{t(s.descKey)}</p>

            <div className="font-geist-mono text-[0.7rem] text-text-d mb-4 flex items-center gap-2">
              <span>{s.rows} rows</span>
              <span>·</span>
              <span>{s.cols} cols</span>
            </div>

            <div className="flex flex-wrap gap-1.5 mb-5">
              {s.tags.map((tag) => (
                <span key={tag} className="text-[0.6rem] px-2 py-0.5 rounded-full border border-white/[0.08] text-text-d uppercase tracking-wider">
                  {tag}
                </span>
              ))}
            </div>

            <div className="mt-auto">
              <p className="text-[0.7rem] text-cyan/80 font-geist-mono mb-3">↳ {t(s.breakKey)}</p>
              <button
                onClick={() => load(s.slug)}
                disabled={loading === s.slug}
                className="w-full py-2.5 rounded-full text-sm font-medium border border-white/10 text-text-m
                           hover:text-text hover:border-cyan/40 transition disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {loading === s.slug ? t("samplesLoading") : t("samplesLoad")}
              </button>
            </div>
          </motion.article>
        ))}
      </div>
    </section>
  );
}
