"use client";

import { motion } from "framer-motion";
import { useTranslations } from "next-intl";

interface Tier {
  name: string;
  price: string;
  period: string;
  desc: string;
  cta: string;
  features: string[];
  save: string;
  highlighted?: boolean;
}

export function PricingV5() {
  const t = useTranslations("landing");

  const tiers: Tier[] = [
    {
      name: t("pricingFreeName"), price: t("pricingFreePrice"), period: t("pricingFreePeriod"),
      desc: t("pricingFreeDesc"), cta: t("pricingFreeCta"),
      features: [t("pricingFreeF1"), t("pricingFreeF2"), t("pricingFreeF3"), t("pricingFreeF4")],
      save: t("pricingFreeSave"),
    },
    {
      name: t("pricingProName"), price: t("pricingProPrice"), period: t("pricingProPeriod"),
      desc: t("pricingProDesc"), cta: t("pricingProCta"),
      features: [t("pricingProF1"), t("pricingProF2"), t("pricingProF3"), t("pricingProF4"), t("pricingProF5")],
      save: t("pricingProSave"),
      highlighted: true,
    },
    {
      name: t("pricingTeamName"), price: t("pricingTeamPrice"), period: t("pricingTeamPeriod"),
      desc: t("pricingTeamDesc"), cta: t("pricingTeamCta"),
      features: [t("pricingTeamF1"), t("pricingTeamF2"), t("pricingTeamF3"), t("pricingTeamF4"), t("pricingTeamF5")],
      save: t("pricingTeamSave"),
    },
  ];

  return (
    <section className="relative w-full max-w-6xl mx-auto px-6 py-24">
      <motion.div
        initial={{ opacity: 0, y: 16 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true, margin: "-100px" }}
        transition={{ duration: 0.5 }}
        className="text-center mb-14"
      >
        <p className="eyebrow-mono mb-3">[08] · {t("pricingEyebrow")}</p>
        <h2 className="heading-display-lg text-text mb-3">{t("pricingTitle")}</h2>
        <p className="text-text-m">{t("pricingSub")}</p>
      </motion.div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-5 items-stretch">
        {tiers.map((tier, i) => (
          <motion.div
            key={i}
            initial={{ opacity: 0, y: 24 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, margin: "-60px" }}
            transition={{ delay: i * 0.08, duration: 0.5 }}
            className={`relative rounded-2xl p-6 lg:p-7 flex flex-col gap-5 border transition
              ${tier.highlighted
                ? "border-purple/60 bg-gradient-to-b from-purple/15 to-transparent shadow-[0_0_50px_-12px_rgba(108,63,237,0.55)] -translate-y-1.5"
                : "border-white/[0.07] bg-[rgba(7,12,26,0.55)]"}`}
          >
            {tier.highlighted && (
              <div className="absolute -top-3 start-1/2 -translate-x-1/2 px-3 py-1 rounded-full text-[0.6rem] font-bold tracking-widest uppercase pulse-pill text-white">
                {t("pricingMostPopular")}
              </div>
            )}

            <div>
              <p className="eyebrow-mono mb-2">{tier.name}</p>
              <div className="flex items-baseline gap-1.5">
                <span className="text-4xl font-bold font-bricolage text-text">{tier.price}</span>
                <span className="text-text-d text-sm">{tier.period}</span>
              </div>
              <p className="text-text-m text-xs mt-1.5">{tier.desc}</p>
            </div>

            <ul className="flex flex-col gap-2.5 flex-1">
              {tier.features.map((f, j) => (
                <li key={j} className="flex items-start gap-2 text-sm text-text-m">
                  <span className="mt-1.5 w-1.5 h-1.5 rounded-full bg-cyan shrink-0" />
                  <span>{f}</span>
                </li>
              ))}
            </ul>

            <div className="border-t border-white/[0.05] pt-4">
              <p className="text-[0.65rem] uppercase tracking-widest text-text-d font-geist-mono mb-1">
                {t("pricingSaveLabel")}
              </p>
              <p className="text-cyan/80 text-xs">{tier.save}</p>
            </div>

            <button
              className={`w-full py-2.5 rounded-full text-sm font-medium transition
                ${tier.highlighted
                  ? "bg-gradient-to-r from-purple to-cyan text-white hover:opacity-95"
                  : "border border-white/10 text-text-m hover:text-text hover:border-cyan/40"}`}
            >
              {tier.cta}
            </button>
          </motion.div>
        ))}
      </div>
    </section>
  );
}
