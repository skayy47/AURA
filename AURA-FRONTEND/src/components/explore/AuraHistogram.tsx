"use client";
import { useLocale } from "next-intl";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";
import type { HistogramBin } from "@/lib/types";

interface Props {
  title: string;
  subtitle?: string;
  data: HistogramBin[];
}

export function AuraHistogram({ title, subtitle, data }: Props) {
  const locale = useLocale();
  const isRTL = locale === "ar";
  const total = data.reduce((a, b) => a + b.count, 0) || 1;

  const fmt = new Intl.NumberFormat(locale);

  return (
    <div className="aura-card p-6">
      <div className="mb-4">
        <h3 className="font-bricolage font-bold text-text text-lg">{title}</h3>
        {subtitle && <p className="text-xs text-text-d mt-0.5">{subtitle}</p>}
      </div>

      <div className="h-64 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart
            data={data}
            margin={isRTL
              ? { top: 4, right: -16, left: 4, bottom: 0 }
              : { top: 4, right: 4, left: -16, bottom: 0 }}
          >
            <defs>
              <linearGradient id="histGradient" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor="#8B5CF6" stopOpacity={0.95} />
                <stop offset="100%" stopColor="#6C3FE5" stopOpacity={0.2} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="#1E2A50" vertical={false} />
            <XAxis
              dataKey="bin"
              stroke="#475569"
              fontSize={10}
              tickLine={false}
              axisLine={false}
              interval="preserveStartEnd"
            />
            <YAxis
              stroke="#475569"
              fontSize={10}
              tickLine={false}
              axisLine={false}
              width={40}
              orientation={isRTL ? "right" : "left"}
              tickFormatter={(v: number) => fmt.format(v)}
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
              itemStyle={{ color: "#F1F5F9" }}
              formatter={(value: number) => [
                `${fmt.format(value)} (${((value / total) * 100).toFixed(1)}%)`,
                "count",
              ]}
            />
            <Bar dataKey="count" fill="url(#histGradient)" radius={[4, 4, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
