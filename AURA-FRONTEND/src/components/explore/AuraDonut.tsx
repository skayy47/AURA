"use client";
import { useLocale } from "next-intl";
import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer } from "recharts";

interface Segment {
  label: string;
  value: number;
  pct: number;
}

interface Props {
  title: string;
  subtitle?: string;
  segments: Segment[];
}

const PALETTE = ["#8B5CF6", "#22D3EE", "#3B82F6", "#00FFB2", "#F59E0B", "#EC4899", "#6C3FE5", "#94A3B8"];

export function AuraDonut({ title, subtitle, segments }: Props) {
  const locale = useLocale();
  const fmt = new Intl.NumberFormat(locale);
  const total = segments.reduce((a, b) => a + b.value, 0);

  return (
    <div className="aura-card p-6">
      <div className="mb-4">
        <h3 className="font-bricolage font-bold text-text text-lg">{title}</h3>
        {subtitle && <p className="text-xs text-text-d mt-0.5">{subtitle}</p>}
      </div>

      <div className="flex items-center gap-6">
        <div className="relative h-52 w-52 shrink-0">
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie
                data={segments}
                dataKey="value"
                nameKey="label"
                innerRadius={58}
                outerRadius={92}
                paddingAngle={2}
                stroke="none"
              >
                {segments.map((_, i) => (
                  <Cell key={i} fill={PALETTE[i % PALETTE.length]} />
                ))}
              </Pie>
              <Tooltip
                contentStyle={{
                  backgroundColor: "#0A1022",
                  borderColor: "#1E2A50",
                  borderRadius: 10,
                  fontSize: 12,
                  color: "#F1F5F9",
                  fontFamily: "Geist Mono, monospace",
                }}
                formatter={(value: number, name: string) => [
                  `${fmt.format(value)} (${((value / (total || 1)) * 100).toFixed(1)}%)`,
                  name,
                ]}
              />
            </PieChart>
          </ResponsiveContainer>
          <div className="absolute inset-0 flex flex-col items-center justify-center pointer-events-none">
            <span className="font-geist-mono font-bold text-xl text-text tabular-nums">{fmt.format(total)}</span>
            <span className="text-[0.6rem] uppercase tracking-[0.12em] text-text-d">total</span>
          </div>
        </div>

        <ul className="flex-1 min-w-0 space-y-2">
          {segments.map((s, i) => (
            <li key={s.label} className="flex items-center gap-2.5">
              <span className="w-2.5 h-2.5 rounded-sm shrink-0" style={{ background: PALETTE[i % PALETTE.length] }} />
              <span className="text-sm text-text-m truncate flex-1" title={s.label}>{s.label}</span>
              <span className="font-geist-mono text-sm text-text tabular-nums">{s.pct}%</span>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}
