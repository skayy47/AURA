"use client";
import { useState } from "react";
import { CleaningConfig } from "@/lib/types";
import { NeonButton } from "@/components/ui/NeonButton";
import { AuraLoader } from "@/components/ui/AuraLoader";

export function CleaningPanel({ onClean, loading }: { onClean: (c: CleaningConfig) => void, loading: boolean }) {
  const [config, setConfig] = useState<CleaningConfig>({
    rename_columns: true,
    normalize_strings: true,
    detect_dates: true,
    remove_empty_cols: true,
    fill_missing: true,
    drop_duplicates: true,
  });

  const toggle = (k: keyof CleaningConfig) => setConfig((p) => ({ ...p, [k]: !p[k] }));

  return (
    <div className="aura-card p-6">
      <h3 className="text-lg font-semibold mb-4 text-text">Cleaning Configuration</h3>
      <div className="grid grid-cols-2 gap-4 mb-6">
        {Object.entries(config).map(([k, v]) => (
          <label key={k} className="flex items-center gap-3 cursor-pointer">
            <input type="checkbox" checked={v} onChange={() => toggle(k as keyof CleaningConfig)}
                   className="w-4 h-4 accent-purple rounded bg-surface border-border" />
            <span className="text-sm text-text-m">{k.replace(/_/g, " ")}</span>
          </label>
        ))}
      </div>
      <div className="flex justify-center">
        {loading ? (
          <AuraLoader size="sm" label="Cleaning" />
        ) : (
          <NeonButton onClick={() => onClean(config)} disabled={loading}>
            Run Cleaning Pipeline
          </NeonButton>
        )}
      </div>
    </div>
  );
}
