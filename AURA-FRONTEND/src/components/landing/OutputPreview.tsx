"use client";

import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { useTranslations } from "next-intl";

export function OutputPreview() {
  const t = useTranslations("landing");

  return (
    <section className="relative w-full max-w-6xl mx-auto px-6 py-24">
      <motion.div
        initial={{ opacity: 0, y: 16 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true, margin: "-100px" }}
        transition={{ duration: 0.5 }}
        className="text-center mb-14"
      >
        <p className="eyebrow-mono mb-3">[06] · {t("outputEyebrow")}</p>
        <h2 className="heading-display-lg text-text mb-3">{t("outputTitle")}</h2>
        <p className="text-text-m max-w-2xl mx-auto">{t("outputSub")}</p>
      </motion.div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
        <ArtifactCard
          n="A"
          title={t("outputCsvTitle")}
          body={t("outputCsvBody")}
          accent="cyan"
          delay={0}
        >
          <CsvMockup />
        </ArtifactCard>
        <ArtifactCard
          n="B"
          title={t("outputAiTitle")}
          body={t("outputAiBody")}
          accent="purple"
          delay={0.1}
        >
          <ChatMockup question={t("outputAiQ")} answer={t("outputAiA")} />
        </ArtifactCard>
        <ArtifactCard
          n="C"
          title={t("outputPdfTitle")}
          body={t("outputPdfBody")}
          accent="blue"
          delay={0.2}
        >
          <PdfMockup label={t("outputPdfLabel")} />
        </ArtifactCard>
      </div>
    </section>
  );
}

function ArtifactCard({
  n, title, body, accent, delay, children,
}: {
  n: string;
  title: string;
  body: string;
  accent: "cyan" | "purple" | "blue";
  delay: number;
  children: React.ReactNode;
}) {
  const ring =
    accent === "cyan" ? "shadow-[0_0_36px_-8px_rgba(34,211,238,0.35)]" :
    accent === "purple" ? "shadow-[0_0_36px_-8px_rgba(108,63,237,0.4)]" :
    "shadow-[0_0_36px_-8px_rgba(59,130,246,0.35)]";

  return (
    <motion.article
      initial={{ opacity: 0, y: 20 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, margin: "-60px" }}
      transition={{ delay, duration: 0.5 }}
      className={`bento-card p-6 flex flex-col gap-4 ${ring}`}
    >
      <div className="flex items-center justify-between">
        <span className="eyebrow-mono">{n}</span>
        <span className={`w-2.5 h-2.5 rounded-full bg-${accent}`} />
      </div>
      <div className="rounded-lg overflow-hidden border border-white/[0.05] bg-[rgba(7,12,26,0.7)] aspect-[16/10] flex">
        {children}
      </div>
      <div>
        <h3 className="font-bricolage font-bold text-text text-lg mb-1">{title}</h3>
        <p className="text-text-m text-sm leading-relaxed">{body}</p>
      </div>
    </motion.article>
  );
}

function CsvMockup() {
  const lines = [
    "id,customer,date,amount,status",
    "001,Aïcha Benali,2026-02-13,129.90,shipped",
    "002,Yousef Al Amin,2026-02-14,329.00,pending",
    "003,Lara Hadid,,,pending",
    "004,Omar Said,2026-02-15,189.50,delivered",
  ];
  return (
    <div className="font-geist-mono text-[0.65rem] p-3 leading-relaxed w-full overflow-hidden">
      {lines.map((l, i) => (
        <motion.div
          key={i}
          initial={{ opacity: 0, x: -6 }}
          whileInView={{ opacity: 1, x: 0 }}
          viewport={{ once: true }}
          transition={{ delay: 0.1 + i * 0.07 }}
          className={i === 0 ? "text-cyan" : "text-text-m"}
        >
          {l}
        </motion.div>
      ))}
    </div>
  );
}

function ChatMockup({ question, answer }: { question: string; answer: string }) {
  const [shownChars, setShownChars] = useState(0);
  const [started, setStarted] = useState(false);

  useEffect(() => {
    if (!started) return;
    if (shownChars >= answer.length) return;
    const t = setTimeout(() => setShownChars((c) => c + 1), 22);
    return () => clearTimeout(t);
  }, [shownChars, answer.length, started]);

  return (
    <motion.div
      onViewportEnter={() => setStarted(true)}
      viewport={{ once: true }}
      className="w-full p-3 flex flex-col gap-2 text-[0.7rem]"
    >
      <div className="self-end max-w-[90%] px-2.5 py-1.5 rounded-lg rounded-tr-none bg-gradient-to-br from-purple to-blue text-white">
        {question}
      </div>
      <div className="self-start max-w-[95%] px-2.5 py-1.5 rounded-lg rounded-tl-none bg-surface2 border border-white/5 text-text">
        {answer.slice(0, shownChars)}
        {shownChars < answer.length && <span className="inline-block w-1.5 h-3 bg-cyan ml-0.5 align-middle animate-pulse" />}
      </div>
    </motion.div>
  );
}

function PdfMockup({ label }: { label: string }) {
  return (
    <div className="w-full h-full p-4 flex flex-col">
      <div className="flex items-center justify-between mb-3">
        <span className="font-bricolage font-bold text-text text-sm">{label}</span>
        <span className="eyebrow-mono">PDF</span>
      </div>
      <div className="flex-1 grid grid-cols-2 gap-2">
        <div className="rounded bg-gradient-to-br from-purple/30 to-cyan/20 border border-white/5 flex items-end justify-around p-1">
          {[30, 50, 38, 65, 48, 72].map((h, i) => (
            <div key={i} className="w-1.5 rounded-t bg-cyan" style={{ height: `${h}%` }} />
          ))}
        </div>
        <div className="rounded bg-gradient-to-br from-blue/20 to-purple/20 border border-white/5 relative overflow-hidden">
          <svg viewBox="0 0 100 60" className="w-full h-full">
            <path d="M0 50 L20 38 L40 42 L60 22 L80 30 L100 12" fill="none" stroke="#22d3ee" strokeWidth="1.5" />
          </svg>
        </div>
        <div className="col-span-2 h-1.5 rounded bg-white/10" />
        <div className="col-span-2 flex gap-1">
          <div className="h-1.5 flex-1 rounded bg-white/8" />
          <div className="h-1.5 flex-1 rounded bg-white/8" />
          <div className="h-1.5 flex-1 rounded bg-white/8" />
        </div>
      </div>
    </div>
  );
}
