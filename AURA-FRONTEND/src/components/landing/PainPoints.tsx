"use client";

import { motion } from "framer-motion";
import { useTranslations } from "next-intl";

export function PainPoints() {
  const t = useTranslations("landing");

  const points = [
    { plain: t("pain1Plain"), emphasis: t("pain1Emph") },
    { plain: t("pain2Plain"), emphasis: t("pain2Emph") },
    { plain: t("pain3Plain"), emphasis: t("pain3Emph") },
    { plain: t("pain4Plain"), emphasis: t("pain4Emph") },
  ];

  return (
    <section className="relative w-full max-w-5xl mx-auto px-6 py-32">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true, margin: "-100px" }}
        transition={{ duration: 0.5 }}
        className="mb-16"
      >
        <p className="eyebrow-mono mb-4">[02] · {t("painEyebrow")}</p>
        <h2 className="heading-display-lg text-text max-w-2xl">{t("painTitle")}</h2>
      </motion.div>

      <ul className="flex flex-col gap-12 lg:gap-14">
        {points.map((p, i) => (
          <motion.li
            key={i}
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, margin: "-80px" }}
            transition={{ delay: i * 0.08, duration: 0.55, ease: [0.22, 0.9, 0.3, 1] }}
            className="text-2xl md:text-3xl lg:text-[2.25rem] leading-snug font-bricolage tracking-tight text-text-m max-w-3xl"
          >
            {p.plain}
            <span className="text-text"> {p.emphasis}</span>
          </motion.li>
        ))}
      </ul>
    </section>
  );
}
