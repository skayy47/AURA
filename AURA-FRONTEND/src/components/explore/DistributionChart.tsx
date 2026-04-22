"use client";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";

export function DistributionChart({ data, xKey, yKey, color = "#6C3FE5" }: { data: any[], xKey: string, yKey: string, color?: string }) {
  return (
    <div className="bg-surface border border-border rounded-md p-4 h-64 w-full">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={data} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#1E2A50" vertical={false} />
          <XAxis dataKey={xKey} stroke="#94A3B8" fontSize={12} tickLine={false} axisLine={false} />
          <YAxis stroke="#94A3B8" fontSize={12} tickLine={false} axisLine={false} />
          <Tooltip 
            cursor={{ fill: "rgba(108,63,229,0.1)" }}
            contentStyle={{ backgroundColor: "#0A1022", borderColor: "#1E2A50", borderRadius: "8px", fontSize: "12px", color: "#F1F5F9" }}
            itemStyle={{ color: "#F1F5F9" }}
          />
          <Bar dataKey={yKey} fill={color} radius={[4, 4, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
