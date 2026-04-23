"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";
import { motion } from "framer-motion";
import { PipelineRoad } from "@/components/layout/PipelineRoad";
import { PageHeader } from "@/components/layout/PageHeader";
import { UploadZone } from "@/components/ingest/UploadZone";
import { MetricCard } from "@/components/ui/MetricCard";
import { NeonButton } from "@/components/ui/NeonButton";
import { DataTable } from "@/components/ingest/DataTable";
import { uploadFile } from "@/lib/api";
import { useStore } from "@/lib/store";

export default function IngestPage() {
  const router = useRouter();
  const { setSession, setIngest, meta, preview } = useStore();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleFile(file: File) {
    setLoading(true);
    setError(null);
    try {
      const res = await uploadFile(file);
      setSession(res.session_id);
      setIngest(res.meta, res.preview);
    } catch (e: any) {
      setError(e.message ?? "Upload failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div>
      <PipelineRoad />
      <PageHeader icon="📂" title="Data Ingestion"
        subtitle="Upload and validate your dataset — CSV, Excel, JSON, Parquet, TSV" />

      <UploadZone onFile={handleFile} loading={loading} />

      {error && (
        <div className="mt-4 p-4 rounded-md bg-red-500/10 border border-red-500/30 text-red-400 text-sm">
          {error}
        </div>
      )}

      {meta && (
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="mt-8 space-y-8">
          {/* Metrics */}
          <div className="grid grid-cols-5 gap-3">
            <MetricCard value={meta.rows.toLocaleString()} label="Rows" index={0} />
            <MetricCard value={meta.cols} label="Columns" index={1} />
            <MetricCard value={`${meta.file_size_kb} KB`} label="File Size" variant="accent" index={2} />
            <MetricCard value={meta.format} label="Format" index={3} />
            <MetricCard
              value={meta.missing_count > 0 ? `${meta.missing_count} missing` : "0 missing"}
              label="Issues"
              variant={meta.missing_count > 0 ? "warn" : "success"}
              index={4}
            />
          </div>

          {/* Preview */}
          {preview && (
            <div>
              <h2 className="text-text font-semibold text-base mb-3">
                Preview <span className="text-text-d font-normal text-sm">— first 5 rows</span>
              </h2>
              <DataTable columns={meta.columns} rows={preview} />
            </div>
          )}

          {/* CTA */}
          <div className="flex items-center justify-between pt-4 border-t border-border">
            <p className="text-text-m text-sm">Dataset validated — ready for cleaning.</p>
            <NeonButton onClick={() => router.push("/clean")}>
              Next: Clean Data
            </NeonButton>
          </div>
        </motion.div>
      )}
    </div>
  );
}
