export function AuroraBackground() {
  return (
    <div className="aura-bg-aurora" aria-hidden="true">
      <div className="aura-bg-blob aura-bg-blob-1" />
      <div className="aura-bg-blob aura-bg-blob-2" />
      <div className="aura-bg-blob aura-bg-blob-3" />

      <div className="aura-bg-waves">
        <svg className="aura-bg-wave aura-bg-wave-1" viewBox="0 0 2400 320" preserveAspectRatio="none">
          <defs>
            <linearGradient id="waveGrad1" x1="0" x2="1" y1="0" y2="0">
              <stop offset="0%" stopColor="#6c3fed" />
              <stop offset="50%" stopColor="#22d3ee" />
              <stop offset="100%" stopColor="#3b82f6" />
            </linearGradient>
          </defs>
          <path
            d="M0,160 C300,60 600,260 1200,160 C1800,60 2100,260 2400,160 L2400,320 L0,320 Z"
            fill="url(#waveGrad1)"
          />
        </svg>

        <svg className="aura-bg-wave aura-bg-wave-2" viewBox="0 0 2400 320" preserveAspectRatio="none">
          <defs>
            <linearGradient id="waveGrad2" x1="0" x2="1" y1="0" y2="0">
              <stop offset="0%" stopColor="#3b82f6" />
              <stop offset="100%" stopColor="#6c3fed" />
            </linearGradient>
          </defs>
          <path
            d="M0,200 C400,100 800,300 1200,200 C1600,100 2000,300 2400,200 L2400,320 L0,320 Z"
            fill="url(#waveGrad2)"
          />
        </svg>

        <svg className="aura-bg-wave aura-bg-wave-3" viewBox="0 0 2400 320" preserveAspectRatio="none">
          <path
            d="M0,240 C300,180 900,300 1200,240 C1500,180 2100,300 2400,240 L2400,320 L0,320 Z"
            fill="#22d3ee"
          />
        </svg>
      </div>
    </div>
  );
}
