"use client";
import { useMemo } from "react";
import { useLocale } from "next-intl";
import {
  ScatterChart,
  Scatter,
  XAxis,
  YAxis,
  ZAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";

interface Point { x: number; y: number }

interface Props {
  title: string;
  subtitle?: string;
  xLabel: string;
  yLabel: string;
  points: Point[];
}

function regression(points: Point[]) {
  const n = points.length;
  if (n < 2) return null;
  let sx = 0, sy = 0;
  for (const p of points) { sx += p.x; sy += p.y; }
  const mx = sx / n, my = sy / n;
  let num = 0, dxx = 0, dyy = 0;
  for (const p of points) {
    const dx = p.x - mx, dy = p.y - my;
    num += dx * dy;
    dxx += dx * dx;
    dyy += dy * dy;
  }
  if (dxx === 0 || dyy === 0) return null;
  const slope = num / dxx;
  const intercept = my - slope * mx;
  const r = num / Math.sqrt(dxx * dyy);
  return { slope, intercept, r2: r * r };
}

export function AuraScatter({ title, subtitle, xLabel, yLabel, points }: Props) {
  const locale = useLocale();
  const isRTL = locale === "ar";
  const fmt = new Intl.NumberFormat(locale, { maximumFractionDigits: 3 });

  const reg = useMemo(() => regression(points), [points]);
  const xMin = useMemo(() => Math.min(...points.map((p) => p.x)), [points]);
  const xMax = useMemo(() => Math.max(...points.map((p) => p.x)), [points]);
  const regLine = useMemo(() => {
    if (!reg) return [];
    return [
      { x: xMin, y: reg.slope * xMin + reg.intercept },
      { x: xMax, y: reg.slope * xMax + reg.intercept },
    ];
  }, [reg, xMin, xMax]);

  return (
    <div className="aura-card p-6">
      <div className="flex items-start justify-between mb-4">
        <div>
          <h3 className="font-bricolage font-bold text-text text-lg">{title}</h3>
          {subtitle && <p className="text-xs text-text-d mt-0.5">{subtitle}</p>}
        </div>
        {reg && (
          <div className="font-geist-mono text-xs text-text-m">
            R² = <span className="text-purple-l font-bold">{fmt.format(reg.r2)}</span>
          </div>
        )}
      </div>

      <div className="h-64 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <ScatterChart
            margin={isRTL
              ? { top: 6, right: 0, bottom: 6, left: 6 }
              : { top: 6, right: 6, bottom: 6, left: 0 }}
          >
            <CartesianGrid strokeDasharray="3 3" stroke="#1E2A50" />
            <XAxis
              dataKey="x"
              name={xLabel}
              type="number"
              stroke="#475569"
              fontSize={10}
              tickLine={false}
              axisLine={false}
              tickFormatter={(v: number) => fmt.format(v)}
            />
            <YAxis
              dataKey="y"
              name={yLabel}
              type="number"
              stroke="#475569"
              fontSize={10}
              tickLine={false}
              axisLine={false}
              width={40}
              orientation={isRTL ? "right" : "left"}
              tickFormatter={(v: number) => fmt.format(v)}
            />
            <ZAxis range={[30, 30]} />
            <Tooltip
              cursor={{ strokeDasharray: "3 3", stroke: "#22D3EE" }}
              contentStyle={{
                backgroundColor: "#0A1022",
                borderColor: "#1E2A50",
                borderRadius: 10,
                fontSize: 12,
                color: "#F1F5F9",
                fontFamily: "Geist Mono, monospace",
              }}
              formatter={(value: number, name: string) => [fmt.format(value), name]}
              labelFormatter={() => ""}
            />
            <Scatter data={points} fill="#8B5CF6" opacity={0.55} />
            {reg && (
              <Scatter
                data={regLine}
                line={{ stroke: "#22D3EE", strokeWidth: 2 }}
                shape={() => <g />}
                legendType="none"
              />
            )}
          </ScatterChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
