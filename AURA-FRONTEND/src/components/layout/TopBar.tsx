"use client";
import { AuraLogo } from "@/components/ui/AuraLogo";
import { Link } from "@/i18n/navigation";

export function TopBar() {
  return (
    <div className="fixed top-0 left-0 z-50 h-12 flex items-center px-6 mix-blend-screen">
      <Link href="/" className="flex items-center gap-3 text-text hover:text-white transition-colors">
        <AuraLogo size={36} />
        <span className="font-brand text-base uppercase tracking-wider">AURA</span>
      </Link>
    </div>
  );
}
