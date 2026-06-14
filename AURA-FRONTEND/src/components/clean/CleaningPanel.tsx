"use client";
import { useState } from "react";
import { useTranslations } from "next-intl";
import { CleaningConfig } from "@/lib/types";
import { NeonButton } from "@/components/ui/NeonButton";
import { AuraLoader } from "@/components/ui/AuraLoader";

export function CleaningPanel({ onClean, loading }: { onClean: (c: CleaningConfig) => void, loading: boolean }) {
  const t = useTranslations("clean");
  const [config, setConfig] = useState<CleaningConfig>({
    rename_columns: true,
    normalize_strings: true,
    detect_dates: true,
    remove_empty_cols: true,
    fill_missing: true,
    drop_duplicates: true,
  });

  const toggle = (k: keyof CleaningConfig) => setConfig((p) => ({ ...p, [k]: !p[k] }));

  const optionKeys = Object.keys(config) as Array<keyof CleaningConfig>;

  return (
    <div className="aura-card p-6">
      <h3 className="text-lg font-semibold mb-4 text-text">{t("configTitle")}</h3>
      <div className="grid grid-cols-2 gap-4 mb-6">
        {optionKeys.map((k) => (
          <label key={k} className="flex items-center gap-3 cursor-pointer">
            <input type="checkbox" checked={config[k]} onChange={() => toggle(k)}
                   className="w-4 h-4 accent-purple rounded bg-surface border-border" />
            <span className="text-sm text-text-m">{t(`options.${k}`)}</span>
          </label>
        ))}
      </div>
      <div className="flex justify-center">
        {loading ? (
          <AuraLoader size="sm" label={t("cleaning")} />
        ) : (
          <NeonButton onClick={() => onClean(config)} disabled={loading}>
            {t("runBtn")}
          </NeonButton>
        )}
      </div>
    </div>
  );
}
