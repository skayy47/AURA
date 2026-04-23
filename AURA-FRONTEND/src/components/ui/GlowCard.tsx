"use client";
import { useId } from "react";
import { cn } from "@/lib/utils";

type Accent = "purple" | "cyan" | "blue";
type Intensity = "low" | "mid" | "high";

interface Props {
  accent?: Accent;
  intensity?: Intensity;
  className?: string;
  innerClassName?: string;
  children: React.ReactNode;
}

const accentStops: Record<Accent, [string, string]> = {
  purple: ["#6c3fed", "#22d3ee"],
  cyan:   ["#22d3ee", "#3b82f6"],
  blue:   ["#3b82f6", "#6c3fed"],
};

const intensityOpacity: Record<Intensity, number> = {
  low: 0.2,
  mid: 0.35,
  high: 0.55,
};

export function GlowCard({
  accent = "purple",
  intensity = "mid",
  className,
  innerClassName,
  children,
}: Props) {
  const id = useId().replace(/:/g, "");
  const gid = `glow-${id}`;
  const [from, to] = accentStops[accent];

  return (
    <div
      className={cn("aura-glow-card", className)}
      style={{ ["--glow-opacity" as any]: intensityOpacity[intensity] }}
    >
      <div className="aura-glow-card-halo" aria-hidden="true" />
      <svg className="aura-glow-card-border" aria-hidden="true">
        <defs>
          <linearGradient id={gid} x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor={from} />
            <stop offset="100%" stopColor={to} />
          </linearGradient>
        </defs>
        <rect
          x="1"
          y="1"
          width="calc(100% - 2px)"
          height="calc(100% - 2px)"
          rx="15"
          fill="none"
          stroke={`url(#${gid})`}
          strokeWidth="1.2"
        />
      </svg>
      <div className={cn("aura-glow-card-inner p-5", innerClassName)}>
        {children}
      </div>
    </div>
  );
}
