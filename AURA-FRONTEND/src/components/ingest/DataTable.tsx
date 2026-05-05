"use client";
import { motion } from "framer-motion";

interface Props {
  columns: string[];
  rows: Record<string, string>[];
}

export function DataTable({ columns, rows }: Props) {
  return (
    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.2 }}
      className="overflow-x-auto rounded-md border border-border">
      <table className="w-full text-sm">
        <thead>
          <tr className="bg-surface2">
            {columns.map((col) => (
              <th key={col} className="px-4 py-3 text-start text-[11px] font-bold
                                       tracking-widest uppercase text-text-m whitespace-nowrap">
                {col}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((row, ri) => (
            <tr key={ri} className={ri % 2 === 0 ? "bg-surface" : "bg-[#080e1c]"}
                style={{ transition: "background 0.15s" }}
                onMouseEnter={(e) => (e.currentTarget.style.background = "rgba(108,63,229,0.06)")}
                onMouseLeave={(e) => (e.currentTarget.style.background = "")}>
              {columns.map((col) => {
                const v = row[col] ?? "—";
                const isMissing = v === "—" || v === "nan" || v === "None";
                return (
                  <td key={col} className={`px-4 py-2.5 font-mono text-xs
                    ${isMissing ? "text-amber" : "text-text"} whitespace-nowrap`}>
                    {v}
                  </td>
                );
              })}
            </tr>
          ))}
        </tbody>
      </table>
    </motion.div>
  );
}
