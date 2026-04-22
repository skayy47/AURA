"use client";
import { cn } from "@/lib/utils";

interface Props {
  log: Array<{ action: string; detail: string; status: string }>;
}

export function CleaningLog({ log }: Props) {
  return (
    <div className="aura-card p-6 mt-6">
      <h3 className="text-lg font-semibold mb-4 text-text">Cleaning Log</h3>
      <div className="space-y-3">
        {log.map((l, i) => (
          <div key={i} className="flex items-start gap-3 text-sm">
            <span className={cn("mt-0.5", l.status === "success" ? "text-green" : "text-amber")}>
              {l.status === "success" ? "✓" : "⚠"}
            </span>
            <div>
              <p className="text-text font-medium">{l.action}</p>
              <p className="text-text-d text-xs font-mono mt-1">{l.detail}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
