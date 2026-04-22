import Link from "next/link";

export function EmptyState() {
  return (
    <div className="flex flex-col items-center justify-center min-h-[50vh] text-center">
      <div className="w-20 h-20 rounded-full bg-surface2 border border-border flex items-center justify-center text-4xl mb-4">📂</div>
      <h2 className="text-text font-semibold text-lg">No dataset loaded</h2>
      <p className="text-text-m text-sm mt-1 mb-6">Go to Ingest to upload your data file.</p>
      <Link href="/ingest" className="aura-btn">Go to Ingest →</Link>
    </div>
  );
}
