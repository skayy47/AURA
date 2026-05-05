"use client";
import { useLocale } from "next-intl";
import { useRouter, usePathname } from "@/i18n/navigation";
import { motion } from "framer-motion";

const LOCALES = [
  { code: "en", label: "EN" },
  { code: "ar", label: "عربي" },
] as const;

export function LanguageSwitcher() {
  const locale = useLocale();
  const router = useRouter();
  const pathname = usePathname();

  const toggle = (next: string) => {
    if (next === locale) return;
    router.replace(pathname as any, { locale: next });
  };

  return (
    <div
      role="group"
      aria-label="Language selector"
      className="relative flex items-center h-8 rounded-full bg-surface2/80 border border-white/[0.08] backdrop-blur-md overflow-hidden"
    >
      {LOCALES.map(({ code, label }) => {
        const isActive = locale === code;
        return (
          <button
            key={code}
            onClick={() => toggle(code)}
            aria-pressed={isActive}
            lang={code}
            className="relative z-10 px-3 h-full text-[0.72rem] font-medium tracking-wide transition-colors duration-200"
            style={{ color: isActive ? "#F1F5F9" : "#94A3B8" }}
          >
            {isActive && (
              <motion.span
                layoutId="lang-pill"
                className="absolute inset-0 rounded-full"
                style={{
                  background: "linear-gradient(135deg, rgba(108,63,229,0.6), rgba(34,211,238,0.4))",
                  border: "1px solid rgba(108,63,229,0.5)",
                }}
                transition={{ type: "spring", stiffness: 380, damping: 28 }}
              />
            )}
            <span className="relative z-10">{label}</span>
          </button>
        );
      })}
    </div>
  );
}
