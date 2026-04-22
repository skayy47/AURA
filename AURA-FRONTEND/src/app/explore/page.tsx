"use client";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { PipelineBar } from "@/components/layout/PipelineBar";
import { PageHeader } from "@/components/layout/PageHeader";
import { EmptyState } from "@/components/ui/EmptyState";
import { MetricCard } from "@/components/ui/MetricCard";
import { DistributionChart } from "@/components/explore/DistributionChart";
import { CorrelationMatrix } from "@/components/explore/CorrelationMatrix";
import { fetchExplore } from "@/lib/api";
import { useStore } from "@/lib/store";

export default function ExplorePage() {
  const router = useRouter();
  const { sessionId, meta, exploreData, setExplore } = useStore();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (sessionId && !exploreData && !loading) {
      setLoading(true);
      fetchExplore(sessionId)
        .then(res => setExplore(res))
        .catch(e => setError(e.message))
        .finally(() => setLoading(false));
    }
  }, [sessionId, exploreData]);

  if (!meta || !sessionId) return <EmptyState />;

  return (
    <div>
      <PipelineBar />
      <PageHeader icon="🔍" title="Data Exploration"
        subtitle="Automated profiling, distributions, and missing value analysis" />

      {loading && <div className="text-text-m text-sm">Generating profile...</div>}
      {error && <div className="mt-4 p-4 rounded-md bg-red-500/10 border border-red-500/30 text-red-400 text-sm">{error}</div>}

      {exploreData && (
        <div className="space-y-8 mt-6">
          <div className="grid grid-cols-4 gap-3">
            <MetricCard value={exploreData.numeric_cols.length} label="Numeric Cols" />
            <MetricCard value={exploreData.categorical_cols.length} label="Categorical Cols" />
            <MetricCard value={exploreData.datetime_cols.length} label="Datetime Cols" />
            <MetricCard value={`${exploreData.shape.rows} x ${exploreData.shape.cols}`} label="Shape" variant="accent" />
          </div>

          <div className="grid grid-cols-2 gap-6">
            <div>
              <h3 className="text-lg font-semibold mb-4 text-text">Missing Values</h3>
              <DistributionChart 
                data={exploreData.missing_heatmap} 
                xKey="column" 
                yKey="missing" 
                color="#F59E0B"
              />
            </div>
            <div>
              <h3 className="text-lg font-semibold mb-4 text-text">Correlations</h3>
              <CorrelationMatrix data={[]} />
            </div>
          </div>

          <div className="flex justify-end pt-4 border-t border-border">
            <button className="aura-btn" onClick={() => router.push("/ai-chat")}>
              Next: AI Chat →
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
