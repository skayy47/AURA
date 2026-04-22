"use client";
import { PipelineBar } from "@/components/layout/PipelineBar";
import { PageHeader } from "@/components/layout/PageHeader";
import { EmptyState } from "@/components/ui/EmptyState";
import { ExportPanel } from "@/components/docs/ExportPanel";
import { useStore } from "@/lib/store";

export default function DocsPage() {
  const { sessionId, meta } = useStore();

  if (!meta || !sessionId) return <EmptyState />;

  return (
    <div>
      <PipelineBar />
      <PageHeader icon="📄" title="Export & Documentation"
        subtitle="Download your processed dataset in multiple formats." />

      <div className="mt-8">
        <h3 className="text-lg font-semibold mb-4 text-text">Download Formats</h3>
        <ExportPanel sessionId={sessionId} />
      </div>
    </div>
  );
}
