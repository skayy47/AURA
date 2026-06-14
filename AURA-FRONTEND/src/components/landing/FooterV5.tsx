"use client";

import { useTranslations } from "next-intl";
import { AuraLogo } from "@/components/ui/AuraLogo";

export function FooterV5() {
  const t = useTranslations("landing");

  return (
    <footer className="relative w-full mt-12 overflow-hidden">
      {/* Aurora glow border */}
      <div className="absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-cyan/60 to-transparent" />
      <div className="absolute inset-x-0 top-0 h-[1px] blur-sm bg-gradient-to-r from-transparent via-purple/50 to-transparent" />
      {/* Subtle radial glow from center-top */}
      <div className="absolute inset-x-0 top-0 h-40 bg-[radial-gradient(ellipse_60%_100%_at_50%_0%,rgba(34,211,238,0.06),transparent)] pointer-events-none" />

      <div className="max-w-6xl mx-auto px-6 py-14">
        <div className="flex flex-col md:flex-row items-start justify-between gap-10 mb-10">
          {/* Brand + description */}
          <div className="max-w-sm">
            <div className="flex items-center gap-3 mb-4">
              <div className="relative">
                <div className="absolute inset-0 blur-md bg-cyan/20 rounded-full" />
                <AuraLogo size={28} />
              </div>
              <span className="font-brand font-bold text-base tracking-widest text-text">AURA</span>
            </div>
            <p className="text-text-m text-sm leading-relaxed">{t("footerTaglineV5")}</p>
            <p className="mt-4 text-text-d text-xs font-geist-mono">{t("footerTagline")}</p>
          </div>

          {/* Minimal links */}
          <div className="flex flex-col gap-3 pt-1">
            <a
              href="https://github.com/skayy47/AURA"
              target="_blank"
              rel="noopener noreferrer"
              className="group flex items-center gap-2 text-sm text-text-m hover:text-cyan transition-colors duration-200"
            >
              <span className="w-1.5 h-1.5 rounded-full bg-cyan/40 group-hover:bg-cyan group-hover:shadow-[0_0_6px_rgba(34,211,238,0.8)] transition-all duration-200" />
              {t("footerGithub")}
            </a>
            <a
              href="mailto:oussamaiskia@gmail.com"
              className="group flex items-center gap-2 text-sm text-text-m hover:text-cyan transition-colors duration-200"
            >
              <span className="w-1.5 h-1.5 rounded-full bg-purple/40 group-hover:bg-purple group-hover:shadow-[0_0_6px_rgba(139,92,246,0.8)] transition-all duration-200" />
              {t("footerContact")}
            </a>
          </div>
        </div>

        <div className="divider-aurora mb-6" />

        <div className="flex flex-col md:flex-row items-center justify-between gap-4 text-text-d text-xs font-geist-mono">
          <p>© 2026 AURA · MIT</p>
          <p className="uppercase tracking-widest">{t("footerByline")}</p>
        </div>
      </div>
    </footer>
  );
}
