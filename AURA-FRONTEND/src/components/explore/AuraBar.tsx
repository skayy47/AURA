"use client";
import { useLocale } from "next-intl";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Cell,
  ResponsiveContainer,
  LabelList,
} from "recharts";

interface BarDatum {
  label: string;
  value: number;
}

interface Props {
  title: string;
  subtitle?: string;
  bars: BarDatum[];
}

export function AuraBar({ title, subtitle, bars }: Props) {
  const locale = useLocale();
  const isRTL = locale === "ar";
  const fmt = new Intl.NumberFormat(locale, { maximumFractionDigits: 2 });
  const compact = new Intl.NumberFormat(locale, { maximumFractionDigits: 1, notation: "compact" });
  const hasNegative = bars.some((b) => b.value < 0);
  // Height scales with bar count so labels never collide.
  const height = Math.max(176, bars.length * 34 + 24);

  return (
    <div className="aura-card p-6">
      <div className="mb-4">
        <h3 className="font-bricolage font-bold text-text text-lg">{title}</h3>
        {subtitle && <p className="text-xs text-text-d mt-0.5">{subtitle}</p>}
      </div>

      <div style={{ height }} className="w-full">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart
            layout="vertical"
            data={bars}
            margin={isRTL ? { top: 0, right: 8, left: 8, bottom: 0 } : { top: 0, right: 36, left: 8, bottom: 0 }}
          >
            <defs>
              <linearGradient id="barPos" x1="0" y1="0" x2="1" y2="0">
                <stop offset="0%" stopColor="#6C3FE5" stopOpacity={0.5} />
                <stop offset="100%" stopColor="#8B5CF6" stopOpacity={1} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="#1E2A50" horizontal={false} />
            <XAxis
              type="number"
              stroke="#475569"
              fontSize={10}
              tickLine={false}
              axisLine={false}
              reversed={isRTL}
              tickFormatter={(v: number) => compact.format(v)}
            />
            <YAxis
              type="category"
              dataKey="label"
              stroke="#94A3B8"
              fontSize={11}
              tickLine={false}
              axisLine={false}
              width={104}
              orientation={isRTL ? "right" : "left"}
              tickFormatter={(v: string) => (v.length > 14 ? v.slice(0, 13) + "…" : v)}
            />
            <Tooltip
              cursor={{ fill: "rgba(108,63,229,0.08)" }}
              contentStyle={{
                backgroundColor: "#0A1022",
                borderColor: "#1E2A50",
                borderRadius: 10,
                fontSize: 12,
                color: "#F1F5F9",
                fontFamily: "Geist Mono, monospace",
              }}
              formatter={(value: number) => [fmt.format(value), ""]}
            />
            <Bar dataKey="value" radius={[0, 5, 5, 0]} barSize={20}>
              {bars.map((b, i) => (
                <Cell key={i} fill={b.value < 0 ? "#fb7185" : hasNegative ? "#8B5CF6" : "url(#barPos)"} />
              ))}
              <LabelList
                dataKey="value"
                position={isRTL ? "left" : "right"}
                formatter={(v: number) => compact.format(v)}
                style={{ fill: "#94A3B8", fontSize: 10, fontFamily: "Geist Mono, monospace" }}
              />
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
