"use client";
import { useState } from "react";
import { useTranslations } from "next-intl";
import { motion } from "framer-motion";
import { PipelineRoad } from "@/components/layout/PipelineRoad";
import { PageHeader } from "@/components/layout/PageHeader";
import { Upload } from "@/components/layout/pipeline-icons";
import { UploadZone } from "@/components/ingest/UploadZone";
import { MetricCard } from "@/components/ui/MetricCard";
import { NeonButton } from "@/components/ui/NeonButton";
import { DataTable } from "@/components/ingest/DataTable";
import { uploadFile } from "@/lib/api";
import { useStore } from "@/lib/store";
import { useRouter } from "@/i18n/navigation";

export default function IngestPage() {
  const t = useTranslations("ingest");
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
      setIngest(res.meta, res.preview, res.warnings ?? []);
    } catch (e: any) {
      setError(e.message ?? t("..errors.uploadFailed"));
    } finally {
      setLoading(false);
    }
  }

  return (
    <div>
      <PipelineRoad />
      <PageHeader
        icon={<Upload size={28} className="text-cyan" />}
        title={t("title")}
        subtitle={t("subtitle")}
      />

      <UploadZone onFile={handleFile} loading={loading} />

      {error && (
        <div className="mt-4 p-4 rounded-md bg-red-500/10 border border-red-500/30 text-red-400 text-sm">
          {error}
        </div>
      )}

      {meta && (
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="mt-8 space-y-8">
          <div className="grid grid-cols-5 gap-3">
            <MetricCard value={meta.n_rows} label={t("rowsLabel")} index={0} />
            <MetricCard value={meta.n_cols} label={t("colsLabel")} index={1} />
            <MetricCard value={`${meta.size_kb} KB`} label={t("sizeLabel")} variant="purple" index={2} />
            <MetricCard value={meta.format} label={t("formatLabel")} variant="blue" index={3} />
            <MetricCard
              value={meta.missing_total > 0 ? `${meta.missing_total} missing` : t("cleanLabel")}
              label={t("issuesLabel")}
              variant={meta.missing_total > 0 ? "amber" : "green"}
              index={4}
            />
          </div>

          {preview && (
            <div>
              <h2 className="text-text font-semibold text-base mb-3">
                {t("preview")}{" "}
                <span className="text-text-d font-normal text-sm">— {t("previewSub")}</span>
              </h2>
              <DataTable columns={meta.columns} rows={preview} />
            </div>
          )}

          <div className="flex items-center justify-between pt-4 border-t border-border">
            <p className="text-text-m text-sm">{t("ready")}</p>
            <NeonButton onClick={() => router.push("/clean")}>
              {t("nextClean")}
            </NeonButton>
          </div>
        </motion.div>
      )}
    </div>
  );
}
