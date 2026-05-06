"use client";
import { useTranslations } from "next-intl";
import { Link } from "@/i18n/navigation";
import { useTier, tierAtLeast, type Tier } from "@/lib/tier";
import type { ReactNode } from "react";

interface Props {
  requires: Tier;
  children: ReactNode;
  /** Optional custom upsell message */
  message?: string;
}

export function ProGate({ requires, children, message }: Props) {
  const { tier } = useTier();
  const t = useTranslations("billing");

  if (tierAtLeast(tier, requires)) return <>{children}</>;

  return (
    <div className="relative rounded-xl overflow-hidden">
      {/* blurred preview of the gated content */}
      <div className="pointer-events-none select-none blur-[3px] opacity-40 saturate-50">
        {children}
      </div>

      {/* overlay */}
      <div className="absolute inset-0 flex flex-col items-center justify-center gap-3 bg-bg/60 backdrop-blur-sm">
        <div className="flex items-center gap-2">
          {/* lock icon */}
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#6C3FE5" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <rect width="18" height="11" x="3" y="11" rx="2" ry="2" />
            <path d="M7 11V7a5 5 0 0 1 10 0v4" />
          </svg>
          <span className="text-sm font-medium text-text">
            {message ?? `${t(requires)} ${t("upgrade")}`}
          </span>
        </div>
        <Link
          href="/pricing"
          className="px-5 py-2 rounded-full text-sm font-medium bg-gradient-to-r from-purple to-cyan text-white hover:opacity-90 transition-opacity"
        >
          {t("upgrade")}
        </Link>
      </div>
    </div>
  );
}
