"use client";

import { motion } from "framer-motion";
import { useTranslations } from "next-intl";
import { Upload, Sparkles, Bot, CheckCircle } from "@/components/layout/pipeline-icons";

export function BentoSteps() {
  const t = useTranslations("landing");

  return (
    <section className="relative w-full max-w-6xl mx-auto px-6 py-24">
      <motion.div
        initial={{ opacity: 0, y: 18 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true, margin: "-100px" }}
        transition={{ duration: 0.55 }}
        className="text-center mb-14"
      >
        <p className="eyebrow-mono mb-3">[04] · {t("howEyebrow")}</p>
        <h2 className="heading-display-lg text-text mb-3">{t("howTitle")}</h2>
        <p className="text-text-m">{t("howSub")}</p>
      </motion.div>

      {/* Bento grid: 2 small left, 1 large center, 2 small right (lg) */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 lg:grid-rows-2 gap-4">
        <BentoCell
          n="01"
          icon={<Upload size={18} />}
          title={t("how1Title")}
          body={t("how1Body")}
          className="lg:col-span-1 lg:row-span-1"
          delay={0}
        />
        <BentoCell
          n="02"
          icon={<Sparkles size={18} />}
          title={t("how2Title")}
          body={t("how2Body")}
          className="lg:col-span-1 lg:row-span-1"
          delay={0.08}
        />
        <BentoCell
          n="03"
          icon={<Sparkles size={18} />}
          title={t("how3Title")}
          body={t("how3Body")}
          className="lg:col-span-2 lg:row-span-2"
          delay={0.16}
          large
        />
        <BentoCell
          n="04"
          icon={<Bot size={18} />}
          title={t("how4Title")}
          body={t("how4Body")}
          className="lg:col-span-1 lg:row-span-1"
          delay={0.24}
        />
        <BentoCell
          n="05"
          icon={<CheckCircle size={18} />}
          title={t("how5Title")}
          body={t("how5Body")}
          className="lg:col-span-1 lg:row-span-1"
          delay={0.32}
        />
      </div>
    </section>
  );
}

function BentoCell({
  n,
  icon,
  title,
  body,
  className = "",
  delay = 0,
  large = false,
}: {
  n: string;
  icon: React.ReactNode;
  title: string;
  body: string;
  className?: string;
  delay?: number;
  large?: boolean;
}) {
  const handleMouse = (e: React.MouseEvent<HTMLDivElement>) => {
    const rect = e.currentTarget.getBoundingClientRect();
    e.currentTarget.style.setProperty("--mx", `${e.clientX - rect.left}px`);
    e.currentTarget.style.setProperty("--my", `${e.clientY - rect.top}px`);
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 18 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, margin: "-60px" }}
      transition={{ delay, duration: 0.5 }}
      onMouseMove={handleMouse}
      className={`bento-card p-6 ${large ? "lg:p-8" : ""} ${className}`}
    >
      <div className="flex items-start justify-between gap-3 mb-6">
        <span className="eyebrow-mono">[{n}]</span>
        <span className="w-9 h-9 rounded-full bg-purple/10 border border-purple/30 text-cyan flex items-center justify-center">
          {icon}
        </span>
      </div>
      <h3 className={`font-bricolage font-bold text-text mb-2 ${large ? "text-3xl lg:text-4xl" : "text-xl"}`}>
        {title}
      </h3>
      <p className={`text-text-m leading-relaxed ${large ? "text-base" : "text-sm"}`}>{body}</p>

      {large && (
        <div className="mt-8 relative h-32 rounded-xl border border-white/[0.05] bg-[rgba(7,12,26,0.7)] overflow-hidden">
          <div className="absolute inset-0 flex items-end justify-around px-4 pb-3">
            {[24, 38, 52, 31, 67, 49, 73, 58, 81, 64].map((h, i) => (
              <motion.div
                key={i}
                initial={{ height: 0 }}
                whileInView={{ height: `${h}%` }}
                viewport={{ once: true }}
                transition={{ delay: 0.5 + i * 0.05, duration: 0.5 }}
                className="w-3 rounded-t bg-gradient-to-t from-purple to-cyan"
              />
            ))}
          </div>
          <div className="absolute top-3 start-4 eyebrow-mono">distribution · age</div>
        </div>
      )}
    </motion.div>
  );
}
