interface Props {
  size?: number;
}

export function AuraLogo({ size = 44 }: Props) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 44 44"
      fill="none"
      aria-hidden="true"
      className="aura-logo-svg"
    >
      <defs>
        <linearGradient id="auraLogoGradient" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stopColor="#6c3fed">
            <animate attributeName="stop-color"
              values="#6c3fed; #22d3ee; #3b82f6; #ec4899; #6c3fed"
              dur="8s" repeatCount="indefinite" />
          </stop>
          <stop offset="50%" stopColor="#22d3ee">
            <animate attributeName="stop-color"
              values="#22d3ee; #3b82f6; #ec4899; #6c3fed; #22d3ee"
              dur="8s" repeatCount="indefinite" />
          </stop>
          <stop offset="100%" stopColor="#3b82f6">
            <animate attributeName="stop-color"
              values="#3b82f6; #ec4899; #6c3fed; #22d3ee; #3b82f6"
              dur="8s" repeatCount="indefinite" />
          </stop>
        </linearGradient>

        <filter id="auraLogoGlow" x="-40%" y="-40%" width="180%" height="180%">
          <feGaussianBlur stdDeviation="1.8" result="blur" />
          <feMerge>
            <feMergeNode in="blur" />
            <feMergeNode in="SourceGraphic" />
          </feMerge>
        </filter>
      </defs>

      {/* Rounded-square gradient border */}
      <rect
        x="2"
        y="2"
        width="40"
        height="40"
        rx="10"
        fill="rgba(10, 16, 34, 0.85)"
        stroke="url(#auraLogoGradient)"
        strokeWidth="1.5"
      />

      {/* "A" in Audiowide — sport-tech angular typeface */}
      <text
        x="22"
        y="31"
        textAnchor="middle"
        fontFamily="'Audiowide', sans-serif"
        fontSize="24"
        fontWeight="400"
        fill="url(#auraLogoGradient)"
        filter="url(#auraLogoGlow)"
        style={{ letterSpacing: "0.02em" }}
      >
        A
      </text>

      {/* accent spark — top-right corner notch */}
      <circle cx="34" cy="10" r="1.4" fill="url(#auraLogoGradient)" opacity="0.9" />
    </svg>
  );
}
