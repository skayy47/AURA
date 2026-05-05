"use client";
import { useState } from "react";
import { useTranslations } from "next-intl";
import { motion } from "framer-motion";
import { PipelineRoad } from "@/components/layout/PipelineRoad";
import { PageHeader } from "@/components/layout/PageHeader";
import { Sparkles } from "@/components/layout/pipeline-icons";
import { EmptyState } from "@/components/ui/EmptyState";
import { CleaningPanel } from "@/components/clean/CleaningPanel";
import { CleaningLog } from "@/components/clean/CleaningLog";
import { MetricCard } from "@/components/ui/MetricCard";
import { NeonButton } from "@/components/ui/NeonButton";
import { runCleaning } from "@/lib/api";
import { useStore } from "@/lib/store";
import { CleaningConfig } from "@/lib/types";
import { useRouter } from "@/i18n/navigation";

export default function CleanPage() {
  const t = useTranslations("clean");
  const router = useRouter();
  const { sessionId, meta, cleanResult, setClean } = useStore();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  if (!meta || !sessionId) return <EmptyState />;

  async function handleClean(config: CleaningConfig) {
    setLoading(true);
    setError(null);
    try {
      const res = await runCleaning(sessionId!, config);
      setClean(res);
    } catch (e: any) {
      setError(e.message ?? t("..errors.cleaningFailed"));
    } finally {
      setLoading(false);
    }
  }

  return (
    <div>
      <PipelineRoad />
      <PageHeader
        icon={<Sparkles size={28} className="text-purple" />}
        title={t("title")}
        subtitle={t("subtitle")}
      />

      <div className="grid grid-cols-2 gap-8">
        <div>
          <CleaningPanel onClean={handleClean} loading={loading} />
          {error && (
            <div className="mt-4 p-4 rounded-md bg-red-500/10 border border-red-500/30 text-red-400 text-sm">
              {error}
            </div>
          )}
        </div>

        {cleanResult && (
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
            <div className="grid grid-cols-2 gap-3 mb-6">
              <MetricCard
                value={`${cleanResult.rows_before} → ${cleanResult.rows_after}`}
                label={t("rowsLabel")}
              />
              <MetricCard
                value={`${cleanResult.cols_before} → ${cleanResult.cols_after}`}
                label={t("colsLabel")}
              />
            </div>
            <CleaningLog log={cleanResult.log} />
            <div className="flex justify-end mt-6">
              <NeonButton onClick={() => router.push("/explore")}>
                {t("nextExplore")}
              </NeonButton>
            </div>
          </motion.div>
        )}
      </div>
    </div>
  );
}
