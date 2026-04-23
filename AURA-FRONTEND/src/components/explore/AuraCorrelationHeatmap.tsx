"use client";
import { useState, useMemo } from "react";
import { motion } from "framer-motion";
import type { CorrelationMatrix } from "@/lib/types";

interface Props {
  data: CorrelationMatrix;
  onColumnClick?: (col: string) => void;
}

function correlationColor(r: number): string {
  // -1 (red #EF4444) → 0 (slate #1E293B) → +1 (purple #6C3FE5)
  const t = Math.max(-1, Math.min(1, r));
  if (t >= 0) {
    // lerp slate → purple
    return lerpHex("#1E293B", "#6C3FE5", t);
  }
  return lerpHex("#1E293B", "#EF4444", -t);
}

function lerpHex(a: string, b: string, t: number): string {
  const pa = parseInt(a.slice(1), 16);
  const pb = parseInt(b.slice(1), 16);
  const ar = (pa >> 16) & 0xff, ag = (pa >> 8) & 0xff, ab = pa & 0xff;
  const br = (pb >> 16) & 0xff, bg = (pb >> 8) & 0xff, bb = pb & 0xff;
  const r = Math.round(ar + (br - ar) * t);
  const g = Math.round(ag + (bg - ag) * t);
  const b2 = Math.round(ab + (bb - ab) * t);
  return `rgb(${r},${g},${b2})`;
}

function strengthLabel(r: number): string {
  const a = Math.abs(r);
  if (a > 0.7) return "Strong";
  if (a > 0.4) return "Moderate";
  if (a > 0.2) return "Weak";
  return "";
}

export function AuraCorrelationHeatmap({ data, onColumnClick }: Props) {
  const cols = data.columns;
  const matrix = data.matrix.data;
  const n = cols.length;
  const [hover, setHover] = useState<{ i: number; j: number } | null>(null);

  const labelSpace = 120;
  const topSpace = 70;
  const cellSize = useMemo(() => {
    const available = 520;
    return Math.max(24, Math.floor((available - labelSpace) / Math.max(n, 1)));
  }, [n]);
  const totalSize = labelSpace + cellSize * n;

  return (
    <div className="aura-card p-6">
      <div className="flex items-baseline justify-between mb-4">
        <div>
          <h3 className="font-bricolage font-bold text-text text-lg">
            Correlation Matrix
          </h3>
          <p className="text-xs text-text-d mt-0.5">
            {n} numeric columns · purple = positive, red = negative
          </p>
        </div>
        {hover && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="font-geist-mono text-xs text-text-m"
          >
            <span className="text-purple-l">{cols[hover.i]}</span>
            <span className="mx-1 text-text-d">×</span>
            <span className="text-purple-l">{cols[hover.j]}</span>
            <span className="mx-2 text-text-d">|</span>
            <span
              className="font-bold"
              style={{ color: correlationColor(matrix[hover.i][hover.j]) }}
            >
              r = {matrix[hover.i][hover.j].toFixed(3)}
            </span>
            {strengthLabel(matrix[hover.i][hover.j]) && (
              <span className="ml-2 text-text-d">
                ({strengthLabel(matrix[hover.i][hover.j])})
              </span>
            )}
          </motion.div>
        )}
      </div>

      <div className="overflow-auto">
        <svg
          width={totalSize}
          height={topSpace + cellSize * n}
          className="min-w-full"
        >
          {/* Column headers (rotated) */}
          {cols.map((col, j) => (
            <text
              key={`colhdr-${j}`}
              x={labelSpace + j * cellSize + cellSize / 2}
              y={topSpace - 8}
              textAnchor="end"
              transform={`rotate(-45, ${labelSpace + j * cellSize + cellSize / 2}, ${topSpace - 8})`}
              className="fill-text-m font-geist-mono cursor-pointer hover:fill-text"
              style={{ fontSize: 10 }}
              onClick={() => onColumnClick?.(col)}
            >
              {col.length > 14 ? col.slice(0, 12) + "…" : col}
            </text>
          ))}

          {/* Row labels */}
          {cols.map((col, i) => (
            <text
              key={`rowhdr-${i}`}
              x={labelSpace - 8}
              y={topSpace + i * cellSize + cellSize / 2 + 3}
              textAnchor="end"
              className="fill-text-m font-geist-mono cursor-pointer hover:fill-text"
              style={{ fontSize: 10 }}
              onClick={() => onColumnClick?.(col)}
            >
              {col.length > 14 ? col.slice(0, 12) + "…" : col}
            </text>
          ))}

          {/* Cells */}
          {matrix.map((row, i) =>
            row.map((value, j) => {
              const isDiag = i === j;
              const strength = strengthLabel(value);
              const showLabel = cellSize >= 40 && !isDiag && strength === "Strong";
              return (
                <g key={`cell-${i}-${j}`}>
                  <motion.rect
                    initial={{ scale: 0, opacity: 0 }}
                    animate={{ scale: 1, opacity: 1 }}
                    transition={{
                      delay: (i * n + j) * 0.012,
                      type: "spring",
                      stiffness: 300,
                      damping: 22,
                    }}
                    x={labelSpace + j * cellSize + 1}
                    y={topSpace + i * cellSize + 1}
                    width={cellSize - 2}
                    height={cellSize - 2}
                    rx={3}
                    fill={isDiag ? "#2A1D4D" : correlationColor(value)}
                    stroke={hover?.i === i && hover?.j === j ? "#22D3EE" : "transparent"}
                    strokeWidth={hover?.i === i && hover?.j === j ? 2 : 0}
                    style={{ cursor: "pointer", transformOrigin: "center" }}
                    onMouseEnter={() => setHover({ i, j })}
                    onMouseLeave={() => setHover(null)}
                  />
                  {showLabel && (
                    <text
                      x={labelSpace + j * cellSize + cellSize / 2}
                      y={topSpace + i * cellSize + cellSize / 2 + 3}
                      textAnchor="middle"
                      className="fill-white font-geist-mono font-bold pointer-events-none"
                      style={{ fontSize: 9 }}
                    >
                      {value.toFixed(2)}
                    </text>
                  )}
                </g>
              );
            })
          )}
        </svg>
      </div>

      {data.top_pairs.length > 0 && (
        <div className="mt-4 pt-4 border-t border-white/[0.06]">
          <p className="text-[0.65rem] font-bold tracking-widest uppercase text-text-d mb-2">
            Top pairs
          </p>
          <div className="flex flex-wrap gap-2">
            {data.top_pairs.slice(0, 5).map((p) => (
              <div
                key={`${p.col_a}-${p.col_b}`}
                className="text-xs font-geist-mono px-2.5 py-1 rounded-full border"
                style={{
                  borderColor: p.r >= 0 ? "rgba(108,63,237,0.4)" : "rgba(239,68,68,0.4)",
                  background: p.r >= 0 ? "rgba(108,63,237,0.08)" : "rgba(239,68,68,0.08)",
                  color: p.r >= 0 ? "#A78BFA" : "#FCA5A5",
                }}
              >
                {p.col_a} × {p.col_b} · r = {p.r.toFixed(2)}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
