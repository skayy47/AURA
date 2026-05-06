"use client";
import { useState } from "react";
import { useTranslations } from "next-intl";
import { useLocale } from "next-intl";
import { motion } from "framer-motion";
import { CheckCircle } from "@/components/layout/pipeline-icons";
import { useTier } from "@/lib/tier";

interface PricingTier {
  key: string;
  nameKey: string;
  priceKey: string;
  periodKey: string;
  descKey: string;
  ctaKey: string;
  features: string[];
  stripeKey: "pro" | "team" | null;
  highlighted: boolean;
}

const TIERS: PricingTier[] = [
  {
    key: "free",
    nameKey: "pricingFreeName", priceKey: "pricingFreePrice", periodKey: "pricingFreePeriod",
    descKey: "pricingFreeDesc", ctaKey: "pricingFreeCta",
    features: ["pricingFreeF1", "pricingFreeF2", "pricingFreeF3", "pricingFreeF4"],
    stripeKey: null, highlighted: false,
  },
  {
    key: "pro",
    nameKey: "pricingProName", priceKey: "pricingProPrice", periodKey: "pricingProPeriod",
    descKey: "pricingProDesc", ctaKey: "pricingProCta",
    features: ["pricingProF1", "pricingProF2", "pricingProF3", "pricingProF4", "pricingProF5"],
    stripeKey: "pro", highlighted: true,
  },
  {
    key: "team",
    nameKey: "pricingTeamName", priceKey: "pricingTeamPrice", periodKey: "pricingTeamPeriod",
    descKey: "pricingTeamDesc", ctaKey: "pricingTeamCta",
    features: ["pricingTeamF1", "pricingTeamF2", "pricingTeamF3", "pricingTeamF4", "pricingTeamF5"],
    stripeKey: "team", highlighted: false,
  },
];

export default function PricingPage() {
  const t = useTranslations("landing");
  const locale = useLocale();
  const { tier: currentTier } = useTier();
  const [loading, setLoading] = useState<string | null>(null);
  const [error, setError]     = useState<string | null>(null);

  const handleUpgrade = async (tier: "pro" | "team") => {
    setLoading(tier);
    setError(null);
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
      const res = await fetch(`${apiUrl}/api/billing/checkout`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ tier, locale }),
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const { url } = await res.json();
      window.location.href = url;
    } catch (e: any) {
      setError(e.message ?? "Checkout failed");
      setLoading(null);
    }
  };

  return (
    <div className="flex flex-col items-center px-6 pt-20 pb-24">
      <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} className="text-center mb-14">
        <h1 className="font-brand text-4xl md:text-5xl text-text mb-4">{t("pricingTitle")}</h1>
        <p className="text-text-m text-lg max-w-lg mx-auto">{t("pricingSub")}</p>
      </motion.div>

      {error && (
        <div className="mb-8 px-5 py-3 rounded-lg bg-red-500/10 border border-red-500/30 text-red-400 text-sm">
          {error}
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 w-full max-w-5xl items-start">
        {TIERS.map((tier, i) => {
          const isCurrent = currentTier === tier.key;
          return (
            <motion.div
              key={tier.key}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.1 }}
              className={`relative rounded-2xl p-6 flex flex-col gap-4 border transition-all
                ${tier.highlighted
                  ? "border-purple/60 bg-purple/10 shadow-[0_0_40px_rgba(108,63,229,0.15)]"
                  : "border-white/[0.06] bg-surface2/60"}`}
            >
              {tier.highlighted && (
                <div className="absolute -top-3 start-1/2 -translate-x-1/2 px-3 py-0.5 rounded-full text-[0.65rem] font-bold tracking-widest uppercase bg-gradient-to-r from-purple to-cyan text-white">
                  Most Popular
                </div>
              )}

              <div>
                <p className="text-text-d text-xs uppercase tracking-widest mb-1">{t(tier.nameKey as any)}</p>
                <div className="flex items-baseline gap-1">
                  <span className="text-3xl font-bold font-bricolage text-text">{t(tier.priceKey as any)}</span>
                  <span className="text-text-d text-sm">{t(tier.periodKey as any)}</span>
                </div>
                <p className="text-text-m text-xs mt-1">{t(tier.descKey as any)}</p>
              </div>

              <ul className="flex flex-col gap-2 flex-1">
                {tier.features.map((fKey) => (
                  <li key={fKey} className="flex items-center gap-2 text-sm text-text-m">
                    <CheckCircle size={14} className="text-green shrink-0" />
                    {t(fKey as any)}
                  </li>
                ))}
              </ul>

              {isCurrent ? (
                <div className="w-full mt-2 py-2.5 rounded-full text-sm font-medium text-center border border-green/30 text-green bg-green/5">
                  Current plan
                </div>
              ) : tier.stripeKey ? (
                <button
                  onClick={() => handleUpgrade(tier.stripeKey!)}
                  disabled={loading === tier.stripeKey}
                  className={`w-full mt-2 py-2.5 rounded-full text-sm font-medium transition-all
                    ${tier.highlighted
                      ? "bg-gradient-to-r from-purple to-cyan text-white hover:opacity-90"
                      : "border border-white/[0.1] text-text-m hover:text-text hover:border-white/20"}
                    disabled:opacity-50 disabled:cursor-not-allowed`}
                >
                  {loading === tier.stripeKey ? "Redirecting…" : t(tier.ctaKey as any)}
                </button>
              ) : (
                <button
                  className="w-full mt-2 py-2.5 rounded-full text-sm font-medium border border-white/[0.1] text-text-m hover:text-text hover:border-white/20 transition-all"
                  onClick={() => window.location.href = `/${locale}/ingest`}
                >
                  {t(tier.ctaKey as any)}
                </button>
              )}
            </motion.div>
          );
        })}
      </div>
    </div>
  );
}
