"use client";
import { useTranslations } from "next-intl";
import { PipelineRoad } from "@/components/layout/PipelineRoad";
import { PageHeader } from "@/components/layout/PageHeader";
import { FileText } from "@/components/layout/pipeline-icons";
import { EmptyState } from "@/components/ui/EmptyState";
import { ExportPanel } from "@/components/docs/ExportPanel";
import { useStore } from "@/lib/store";

export default function DocsPage() {
  const t = useTranslations("docs");
  const { sessionId, meta } = useStore();

  if (!meta || !sessionId) return <EmptyState />;

  return (
    <div>
      <PipelineRoad />
      <PageHeader
        icon={<FileText size={28} className="text-text-m" />}
        title={t("title")}
        subtitle={t("subtitle")}
      />

      <div className="mt-8">
        <ExportPanel sessionId={sessionId} />
      </div>
    </div>
  );
}
