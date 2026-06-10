"use client";

import { motion } from "framer-motion";
import { useTranslations } from "next-intl";

const STACK = [
  { n: "05", name: "Next.js 14",  tag: "frontend" },
  { n: "04", name: "FastAPI",     tag: "backend"  },
  { n: "03", name: "pandas",      tag: "compute"  },
  { n: "02", name: "Groq",        tag: "free ai"  },
  { n: "01", name: "Claude",      tag: "intel"    },
];

export function TechStack() {
  const t = useTranslations("landing");

  return (
    <section className="relative w-full max-w-6xl mx-auto px-6 py-20">
      <motion.div
        initial={{ opacity: 0, y: 16 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true, margin: "-100px" }}
        transition={{ duration: 0.5 }}
        className="mb-10"
      >
        <p className="eyebrow-mono mb-3">[07] · {t("techEyebrow")}</p>
        <h2 className="heading-display-lg text-text">{t("techTitle")}</h2>
      </motion.div>

      <div className="rounded-2xl border border-white/[0.06] bg-[rgba(7,12,26,0.55)] backdrop-blur p-6 lg:p-8">
        <ul className="grid grid-cols-1 md:grid-cols-5 gap-4 lg:gap-6">
          {STACK.map((tool, i) => (
            <motion.li
              key={tool.name}
              initial={{ opacity: 0, y: 12 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, margin: "-40px" }}
              transition={{ delay: i * 0.08, duration: 0.45 }}
              className="flex items-baseline justify-between md:justify-start md:flex-col md:items-start md:gap-1.5 py-3 md:py-0 border-b border-white/[0.04] md:border-0 last:border-0"
            >
              <span className="eyebrow-mono">[{tool.n}]</span>
              <div className="text-end md:text-start">
                <p className="font-bricolage font-bold text-text text-lg md:text-xl">{tool.name}</p>
                <p className="text-text-d text-[0.7rem] uppercase tracking-widest font-geist-mono">{tool.tag}</p>
              </div>
            </motion.li>
          ))}
        </ul>
      </div>
    </section>
  );
}
