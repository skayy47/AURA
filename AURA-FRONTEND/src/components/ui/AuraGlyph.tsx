"use client";

/**
 * AuraGlyph — the canonical "A" mark used in the logo and the robot's chest.
 * Draw once here, render anywhere. Two strokes (peak + crossbar) over a
 * 100×100 viewBox so it stays pixel-identical at every size.
 */

interface Props {
  size?: number;
  variant?: "gradient" | "outline" | "solid";
  glow?: boolean;
  animated?: boolean;
  className?: string;
  idSuffix?: string; // gradient/filter id collision guard when used 2× per page
}

export function AuraGlyph({
  size = 44,
  variant = "gradient",
  glow = true,
  animated = true,
  className,
  idSuffix = "",
}: Props) {
  const gid = `auraGlyphG${idSuffix}`;
  const fid = `auraGlyphF${idSuffix}`;
  const stroke = variant === "outline" ? "currentColor" : `url(#${gid})`;
  const filter = glow ? `url(#${fid})` : undefined;

  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 100 100"
      fill="none"
      aria-hidden="true"
      className={className}
    >
      <defs>
        <linearGradient id={gid} x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stopColor="#6c3fed">
            {animated && (
              <animate
                attributeName="stop-color"
                values="#6c3fed;#22d3ee;#3b82f6;#ec4899;#6c3fed"
                dur="9s"
                repeatCount="indefinite"
              />
            )}
          </stop>
          <stop offset="55%" stopColor="#22d3ee">
            {animated && (
              <animate
                attributeName="stop-color"
                values="#22d3ee;#3b82f6;#ec4899;#6c3fed;#22d3ee"
                dur="9s"
                repeatCount="indefinite"
              />
            )}
          </stop>
          <stop offset="100%" stopColor="#3b82f6">
            {animated && (
              <animate
                attributeName="stop-color"
                values="#3b82f6;#ec4899;#6c3fed;#22d3ee;#3b82f6"
                dur="9s"
                repeatCount="indefinite"
              />
            )}
          </stop>
        </linearGradient>

        {glow && (
          <filter id={fid} x="-40%" y="-40%" width="180%" height="180%">
            <feGaussianBlur stdDeviation="2.4" result="b" />
            <feMerge>
              <feMergeNode in="b" />
              <feMergeNode in="SourceGraphic" />
            </feMerge>
          </filter>
        )}
      </defs>

      {/* Two diagonal blades forming the A peak */}
      <path
        d="M 14 90 L 50 12 L 86 90"
        stroke={stroke}
        strokeWidth="11"
        strokeLinecap="round"
        strokeLinejoin="round"
        filter={filter}
      />
      {/* Crossbar */}
      <path
        d="M 30 62 L 70 62"
        stroke={stroke}
        strokeWidth="9"
        strokeLinecap="round"
        filter={filter}
      />
    </svg>
  );
}
