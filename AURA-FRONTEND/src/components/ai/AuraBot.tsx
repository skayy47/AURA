"use client";

import { motion } from "framer-motion";

export type BotState = "idle" | "listening" | "thinking" | "speaking" | "celebrate" | "error";

interface AuraBotProps {
  state?: BotState;
  size?: number;
  onClick?: () => void;
  ariaLabel?: string;
}

const CYAN = "#22D3EE";
const PURPLE = "#6C3FED";
const AMBER = "#F59E0B";
// ViewBox matches the portfolio live-demo robot exactly
const VBOX_W = 280;
const VBOX_H = 360;

export function AuraBot({
  state = "idle",
  size = 200,
  onClick,
  ariaLabel = "AURA AI assistant",
}: AuraBotProps) {
  const aspect = VBOX_W / VBOX_H;
  // Accent colour shifts to amber on error (eyes, strokes, logo)
  const c = state === "error" ? AMBER : CYAN;
  const antennaC = state === "error" ? AMBER : PURPLE;

  // ------------------------------------------------------------------
  // Animation variants (Framer Motion equivalents of the CSS keyframes)
  // ------------------------------------------------------------------

  // botFloat: 5.5s ease-in-out, translateY -12px at 50%
  const floatAnim =
    state === "celebrate" ? { y: [0, -22, -16, -22, 0] } : { y: [0, -12, 0] };
  const floatTrans =
    state === "celebrate"
      ? { duration: 0.65, repeat: Infinity, ease: "easeInOut" as const }
      : { duration: 5.5, repeat: Infinity, ease: "easeInOut" as const };

  // botBob: left 4s, right 4.6s delay 0.4s, translateY -7px at 50%
  const bobTrans = (dur: number, delay = 0) => ({
    duration: dur,
    repeat: Infinity,
    ease: "easeInOut" as const,
    delay,
  });

  // botBlink: scaleY 1→1→0.12→1→1 at 0% 90% 93% 96% 100%
  const blinkAnim = { scaleY: [1, 1, 0.12, 1, 1] };
  const blinkTrans = {
    duration: 5,
    repeat: Infinity,
    ease: "linear" as const,
    times: [0, 0.9, 0.93, 0.96, 1],
  };

  // botGlow: opacity 0.55 at 50%
  const glowAnim = { opacity: [1, 0.55, 1] };
  const logoGlowTrans = { duration: 2.8, repeat: Infinity, ease: "easeInOut" as const };
  const antennaGlowTrans = {
    duration: state === "listening" ? 1.1 : 2,
    repeat: Infinity,
    ease: "easeInOut" as const,
  };

  // botShadowPulse: opacity 0.28→0.16→0.28, scaleX 1→0.86→1
  const shadowAnim = { opacity: [0.28, 0.16, 0.28], scaleX: [1, 0.86, 1] };
  const shadowTrans = { duration: 5.5, repeat: Infinity, ease: "easeInOut" as const };

  return (
    <motion.div
      style={{ width: size * aspect, height: size }}
      onClick={onClick}
      className={onClick ? "cursor-pointer select-none" : "select-none"}
      whileHover={onClick ? { scale: 1.03 } : undefined}
      transition={{ type: "spring", stiffness: 280, damping: 24 }}
      role="img"
      aria-label={ariaLabel}
    >
      <svg
        viewBox={`0 0 ${VBOX_W} ${VBOX_H}`}
        width="100%"
        height="100%"
        overflow="visible"
        aria-hidden
      >
        <defs>
          <linearGradient id="ab-head" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0" stopColor="#1c2750" />
            <stop offset="1" stopColor="#0b1130" />
          </linearGradient>
          <linearGradient id="ab-body" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0" stopColor="#161f44" />
            <stop offset="1" stopColor="#090e26" />
          </linearGradient>
          <linearGradient id="ab-logo" x1="0" y1="0" x2="1" y2="1">
            <stop offset="0" stopColor={c} />
            <stop offset="1" stopColor={PURPLE} />
          </linearGradient>
        </defs>

        {/* Ground shadow — stays fixed while body floats */}
        <motion.ellipse
          cx={140}
          cy={342}
          rx={64}
          ry={9}
          fill={c}
          animate={shadowAnim}
          transition={shadowTrans}
          style={{ filter: "blur(7px)", transformBox: "fill-box", transformOrigin: "center" }}
        />

        {/* Error shake wrapper */}
        <motion.g
          animate={
            state === "error"
              ? { x: [0, -6, 6, -5, 5, -3, 3, 0] }
              : { x: 0 }
          }
          transition={
            state === "error"
              ? { duration: 0.5, repeat: Infinity, repeatDelay: 1.8 }
              : { duration: 0.3 }
          }
        >
          {/* ── FLOAT GROUP — everything bobs up/down together ── */}
          <motion.g animate={floatAnim} transition={floatTrans}>

            {/* Left planet hand */}
            <motion.g
              animate={{ y: [0, -7, 0] }}
              transition={bobTrans(4)}
            >
              <circle
                cx={46} cy={252} r={16}
                fill="url(#ab-body)"
                stroke={c}
                strokeOpacity={0.45}
              />
              <ellipse
                cx={46} cy={252} rx={25} ry={6.5}
                stroke={c}
                strokeOpacity={0.5}
                fill="none"
                transform="rotate(-20 46 252)"
              />
            </motion.g>

            {/* Right planet hand */}
            <motion.g
              animate={{ y: [0, -7, 0] }}
              transition={bobTrans(4.6, 0.4)}
            >
              <circle
                cx={234} cy={252} r={16}
                fill="url(#ab-body)"
                stroke={c}
                strokeOpacity={0.45}
              />
              <ellipse
                cx={234} cy={252} rx={25} ry={6.5}
                stroke={c}
                strokeOpacity={0.5}
                fill="none"
                transform="rotate(20 234 252)"
              />
            </motion.g>

            {/* Body shield */}
            <path
              d="M90 214 q0 -16 16 -16 h68 q16 0 16 16 v64 q0 11 -7 19 l-43 50 -43 -50 q-7 -8 -7 -19 z"
              fill="url(#ab-body)"
              stroke={c}
              strokeOpacity={0.35}
              strokeWidth={1.5}
            />

            {/* Logo panel */}
            <rect
              x={110} y={226} width={60} height={60} rx={16}
              fill="#0b1230"
              stroke={c}
              strokeOpacity={0.5}
              strokeWidth={1.5}
            />

            {/* AURA caret — glows and pulses */}
            <motion.path
              d="M140 244 L125 275 M140 244 L155 275"
              stroke="url(#ab-logo)"
              strokeWidth={7}
              strokeLinecap="round"
              strokeLinejoin="round"
              fill="none"
              animate={glowAnim}
              transition={logoGlowTrans}
              style={{ filter: `drop-shadow(0 0 6px ${c})` }}
            />

            {/* Antenna */}
            <motion.g
              animate={state === "error" ? { rotate: 16 } : { rotate: 0 }}
              style={{ transformOrigin: "140px 54px" }}
              transition={{ type: "spring", stiffness: 80, damping: 8 }}
            >
              <line
                x1={140} y1={54} x2={140} y2={32}
                stroke={PURPLE}
                strokeWidth={3}
                strokeLinecap="round"
                strokeOpacity={0.7}
              />
              <motion.circle
                cx={140} cy={25} r={7}
                fill={antennaC}
                animate={glowAnim}
                transition={antennaGlowTrans}
                style={{ filter: `drop-shadow(0 0 8px ${antennaC})` }}
              />
            </motion.g>

            {/* Head */}
            <ellipse
              cx={140} cy={122} rx={80} ry={74}
              fill="url(#ab-head)"
              stroke={c}
              strokeOpacity={0.65}
              strokeWidth={1.5}
            />

            {/* Visor band */}
            <path
              d="M68 104 a78 70 0 0 1 144 0 a200 200 0 0 1 -144 0 z"
              fill="#0a1028"
              opacity={0.5}
            />

            {/* ── EYES — state-dependent ── */}
            {state === "thinking" ? (
              /* Thinking dots pulse inside each eye slot */
              <g>
                {[0, 1, 2].map((i) => (
                  <motion.circle
                    key={`tl${i}`}
                    cx={107 + i * 9} cy={122} r={3}
                    fill={c}
                    animate={{ opacity: [0.25, 1, 0.25] }}
                    transition={{ duration: 0.9, repeat: Infinity, delay: i * 0.18 }}
                  />
                ))}
                {[0, 1, 2].map((i) => (
                  <motion.circle
                    key={`tr${i}`}
                    cx={157 + i * 9} cy={122} r={3}
                    fill={c}
                    animate={{ opacity: [0.25, 1, 0.25] }}
                    transition={{ duration: 0.9, repeat: Infinity, delay: 0.45 + i * 0.18 }}
                  />
                ))}
              </g>
            ) : state === "celebrate" ? (
              /* Happy arc eyes */
              <g>
                <path
                  d="M98 122 Q115 138 132 122"
                  fill="none"
                  stroke={c}
                  strokeWidth={3.5}
                  strokeLinecap="round"
                />
                <path
                  d="M148 122 Q165 138 182 122"
                  fill="none"
                  stroke={c}
                  strokeWidth={3.5}
                  strokeLinecap="round"
                />
              </g>
            ) : (
              /* Default blink — scaleY collapses at ~93% of a 5s cycle */
              <motion.g
                style={{ transformBox: "fill-box", transformOrigin: "center" }}
                animate={blinkAnim}
                transition={blinkTrans}
              >
                <rect
                  x={98} y={112} width={34} height={20} rx={10}
                  fill={c}
                  style={{ filter: `drop-shadow(0 0 7px ${c})` }}
                />
                <rect
                  x={148} y={112} width={34} height={20} rx={10}
                  fill={c}
                  style={{ filter: `drop-shadow(0 0 7px ${c})` }}
                />
              </motion.g>
            )}

            {/* Mouth */}
            <motion.rect
              x={127} y={152} width={26} height={6} rx={3}
              fill={c}
              animate={
                state === "speaking"
                  ? { scaleX: [0.6, 1.1, 0.6], opacity: [0.7, 1, 0.7] }
                  : { scaleX: 1, opacity: 0.4 }
              }
              transition={
                state === "speaking"
                  ? { duration: 0.38, repeat: Infinity }
                  : { duration: 0.3 }
              }
              style={{
                transformBox: "fill-box",
                transformOrigin: "center",
                filter: state === "speaking" ? `drop-shadow(0 0 4px ${c})` : undefined,
              }}
            />

          </motion.g>
          {/* ── end float group ── */}
        </motion.g>
        {/* ── end error shake wrapper ── */}
      </svg>
    </motion.div>
  );
}
