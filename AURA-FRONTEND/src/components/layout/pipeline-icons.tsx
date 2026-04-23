interface IconProps {
  size?: number;
  color?: string;
  strokeWidth?: number;
}

const base = (size: number, strokeWidth: number, color: string) => ({
  width: size,
  height: size,
  viewBox: "0 0 24 24",
  fill: "none" as const,
  stroke: color,
  strokeWidth,
  strokeLinecap: "round" as const,
  strokeLinejoin: "round" as const,
  "aria-hidden": true as const,
});

export function Upload({ size = 24, color = "currentColor", strokeWidth = 2 }: IconProps) {
  return (
    <svg {...base(size, strokeWidth, color)}>
      <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
      <polyline points="17 8 12 3 7 8" />
      <line x1="12" x2="12" y1="3" y2="15" />
    </svg>
  );
}

export function Sparkles({ size = 24, color = "currentColor", strokeWidth = 2 }: IconProps) {
  return (
    <svg {...base(size, strokeWidth, color)}>
      <path d="m12 3-1.912 5.813a2 2 0 0 1-1.275 1.275L3 12l5.813 1.912a2 2 0 0 1 1.275 1.275L12 21l1.912-5.813a2 2 0 0 1 1.275-1.275L21 12l-5.813-1.912a2 2 0 0 1-1.275-1.275Z" />
      <path d="M5 3v4" />
      <path d="M19 17v4" />
      <path d="M3 5h4" />
      <path d="M17 19h4" />
    </svg>
  );
}

export function BarChart3({ size = 24, color = "currentColor", strokeWidth = 2 }: IconProps) {
  return (
    <svg {...base(size, strokeWidth, color)}>
      <path d="M3 3v18h18" />
      <path d="M18 17V9" />
      <path d="M13 17V5" />
      <path d="M8 17v-3" />
    </svg>
  );
}

export function Bot({ size = 24, color = "currentColor", strokeWidth = 2 }: IconProps) {
  return (
    <svg {...base(size, strokeWidth, color)}>
      <path d="M12 8V4H8" />
      <rect width="16" height="12" x="4" y="8" rx="2" />
      <path d="M2 14h2" />
      <path d="M20 14h2" />
      <path d="M15 13v2" />
      <path d="M9 13v2" />
    </svg>
  );
}

export function FileText({ size = 24, color = "currentColor", strokeWidth = 2 }: IconProps) {
  return (
    <svg {...base(size, strokeWidth, color)}>
      <path d="M15 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7Z" />
      <polyline points="14 2 14 8 20 8" />
      <line x1="16" x2="8" y1="13" y2="13" />
      <line x1="16" x2="8" y1="17" y2="17" />
      <polyline points="10 9 9 9 8 9" />
    </svg>
  );
}

export function Check({ size = 24, color = "currentColor", strokeWidth = 2.5 }: IconProps) {
  return (
    <svg {...base(size, strokeWidth, color)}>
      <polyline points="20 6 9 17 4 12" />
    </svg>
  );
}
