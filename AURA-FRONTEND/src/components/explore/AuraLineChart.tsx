"use client";
import { useMemo } from "react";
import { useLocale } from "next-intl";
import {
  LineChart,
  Line,
  Area,
  ComposedChart,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";

interface LinePoint {
  x: string;
  value: number;
}
interface Series {
  name: string;
  points: LinePoint[];
}

interface Props {
  title: string;
  subtitle?: string;
  /** Single-series data. */
  points?: LinePoint[];
  /** Multi-series data (overrides points when present). */
  series?: Series[];
}

const PALETTE = ["#8B5CF6", "#22D3EE", "#3B82F6", "#00FFB2", "#F59E0B"];

export function AuraLineChart({ title, subtitle, points = [], series = [] }: Props) {
  const locale = useLocale();
  const isRTL = locale === "ar";
  const fmt = new Intl.NumberFormat(locale, { maximumFractionDigits: 2, notation: "compact" });
  const multi = series.length > 0;

  // Merge multi-series into a single row-per-x dataset for recharts.
  const { data, keys } = useMemo(() => {
    if (!multi) return { data: points, keys: ["value"] };
    const byX = new Map<string, Record<string, number | string>>();
    for (const s of series) {
      for (const p of s.points) {
        const row = byX.get(p.x) ?? { x: p.x };
        row[s.name] = p.value;
        byX.set(p.x, row);
      }
    }
    const rows = Array.from(byX.values()).sort((a, b) =>
      String(a.x).localeCompare(String(b.x))
    );
    return { data: rows, keys: series.map((s) => s.name) };
  }, [multi, points, series]);

  const Chart = multi ? LineChart : ComposedChart;

  return (
    <div className="aura-card p-6">
      <div className="mb-4">
        <h3 className="font-bricolage font-bold text-text text-lg">{title}</h3>
        {subtitle && <p className="text-xs text-text-d mt-0.5">{subtitle}</p>}
      </div>

      <div className="h-64 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <Chart
            data={data as object[]}
            margin={isRTL ? { top: 8, right: -16, left: 4, bottom: 0 } : { top: 8, right: 4, left: -16, bottom: 0 }}
          >
            <defs>
              <linearGradient id="lineArea" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor="#8B5CF6" stopOpacity={0.35} />
                <stop offset="100%" stopColor="#8B5CF6" stopOpacity={0} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="#1E2A50" vertical={false} />
            <XAxis
              dataKey="x"
              stroke="#475569"
              fontSize={10}
              tickLine={false}
              axisLine={false}
              interval="preserveStartEnd"
              minTickGap={28}
            />
            <YAxis
              stroke="#475569"
              fontSize={10}
              tickLine={false}
              axisLine={false}
              width={44}
              orientation={isRTL ? "right" : "left"}
              tickFormatter={(v: number) => fmt.format(v)}
            />
            <Tooltip
              cursor={{ stroke: "#22D3EE", strokeDasharray: "3 3" }}
              contentStyle={{
                backgroundColor: "#0A1022",
                borderColor: "#1E2A50",
                borderRadius: 10,
                fontSize: 12,
                color: "#F1F5F9",
                fontFamily: "Geist Mono, monospace",
              }}
              formatter={(value: number, name: string) => [fmt.format(value), name === "value" ? "" : name]}
            />
            {multi && <Legend wrapperStyle={{ fontSize: 11, color: "#94A3B8" }} />}
            {!multi && (
              <Area type="monotone" dataKey="value" stroke="none" fill="url(#lineArea)" />
            )}
            {keys.map((k, i) => (
              <Line
                key={k}
                type="monotone"
                dataKey={k}
                stroke={PALETTE[i % PALETTE.length]}
                strokeWidth={2.25}
                dot={false}
                activeDot={{ r: 4, strokeWidth: 0 }}
              />
            ))}
          </Chart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
