"use client";
import { useState } from "react";
import { exportUrl } from "@/lib/api";

export function ExportPanel({ sessionId }: { sessionId: string }) {
  const formats = [
    { id: "csv", label: "CSV File", desc: "Best for simple tabular data" },
    { id: "xlsx", label: "Excel File", desc: "Best for sharing with stakeholders" },
    { id: "json", label: "JSON File", desc: "Best for web apps & APIs" },
    { id: "parquet", label: "Parquet", desc: "Best for big data & analytics" },
  ];

  return (
    <div className="grid grid-cols-2 gap-4">
      {formats.map(f => (
        <a 
          key={f.id} 
          href={exportUrl(sessionId, f.id as "csv" | "xlsx" | "json" | "parquet")}
          download
          className="aura-card p-6 flex flex-col gap-2 hover:border-purple/40 block text-start"
        >
          <div className="flex items-center justify-between">
            <span className="font-semibold text-lg text-text">{f.label}</span>
            <span className="text-xl">⬇️</span>
          </div>
          <p className="text-text-m text-sm">{f.desc}</p>
        </a>
      ))}
    </div>
  );
}
