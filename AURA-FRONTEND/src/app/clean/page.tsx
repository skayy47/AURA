"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";
import { motion } from "framer-motion";
import { PipelineBar } from "@/components/layout/PipelineBar";
import { PageHeader } from "@/components/layout/PageHeader";
import { EmptyState } from "@/components/ui/EmptyState";
import { CleaningPanel } from "@/components/clean/CleaningPanel";
import { CleaningLog } from "@/components/clean/CleaningLog";
import { MetricCard } from "@/components/ui/MetricCard";
import { runCleaning } from "@/lib/api";
import { useStore } from "@/lib/store";
import { CleaningConfig } from "@/lib/types";

export default function CleanPage() {
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
      setError(e.message ?? "Cleaning failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div>
      <PipelineBar />
      <PageHeader icon="🧼" title="Data Cleaning"
        subtitle="Standardize columns, impute missing values, and handle anomalies" />

      <div className="grid grid-cols-2 gap-8">
        <div>
          <CleaningPanel onClean={handleClean} loading={loading} />
          {error && <div className="mt-4 p-4 rounded-md bg-red-500/10 border border-red-500/30 text-red-400 text-sm">{error}</div>}
        </div>

        {cleanResult && (
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
            <div className="grid grid-cols-2 gap-3 mb-6">
              <MetricCard value={`${cleanResult.rows_before} → ${cleanResult.rows_after}`} label="Rows" />
              <MetricCard value={`${cleanResult.cols_before} → ${cleanResult.cols_after}`} label="Columns" />
            </div>
            <CleaningLog log={cleanResult.log} />
            <div className="flex justify-end mt-6">
              <button className="aura-btn" onClick={() => router.push("/explore")}>
                Next: Explore Data →
              </button>
            </div>
          </motion.div>
        )}
      </div>
    </div>
  );
}
