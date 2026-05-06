"use client";

import { useTranslations } from "next-intl";
import { AuraBot } from "@/components/ai/AuraBot";
import { DataConstellation } from "@/components/ai/DataConstellation";
import { GlowCard } from "@/components/ui/GlowCard";
import { AuraLogo } from "@/components/ui/AuraLogo";
import { Upload, Sparkles, Bot, CheckCircle } from "@/components/layout/pipeline-icons";
import { Link, useRouter } from "@/i18n/navigation";
import { useState } from "react";
import { useStore } from "@/lib/store";
import { uploadFile } from "@/lib/api";
import { motion, AnimatePresence } from "framer-motion";

// ─── inline icon primitives ────────────────────────────────────────────────
function ChevronDown({ open }: { open: boolean }) {
  return (
    <svg width="16" height="16" viewBox="0 0 16 16" fill="none" className={`transition-transform duration-200 ${open ? "rotate-180" : ""}`}>
      <path d="M3 6l5 5 5-5" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
}
function StepIcon({ n }: { n: number }) {
  return (
    <div className="w-10 h-10 rounded-full flex items-center justify-center text-sm font-bold font-geist-mono border border-purple/40 bg-purple/10 text-purple-l shrink-0">
      {n}
    </div>
  );
}

// ─── sample catalogue (mirrors backend) ────────────────────────────────────
const SAMPLES = [
  { slug: "sales-mess",       accent: "cyan"   as const, rows: 40, cols: 11, tags: ["duplicates", "outliers", "nulls"] },
  { slug: "climate-sensors",  accent: "purple" as const, rows: 44, cols: 12, tags: ["time-series", "MENA", "sensors"]  },
  { slug: "mena-orders",      accent: "blue"   as const, rows: 50, cols: 13, tags: ["e-commerce", "MENA", "clean"]     },
];

// ─── FAQ accordion item ─────────────────────────────────────────────────────
function FaqItem({ q, a }: { q: string; a: string }) {
  const [open, setOpen] = useState(false);
  return (
    <div className="border-b border-white/[0.06]">
      <button
        className="w-full flex items-center justify-between gap-4 py-5 text-start text-text font-medium hover:text-white transition-colors"
        onClick={() => setOpen(!open)}
      >
        <span>{q}</span>
        <span className="text-text-d shrink-0"><ChevronDown open={open} /></span>
      </button>
      <AnimatePresence initial={false}>
        {open && (
          <motion.div
            key="body"
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: "auto", opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.22 }}
            className="overflow-hidden"
          >
            <p className="pb-5 text-text-m text-sm leading-relaxed">{a}</p>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

// ─── pricing card ───────────────────────────────────────────────────────────
interface PricingCardProps {
  name: string; price: string; period: string; desc: string; cta: string;
  features: string[]; highlighted?: boolean;
}
function PricingCard({ name, price, period, desc, cta, features, highlighted }: PricingCardProps) {
  return (
    <div className={`relative rounded-2xl p-6 flex flex-col gap-4 border transition-all duration-300
      ${highlighted
        ? "border-purple/60 bg-purple/10 shadow-[0_0_40px_rgba(108,63,229,0.15)]"
        : "border-white/[0.06] bg-surface2/60"}`}
    >
      {highlighted && (
        <div className="absolute -top-3 start-1/2 -translate-x-1/2 px-3 py-0.5 rounded-full text-[0.65rem] font-bold tracking-widest uppercase bg-gradient-to-r from-purple to-cyan text-white">
          Most Popular
        </div>
      )}
      <div>
        <p className="text-text-d text-xs uppercase tracking-widest mb-1">{name}</p>
        <div className="flex items-baseline gap-1">
          <span className="text-3xl font-bold font-bricolage text-text">{price}</span>
          <span className="text-text-d text-sm">{period}</span>
        </div>
        <p className="text-text-m text-xs mt-1">{desc}</p>
      </div>
      <ul className="flex flex-col gap-2 flex-1">
        {features.map((f, i) => (
          <li key={i} className="flex items-center gap-2 text-sm text-text-m">
            <CheckCircle size={14} className="text-green shrink-0" />
            {f}
          </li>
        ))}
      </ul>
      <button
        className={`w-full mt-2 py-2.5 rounded-full text-sm font-medium transition-all
          ${highlighted
            ? "bg-gradient-to-r from-purple to-cyan text-white hover:opacity-90"
            : "border border-white/[0.1] text-text-m hover:text-text hover:border-white/20"}`}
      >
        {cta}
      </button>
    </div>
  );
}

// ─── page ───────────────────────────────────────────────────────────────────
export default function LandingPage() {
  const t = useTranslations("landing");
  const tErrors = useTranslations("errors");
  const router = useRouter();
  const setIngest   = useStore((s) => s.setIngest);
  const setSession  = useStore((s) => s.setSession);
  const setFirstRun = useStore((s) => s.setFirstRun);

  const [botState, setBotState]   = useState<"idle" | "thinking" | "celebrate" | "error">("idle");
  const [demoError, setDemoError] = useState<string | null>(null);
  const [loadingSlug, setLoadingSlug] = useState<string | null>(null);

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
      setTimeout(() => router.push("/ingest"), 1200);
    } catch {
      setBotState("error");
      setDemoError(tErrors("networkDown"));
      setTimeout(() => setBotState("idle"), 2500);
    }
  };

  const handleLoadSample = async (slug: string) => {
    setLoadingSlug(slug);
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
      const res = await fetch(`${apiUrl}/api/samples/${slug}/load`, { method: "POST" });
      if (!res.ok) throw new Error("Sample load failed");
      const result = await res.json();
      setSession(result.session_id);
      setIngest(result.meta, result.preview, result.warnings ?? []);
      setFirstRun(true);
      router.push("/ingest");
    } catch {
      setDemoError(tErrors("networkDown"));
    } finally {
      setLoadingSlug(null);
    }
  };

  const HOW_STEPS = [
    { n: 1, icon: <Upload size={20} />,   title: t("how1Title"), body: t("how1Body") },
    { n: 2, icon: <Sparkles size={20} />, title: t("how2Title"), body: t("how2Body") },
    { n: 3, icon: <Sparkles size={20} />, title: t("how3Title"), body: t("how3Body") },
    { n: 4, icon: <Bot size={20} />,      title: t("how4Title"), body: t("how4Body") },
    { n: 5, icon: <Upload size={20} />,   title: t("how5Title"), body: t("how5Body") },
  ];

  const PRICING = [
    {
      name: t("pricingFreeName"), price: t("pricingFreePrice"), period: t("pricingFreePeriod"),
      desc: t("pricingFreeDesc"), cta: t("pricingFreeCta"),
      features: [t("pricingFreeF1"), t("pricingFreeF2"), t("pricingFreeF3"), t("pricingFreeF4")],
    },
    {
      name: t("pricingProName"), price: t("pricingProPrice"), period: t("pricingProPeriod"),
      desc: t("pricingProDesc"), cta: t("pricingProCta"),
      features: [t("pricingProF1"), t("pricingProF2"), t("pricingProF3"), t("pricingProF4"), t("pricingProF5")],
      highlighted: true,
    },
    {
      name: t("pricingTeamName"), price: t("pricingTeamPrice"), period: t("pricingTeamPeriod"),
      desc: t("pricingTeamDesc"), cta: t("pricingTeamCta"),
      features: [t("pricingTeamF1"), t("pricingTeamF2"), t("pricingTeamF3"), t("pricingTeamF4"), t("pricingTeamF5")],
    },
  ];

  const FAQS = [
    { q: t("faq1Q"), a: t("faq1A") },
    { q: t("faq2Q"), a: t("faq2A") },
    { q: t("faq3Q"), a: t("faq3A") },
    { q: t("faq4Q"), a: t("faq4A") },
    { q: t("faq5Q"), a: t("faq5A") },
  ];

  return (
    <div className="flex flex-col items-center">

      {/* ── Hero ─────────────────────────────────────────────────────────── */}
      <section className="flex flex-col items-center text-center w-full max-w-3xl min-h-[calc(100vh-56px)] justify-center pb-12 px-6">
        <div className="w-[280px] h-[280px] mb-8 relative flex items-center justify-center">
          <DataConstellation className="absolute inset-0 w-full h-full" />
          {botState === "thinking" && (
            <motion.div
              className="absolute -inset-4 rounded-full border-2 border-dashed border-cyan/50"
              animate={{ rotate: 360 }}
              transition={{ duration: 4, repeat: Infinity, ease: "linear" }}
            />
          )}
          <AuraBot size={280} state={botState} />
        </div>

        <h1 className="font-brand text-5xl md:text-6xl text-text mb-5 tracking-tight leading-tight">
          {t("hero")}
        </h1>
        <p className="text-text-m text-lg max-w-[520px] mb-10 leading-relaxed">{t("sub")}</p>

        <div className="flex flex-wrap items-center justify-center gap-4">
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
            className="px-8 py-3 rounded-full bg-transparent font-medium text-text-m hover:text-text border border-border hover:border-text-d transition-colors"
          >
            {t("ctaSecondary")}
          </button>
        </div>

        <AnimatePresence>
          {demoError && (
            <motion.p key="demo-err" initial={{ opacity: 0, y: 6 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: 6 }}
              className="mt-5 text-sm text-amber font-geist-mono">
              {demoError}
            </motion.p>
          )}
        </AnimatePresence>

        <div className="mt-12 text-xs uppercase tracking-widest bg-gradient-to-r from-purple-l via-cyan to-blue bg-clip-text text-transparent">
          {t("byline")}
        </div>
      </section>

      {/* ── Value props ──────────────────────────────────────────────────── */}
      <section className="grid grid-cols-1 md:grid-cols-3 gap-6 w-full max-w-5xl pb-16 px-6">
        {[
          { accent: "cyan"   as const, icon: <Upload size={20} />,   title: t("smartIngestion"),    body: t("smartIngestionBody")    },
          { accent: "purple" as const, icon: <Sparkles size={20} />, title: t("automatedCleaning"), body: t("automatedCleaningBody") },
          { accent: "blue"   as const, icon: <Bot size={20} />,      title: t("aiAnalysis"),        body: t("aiAnalysisBody")        },
        ].map((card, i) => (
          <motion.div key={i} initial={{ opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }} transition={{ delay: i * 0.1 }}>
            <GlowCard accent={card.accent} intensity="low" className="h-full">
              <div className={`bg-[#0A1022] w-12 h-12 rounded-full flex items-center justify-center mb-6 border border-${card.accent}/30 text-${card.accent}`}>
                {card.icon}
              </div>
              <h3 className="font-brand text-lg text-text mb-3">{card.title}</h3>
              <p className="text-text-m text-sm leading-relaxed">{card.body}</p>
            </GlowCard>
          </motion.div>
        ))}
      </section>

      {/* ── Samples grid ─────────────────────────────────────────────────── */}
      <section className="w-full max-w-5xl pb-20 px-6">
        <div className="text-center mb-10">
          <h2 className="font-brand text-3xl md:text-4xl text-text mb-3">{t("samplesTitle")}</h2>
          <p className="text-text-m">{t("samplesSub")}</p>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {SAMPLES.map((s, i) => (
            <motion.div key={s.slug} initial={{ opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }} transition={{ delay: i * 0.1 }}>
              <GlowCard accent={s.accent} intensity="low" className="h-full flex flex-col">
                <div className="flex-1">
                  <div className="flex flex-wrap gap-1.5 mb-4">
                    {s.tags.map((tag) => (
                      <span key={tag} className="text-[0.6rem] px-2 py-0.5 rounded-full border border-white/[0.08] text-text-d uppercase tracking-wider">
                        {tag}
                      </span>
                    ))}
                  </div>
                  <h3 className="font-bricolage font-bold text-text mb-2">
                    {s.slug === "sales-mess"      ? "Sales Pipeline (messy)"       :
                     s.slug === "climate-sensors"  ? "MENA Climate Sensors"         :
                                                    "MENA E-Commerce Orders"}
                  </h3>
                  <p className="text-text-d text-xs font-geist-mono mb-1">{s.rows} rows · {s.cols} cols</p>
                </div>
                <button
                  onClick={() => handleLoadSample(s.slug)}
                  disabled={loadingSlug === s.slug}
                  className="mt-5 w-full py-2 rounded-full text-sm font-medium border border-white/[0.1] text-text-m hover:text-text hover:border-purple/50 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {loadingSlug === s.slug ? t("samplesLoading") : t("samplesLoad")}
                </button>
              </GlowCard>
            </motion.div>
          ))}
        </div>
      </section>

      {/* ── How it works ─────────────────────────────────────────────────── */}
      <section className="w-full max-w-3xl pb-20 px-6">
        <div className="text-center mb-12">
          <h2 className="font-brand text-3xl md:text-4xl text-text mb-3">{t("howTitle")}</h2>
          <p className="text-text-m">{t("howSub")}</p>
        </div>
        <div className="flex flex-col gap-px">
          {HOW_STEPS.map((step, i) => (
            <motion.div key={step.n} initial={{ opacity: 0, x: -20 }} whileInView={{ opacity: 1, x: 0 }} viewport={{ once: true }} transition={{ delay: i * 0.08 }}
              className="flex items-start gap-5 py-5 border-b border-white/[0.05] last:border-0">
              <StepIcon n={step.n} />
              <div>
                <h4 className="font-bricolage font-bold text-text mb-1">{step.title}</h4>
                <p className="text-text-m text-sm leading-relaxed">{step.body}</p>
              </div>
            </motion.div>
          ))}
        </div>
      </section>

      {/* ── Pricing ──────────────────────────────────────────────────────── */}
      <section className="w-full max-w-5xl pb-20 px-6">
        <div className="text-center mb-12">
          <h2 className="font-brand text-3xl md:text-4xl text-text mb-3">{t("pricingTitle")}</h2>
          <p className="text-text-m">{t("pricingSub")}</p>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 items-start">
          {PRICING.map((tier, i) => (
            <motion.div key={i} initial={{ opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }} transition={{ delay: i * 0.1 }}>
              <PricingCard {...tier} />
            </motion.div>
          ))}
        </div>
      </section>

      {/* ── FAQ ──────────────────────────────────────────────────────────── */}
      <section className="w-full max-w-2xl pb-20 px-6">
        <h2 className="font-brand text-3xl md:text-4xl text-text mb-10 text-center">{t("faqTitle")}</h2>
        {FAQS.map((item, i) => (
          <FaqItem key={i} q={item.q} a={item.a} />
        ))}
      </section>

      {/* ── Footer ───────────────────────────────────────────────────────── */}
      <footer className="w-full border-t border-white/[0.05] py-10 px-6 flex flex-col items-center gap-4">
        <div className="flex items-center gap-3 text-text-d">
          <AuraLogo size={24} />
          <span className="font-brand text-sm uppercase tracking-widest">AURA</span>
        </div>
        <p className="text-text-d text-xs">{t("footerTagline")}</p>
        <div className="flex items-center gap-6 text-text-d text-xs">
          <a href="https://github.com/skayy47/AURA" target="_blank" rel="noopener noreferrer" className="hover:text-text transition-colors">{t("footerGithub")}</a>
          <Link href="/docs" className="hover:text-text transition-colors">{t("footerDocs")}</Link>
          <span className="cursor-default">{t("footerPrivacy")}</span>
        </div>
      </footer>

    </div>
  );
}
