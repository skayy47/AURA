import { cn } from "@/lib/utils";

interface Props {
  size?: number;
  className?: string;
}

export function BotMiniAvatar({ size = 32, className }: Props) {
  return (
    <div
      className={cn(
        "shrink-0 rounded-full bg-gradient-to-br from-[#0E162E] to-[#070C1A] border border-[rgba(108,63,237,0.5)]",
        "flex items-center justify-center shadow-[0_0_8px_rgba(108,63,237,0.25)]",
        className
      )}
      style={{ width: size, height: size }}
      aria-label="AURA"
    >
      <svg viewBox="0 0 32 32" width={size * 0.72} height={size * 0.72}>
        <defs>
          <linearGradient id={`mini-edge-${size}`} x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="#6C3FED" />
            <stop offset="100%" stopColor="#22D3EE" />
          </linearGradient>
        </defs>
        <line x1="16" y1="6" x2="16" y2="2" stroke="rgba(108,63,237,0.6)" strokeWidth="1" strokeLinecap="round" />
        <circle cx="16" cy="2.2" r="1.6" fill="#6C3FED" />
        <ellipse cx="16" cy="16" rx="11" ry="9.5" fill="#0A1022" stroke={`url(#mini-edge-${size})`} strokeWidth="0.9" />
        <path d="M 6 16 Q 16 22 26 16 L 26 22 Q 16 26 6 22 Z" fill="#070C1A" opacity="0.85" />
        <rect x="9.5" y="14.5" width="4.5" height="2.4" rx="1" fill="#22D3EE" style={{ filter: "drop-shadow(0 0 2px rgba(34,211,238,0.7))" }} />
        <rect x="18" y="14.5" width="4.5" height="2.4" rx="1" fill="#22D3EE" style={{ filter: "drop-shadow(0 0 2px rgba(34,211,238,0.7))" }} />
      </svg>
    </div>
  );
}
