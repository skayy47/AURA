"use client";

import { useTranslations } from "next-intl";
import { Link } from "@/i18n/navigation";
import { AuraLogo } from "@/components/ui/AuraLogo";

export function FooterV5() {
  const t = useTranslations("landing");

  return (
    <footer className="relative w-full border-t border-white/[0.05] mt-12">
      <div className="max-w-6xl mx-auto px-6 py-14">
        <div className="grid grid-cols-2 md:grid-cols-5 gap-8 mb-10">
          <div className="col-span-2">
            <div className="flex items-center gap-3 mb-4 text-text">
              <AuraLogo size={28} />
              <span className="font-brand font-bold text-base tracking-widest">AURA</span>
            </div>
            <p className="text-text-m text-sm max-w-xs leading-relaxed">{t("footerTaglineV5")}</p>
            <p className="mt-4 text-text-d text-xs font-geist-mono">{t("footerTagline")}</p>
          </div>

          <div>
            <p className="eyebrow-mono mb-3">{t("footerProduct")}</p>
            <ul className="flex flex-col gap-2 text-sm">
              <li><Link href="/ingest" className="text-text-m hover:text-text transition">{t("footerIngest")}</Link></li>
              <li><Link href="/clean" className="text-text-m hover:text-text transition">{t("footerClean")}</Link></li>
              <li><Link href="/explore" className="text-text-m hover:text-text transition">{t("footerExplore")}</Link></li>
              <li><Link href="/ai-chat" className="text-text-m hover:text-text transition">{t("footerAi")}</Link></li>
              <li><Link href="/docs" className="text-text-m hover:text-text transition">{t("footerExport")}</Link></li>
            </ul>
          </div>

          <div>
            <p className="eyebrow-mono mb-3">{t("footerResources")}</p>
            <ul className="flex flex-col gap-2 text-sm">
              <li>
                <a href="https://github.com/skayy47/AURA" target="_blank" rel="noopener noreferrer" className="text-text-m hover:text-text transition">
                  {t("footerGithub")}
                </a>
              </li>
              <li><Link href="/docs" className="text-text-m hover:text-text transition">{t("footerDocs")}</Link></li>
              <li><Link href="/pricing" className="text-text-m hover:text-text transition">{t("footerPricing")}</Link></li>
            </ul>
          </div>

          <div>
            <p className="eyebrow-mono mb-3">{t("footerCompany")}</p>
            <ul className="flex flex-col gap-2 text-sm">
              <li><span className="text-text-m cursor-default">{t("footerAbout")}</span></li>
              <li><span className="text-text-m cursor-default">{t("footerPrivacy")}</span></li>
              <li>
                <a href="mailto:oussamaiskia@gmail.com" className="text-text-m hover:text-text transition">{t("footerContact")}</a>
              </li>
            </ul>
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
