interface Props {
  size?: "sm" | "md" | "lg";
  label?: string;
}

const dims = {
  sm: { w: 120, h: 40, fs: 28 },
  md: { w: 200, h: 72, fs: 48 },
  lg: { w: 320, h: 120, fs: 80 },
};

export function AuraLoader({ size = "md", label }: Props) {
  const { w, h, fs } = dims[size];

  return (
    <div className="aura-loader" role="status" aria-live="polite">
      <svg
        className="aura-loader-svg"
        width={w}
        height={h}
        viewBox={`0 0 ${w} ${h}`}
        aria-hidden="true"
      >
        <defs>
          <linearGradient id="auraLoaderGradient" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" stopColor="#6c3fed">
              <animate attributeName="stop-color"
                values="#6c3fed; #22d3ee; #3b82f6; #ec4899; #6c3fed"
                dur="6s" repeatCount="indefinite" />
            </stop>
            <stop offset="50%" stopColor="#22d3ee">
              <animate attributeName="stop-color"
                values="#22d3ee; #3b82f6; #ec4899; #6c3fed; #22d3ee"
                dur="6s" repeatCount="indefinite" />
            </stop>
            <stop offset="100%" stopColor="#3b82f6">
              <animate attributeName="stop-color"
                values="#3b82f6; #ec4899; #6c3fed; #22d3ee; #3b82f6"
                dur="6s" repeatCount="indefinite" />
            </stop>
          </linearGradient>
        </defs>
        <text
          x="50%"
          y="50%"
          textAnchor="middle"
          dominantBaseline="central"
          fontSize={fs}
        >
          aura
        </text>
      </svg>
      {label && <span className="aura-loader-label">{label}</span>}
      <span className="sr-only">Loading{label ? `: ${label}` : ""}</span>
    </div>
  );
}
