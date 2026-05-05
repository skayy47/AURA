"use client";
import { AuraLogo } from "@/components/ui/AuraLogo";
import { Link } from "@/i18n/navigation";
import { LanguageSwitcher } from "./LanguageSwitcher";

export function TopBar() {
  return (
    <div className="fixed top-0 start-0 end-0 z-50 h-12 flex items-center px-6 justify-between">
      <Link href="/" className="flex items-center gap-3 text-text hover:text-white transition-colors mix-blend-screen">
        <AuraLogo size={36} />
        <span className="font-brand text-base uppercase tracking-wider">AURA</span>
      </Link>
      <LanguageSwitcher />
    </div>
  );
}
