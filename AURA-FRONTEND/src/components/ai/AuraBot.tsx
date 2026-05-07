"use client";
import { useEffect, useRef, useState } from "react";
import { motion, useMotionValue, useAnimationFrame, animate } from "framer-motion";

export type BotState = "idle" | "listening" | "thinking" | "speaking" | "celebrate" | "error";

interface AuraBotProps {
  state?: BotState;
  size?: number;
  onClick?: () => void;
  ariaLabel?: string;
}

interface Particle {
  id: number;
  x: number;
  y: number;
  vx: number;
  vy: number;
  color: string;
  opacity: number;
  size: number;
}

const AURORA_COLORS = ["#6C3FED", "#22D3EE", "#3B82F6", "#EC4899"];
const PI = Math.PI;
const VBOX_W = 200;
const VBOX_H = 300;

const SPRING = { type: "spring" as const, stiffness: 300, damping: 20 };
const SOFT_SPRING = { type: "spring" as const, stiffness: 200, damping: 22 };
const DROOP_SPRING = { type: "spring" as const, stiffness: 80, damping: 8 };

export function AuraBot({ state = "idle", size = 200, onClick, ariaLabel = "AURA AI assistant" }: AuraBotProps) {
  const stateRef = useRef<BotState>(state);
  useEffect(() => { stateRef.current = state; }, [state]);

  const bodyY = useMotionValue(0);
  const bodyShakeX = useMotionValue(0);
  const antennaGlow = useMotionValue(0.7);
  const antennaOrbColor = useMotionValue(0);
  const armLeftX = useMotionValue(0);
  const armLeftY = useMotionValue(0);
  const armRightX = useMotionValue(0);
  const armRightY = useMotionValue(0);
  const chestOpacity = useMotionValue(0.85);
  const eyeGlow = useMotionValue(0.6);
  const eyeScaleY = useMotionValue(1);
  const antennaRotateZ = useMotionValue(0);
  const bodyRotateZ = useMotionValue(0);
  const bodyScale = useMotionValue(1);
  const mouthScaleX = useMotionValue(1);
  const mouthOpacity = useMotionValue(0.6);
  const edgeDashOffset = useMotionValue(0);

  const startTimeRef = useRef(performance.now());
  const errorStartRef = useRef<number | null>(null);
  const celebrateStartRef = useRef<number | null>(null);

  const [particles, setParticles] = useState<Particle[]>([]);
  const particleSeqRef = useRef(0);

  useEffect(() => {
    if (state === "error") errorStartRef.current = performance.now();
    else errorStartRef.current = null;

    if (state === "celebrate") {
      celebrateStartRef.current = performance.now();
      const burst: Particle[] = [];
      for (let i = 0; i < 28; i++) {
        const angle = (i / 28) * PI * 2 + Math.random() * 0.4;
        const speed = 2 + Math.random() * 3;
        burst.push({
          id: ++particleSeqRef.current,
          x: 100,
          y: 6,
          vx: Math.cos(angle) * speed,
          vy: Math.sin(angle) * speed - 0.5,
          color: AURORA_COLORS[i % AURORA_COLORS.length],
          opacity: 1,
          size: 1.6 + Math.random() * 1.8,
        });
      }
      setParticles(burst);
    } else {
      celebrateStartRef.current = null;
    }
  }, [state]);

  useEffect(() => {
    const s = state;
    if (s === "listening") {
      animate(eyeGlow, 0.85, SPRING);
      animate(eyeScaleY, 1.18, SPRING);
      animate(antennaRotateZ, -8, SPRING);
      animate(bodyRotateZ, 2, SPRING);
      animate(bodyScale, 1, SPRING);
      animate(mouthOpacity, 0.55, SPRING);
    } else if (s === "thinking") {
      animate(eyeGlow, 0.7, SOFT_SPRING);
      animate(eyeScaleY, 1, SPRING);
      animate(antennaRotateZ, 0, SPRING);
      animate(bodyRotateZ, 0, SPRING);
      animate(bodyScale, 1, SPRING);
      animate(mouthOpacity, 0, SPRING);
    } else if (s === "speaking") {
      animate(eyeGlow, 1, SPRING);
      animate(eyeScaleY, 1, SPRING);
      animate(antennaRotateZ, 0, SPRING);
      animate(bodyRotateZ, 0, SPRING);
      animate(bodyScale, 1, SPRING);
      animate(mouthOpacity, 0.95, SPRING);
    } else if (s === "celebrate") {
      animate(eyeGlow, 1, SPRING);
      animate(eyeScaleY, 1, SPRING);
      animate(antennaRotateZ, 0, SPRING);
      animate(bodyRotateZ, 0, SPRING);
      animate(bodyScale, 1.08, { type: "spring", stiffness: 400, damping: 15 });
      animate(mouthOpacity, 1, SPRING);
    } else if (s === "error") {
      animate(eyeGlow, 0.95, SPRING);
      animate(eyeScaleY, 0.85, SPRING);
      animate(antennaRotateZ, 18, DROOP_SPRING);
      animate(bodyRotateZ, 0, SPRING);
      animate(bodyScale, 1, SPRING);
      animate(mouthOpacity, 0, SPRING);
    } else {
      animate(eyeGlow, 0.6, SPRING);
      animate(eyeScaleY, 1, SPRING);
      animate(antennaRotateZ, 0, SPRING);
      animate(bodyRotateZ, 0, SPRING);
      animate(bodyScale, 1, SPRING);
      animate(mouthOpacity, 0.6, SPRING);
    }
  }, [state, eyeGlow, eyeScaleY, antennaRotateZ, bodyRotateZ, bodyScale, mouthOpacity]);

  useAnimationFrame((time) => {
    const t = (time - startTimeRef.current) / 1000;
    const s = stateRef.current;

    edgeDashOffset.set(-(t * (s === "speaking" ? 30 : 12)) % 100);
    antennaOrbColor.set((t * 30) % 360);

    if (s === "idle") {
      bodyY.set(Math.sin(t * 0.8) * 6);
      antennaGlow.set(Math.sin(t * 1.2) * 0.3 + 0.7);
      armLeftX.set(Math.cos(t * 0.6) * 4);
      armLeftY.set(Math.sin(t * 0.6) * 3);
      armRightX.set(Math.cos(t * 0.6 + PI) * 4);
      armRightY.set(Math.sin(t * 0.6 + PI) * 3);
      chestOpacity.set(Math.sin(t * 0.4) * 0.15 + 0.85);
      mouthScaleX.set(1);
    } else if (s === "listening") {
      bodyY.set(Math.sin(t * 1.0) * 4);
      antennaGlow.set(Math.sin(t * 1.6) * 0.25 + 0.75);
      armLeftX.set(Math.cos(t * 0.8) * 4);
      armLeftY.set(Math.sin(t * 0.8) * 3);
      armRightX.set(Math.cos(t * 0.8 + PI) * 4);
      armRightY.set(Math.sin(t * 0.8 + PI) * 3);
      chestOpacity.set(Math.sin(t * 0.4) * 0.15 + 0.85);
      mouthScaleX.set(1);
    } else if (s === "thinking") {
      bodyY.set(Math.sin(t * 1.2) * 5);
      antennaGlow.set(Math.sin(t * 2) * 0.3 + 0.6);
      const orbitR = 32;
      const orbitRy = 20;
      armLeftX.set(Math.cos(t * 1.5) * orbitR);
      armLeftY.set(Math.sin(t * 1.5) * orbitRy);
      armRightX.set(Math.cos(t * 1.5 + PI) * orbitR);
      armRightY.set(Math.sin(t * 1.5 + PI) * orbitRy);
      chestOpacity.set(Math.sin(t * 0.6) * 0.2 + 0.8);
      mouthScaleX.set(1);
    } else if (s === "speaking") {
      bodyY.set(Math.sin(t * 1.0) * 4);
      antennaGlow.set(0.9 + Math.sin(t * 4) * 0.1);
      armLeftX.set(Math.cos(t * 0.6) * 3);
      armLeftY.set(Math.sin(t * 0.6) * 2);
      armRightX.set(Math.cos(t * 0.6 + PI) * 3);
      armRightY.set(Math.sin(t * 0.6 + PI) * 2);
      chestOpacity.set(Math.sin(t * 1.5) * 0.2 + 0.8);
      mouthScaleX.set(0.6 + Math.abs(Math.sin(t * 6)) * 0.5);
    } else if (s === "celebrate") {
      const elapsed = celebrateStartRef.current ? (time - celebrateStartRef.current) / 1000 : 0;
      const jump = Math.max(0, 1 - elapsed / 1.5);
      bodyY.set(-12 * jump + Math.sin(t * 4) * 4);
      antennaGlow.set(1);
      const spin = Math.min(1, elapsed / 0.8) * PI * 2;
      armLeftX.set(Math.cos(spin) * 18);
      armLeftY.set(Math.sin(spin) * 12);
      armRightX.set(Math.cos(spin + PI) * 18);
      armRightY.set(Math.sin(spin + PI) * 12);
      chestOpacity.set(1);
      mouthScaleX.set(1);
    } else if (s === "error") {
      const elapsed = errorStartRef.current ? (time - errorStartRef.current) / 1000 : 0;
      const shake = Math.sin(elapsed * 18) * Math.max(0, 8 - elapsed * 3);
      bodyShakeX.set(shake);
      bodyY.set(Math.sin(t * 0.8) * 3);
      antennaGlow.set(0.5);
      armLeftX.set(0);
      armLeftY.set(8);
      armRightX.set(0);
      armRightY.set(8);
      chestOpacity.set(0.5);
      mouthScaleX.set(1);
    }

    if (s !== "error") bodyShakeX.set(0);

    if (s === "celebrate" && particles.length > 0) {
      setParticles((prev) =>
        prev
          .map((p) => ({
            ...p,
            x: p.x + p.vx,
            y: p.y + p.vy,
            vx: p.vx * 0.94,
            vy: p.vy * 0.94 + 0.08,
            opacity: Math.max(0, p.opacity - 0.018),
          }))
          .filter((p) => p.opacity > 0.02)
      );
    } else if (s !== "celebrate" && particles.length > 0) {
      setParticles([]);
    }
  });

  const eyeColor = state === "error" ? "#F59E0B" : "#22D3EE";
  const eyeGlowRgba = state === "error" ? "rgba(245, 158, 11, 0.85)" : "rgba(34, 211, 238, 0.85)";
  const antennaOrbBaseColor = state === "error" ? "#F59E0B" : "#6C3FED";
  const aspect = VBOX_W / VBOX_H;

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
      <svg viewBox={`0 0 ${VBOX_W} ${VBOX_H}`} width="100%" height="100%" overflow="visible">
        <defs>
          <linearGradient id="aurabot-edge" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="#6C3FED" />
            <stop offset="50%" stopColor="#22D3EE" />
            <stop offset="100%" stopColor="#3B82F6" />
          </linearGradient>
          <linearGradient id="aurabot-edge-cycle" x1="0%" y1="0%" x2="200%" y2="0%">
            <stop offset="0%" stopColor="#6C3FED" />
            <stop offset="33%" stopColor="#22D3EE" />
            <stop offset="66%" stopColor="#3B82F6" />
            <stop offset="100%" stopColor="#6C3FED" />
          </linearGradient>
          <linearGradient id="aurabot-body" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" stopColor="#0E162E" />
            <stop offset="100%" stopColor="#0A1022" />
          </linearGradient>
          <linearGradient id="aurabot-dome-tint" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="rgba(108,63,237,0.18)" />
            <stop offset="100%" stopColor="rgba(34,211,238,0.06)" />
          </linearGradient>
          <radialGradient id="aurabot-dome-shine" cx="32%" cy="22%" r="60%">
            <stop offset="0%" stopColor="rgba(255,255,255,0.18)" />
            <stop offset="100%" stopColor="rgba(255,255,255,0)" />
          </radialGradient>
          <radialGradient id="aurabot-arm" cx="35%" cy="30%" r="65%">
            <stop offset="0%" stopColor="#1A2848" />
            <stop offset="100%" stopColor="#0E162E" />
          </radialGradient>
          <radialGradient id="aurabot-orb" cx="50%" cy="50%" r="50%">
            <stop offset="0%" stopColor="#FFFFFF" stopOpacity="0.9" />
            <stop offset="40%" stopColor={antennaOrbBaseColor} stopOpacity="1" />
            <stop offset="100%" stopColor={antennaOrbBaseColor} stopOpacity="0.6" />
          </radialGradient>
          <filter id="aurabot-eye-glow" x="-100%" y="-100%" width="300%" height="300%">
            <feGaussianBlur stdDeviation="2.5" />
          </filter>
          <filter id="aurabot-orb-glow" x="-200%" y="-200%" width="500%" height="500%">
            <feGaussianBlur stdDeviation="4" />
          </filter>
          <filter id="aurabot-ground-glow" x="-100%" y="-100%" width="300%" height="300%">
            <feGaussianBlur stdDeviation="6" />
          </filter>
          <clipPath id="aurabot-head-clip">
            <ellipse cx="100" cy="80" rx="60" ry="52" />
          </clipPath>
        </defs>

        <motion.ellipse
          cx={100}
          cy={286}
          rx={48}
          ry={9}
          fill="rgba(34, 211, 238, 0.18)"
          filter="url(#aurabot-ground-glow)"
        />

        <motion.g style={{ x: bodyShakeX, scale: bodyScale, originX: "100px", originY: "150px" }}>
          <motion.g style={{ y: bodyY }}>

            <motion.g style={{ x: armLeftX, y: armLeftY }}>
              <ellipse cx={28} cy={188} rx={18} ry={5} fill="none" stroke="url(#aurabot-edge)" strokeWidth="0.8" opacity="0.7" />
              <circle cx={28} cy={188} r={13} fill="url(#aurabot-arm)" stroke="rgba(108,63,237,0.4)" strokeWidth="0.8" />
              <circle cx={25} cy={184} r={3.5} fill="rgba(255,255,255,0.08)" />
            </motion.g>

            <motion.g style={{ x: armRightX, y: armRightY }}>
              <ellipse cx={172} cy={188} rx={18} ry={5} fill="none" stroke="url(#aurabot-edge)" strokeWidth="0.8" opacity="0.7" />
              <circle cx={172} cy={188} r={13} fill="url(#aurabot-arm)" stroke="rgba(108,63,237,0.4)" strokeWidth="0.8" />
              <circle cx={169} cy={184} r={3.5} fill="rgba(255,255,255,0.08)" />
            </motion.g>

            <motion.g style={{ rotateZ: bodyRotateZ, originX: "100px", originY: "190px" }}>
              <path
                d="M 54 138 C 54 134 58 132 62 132 L 138 132 C 142 132 146 134 146 138 L 146 238 C 146 246 130 256 118 260 L 100 266 L 82 260 C 70 256 54 246 54 238 Z"
                fill="url(#aurabot-body)"
              />
              <motion.path
                d="M 54 138 C 54 134 58 132 62 132 L 138 132 C 142 132 146 134 146 138 L 146 238 C 146 246 130 256 118 260 L 100 266 L 82 260 C 70 256 54 246 54 238 Z"
                fill="none"
                stroke="url(#aurabot-edge-cycle)"
                strokeWidth="1.4"
                strokeDasharray="6 4"
                style={{ strokeDashoffset: edgeDashOffset }}
              />

              <rect x={73} y={150} width={54} height={64} rx={7}
                fill="rgba(7, 12, 26, 0.65)"
                stroke="rgba(108, 63, 237, 0.35)"
                strokeWidth="0.8"
              />
              <rect x={73} y={150} width={54} height={1.5} fill="rgba(34, 211, 238, 0.25)" />

              <motion.g style={{ opacity: chestOpacity }}>
                <g transform="translate(81.8, 163.44) scale(0.364)">
                  <path d="M 14 90 L 50 12 L 86 90"
                    stroke="rgba(34, 211, 238, 0.10)" strokeWidth="28"
                    strokeLinecap="round" strokeLinejoin="round" fill="none" />
                </g>
                <g transform="translate(81.8, 163.44) scale(0.364)">
                  <path d="M 14 90 L 50 12 L 86 90"
                    stroke="url(#aurabot-edge)" strokeWidth="11"
                    strokeLinecap="round" strokeLinejoin="round" fill="none" />
                  <path d="M 30 62 L 70 62"
                    stroke="url(#aurabot-edge)" strokeWidth="9"
                    strokeLinecap="round" fill="none" />
                </g>
              </motion.g>
            </motion.g>

            <g>
              <ellipse cx={100} cy={80} rx={60} ry={52} fill="url(#aurabot-body)" />
              <ellipse cx={100} cy={80} rx={60} ry={52} fill="url(#aurabot-dome-tint)" />
              <ellipse cx={100} cy={80} rx={60} ry={52} fill="url(#aurabot-dome-shine)" />

              <g clipPath="url(#aurabot-head-clip)">
                <path
                  d="M 40 75 Q 40 50 100 48 Q 160 50 160 75 L 160 130 Q 100 142 40 130 Z"
                  fill="#070C1A"
                />
                <path
                  d="M 40 75 Q 40 50 100 48 Q 160 50 160 75"
                  fill="none"
                  stroke="rgba(108, 63, 237, 0.25)"
                  strokeWidth="0.8"
                />
              </g>

              <ellipse cx={100} cy={80} rx={60} ry={52} fill="none" stroke="url(#aurabot-edge)" strokeWidth="1.2" />

              {state === "thinking" ? (
                <g>
                  {[0, 1, 2].map((i) => (
                    <motion.circle
                      key={`dl${i}`}
                      cx={64 + i * 8}
                      cy={92}
                      r={2.5}
                      fill={eyeColor}
                      animate={{ opacity: [0.25, 1, 0.25] }}
                      transition={{ duration: 0.9, repeat: Infinity, delay: i * 0.18 }}
                    />
                  ))}
                  {[0, 1, 2].map((i) => (
                    <motion.circle
                      key={`dr${i}`}
                      cx={114 + i * 8}
                      cy={92}
                      r={2.5}
                      fill={eyeColor}
                      animate={{ opacity: [0.25, 1, 0.25] }}
                      transition={{ duration: 0.9, repeat: Infinity, delay: i * 0.18 + 0.45 }}
                    />
                  ))}
                </g>
              ) : state === "celebrate" ? (
                <g>
                  <path d="M 60 92 Q 70 102 80 92" fill="none" stroke={eyeColor} strokeWidth="3" strokeLinecap="round" />
                  <path d="M 110 92 Q 120 102 130 92" fill="none" stroke={eyeColor} strokeWidth="3" strokeLinecap="round" />
                </g>
              ) : (
                <motion.g style={{ scaleY: eyeScaleY, originY: "92px" }}>
                  <motion.rect x={59} y={86} width={22} height={12} rx={5} fill={eyeColor} filter="url(#aurabot-eye-glow)" style={{ opacity: eyeGlow }} />
                  <motion.rect x={59} y={86} width={22} height={12} rx={5} fill={eyeColor} style={{ opacity: eyeGlow }} />
                  <motion.rect x={119} y={86} width={22} height={12} rx={5} fill={eyeColor} filter="url(#aurabot-eye-glow)" style={{ opacity: eyeGlow }} />
                  <motion.rect x={119} y={86} width={22} height={12} rx={5} fill={eyeColor} style={{ opacity: eyeGlow }} />
                  <rect x={63} y={88} width={5} height={3} rx={1.5} fill="rgba(255,255,255,0.5)" style={{ opacity: 0.7 }} />
                  <rect x={123} y={88} width={5} height={3} rx={1.5} fill="rgba(255,255,255,0.5)" style={{ opacity: 0.7 }} />
                </motion.g>
              )}

              <motion.rect
                x={87}
                y={111}
                width={26}
                height={3}
                rx={1.5}
                fill={state === "speaking" ? "#22D3EE" : "#1E2A50"}
                style={{
                  opacity: mouthOpacity,
                  scaleX: mouthScaleX,
                  originX: "100px",
                  filter: state === "speaking" ? `drop-shadow(0 0 4px ${eyeGlowRgba})` : undefined,
                }}
              />
            </g>

            <motion.g style={{ rotateZ: antennaRotateZ, originX: "100px", originY: "30px" }}>
              <line x1={100} y1={30} x2={100} y2={12} stroke="#1E2A50" strokeWidth="1.5" strokeLinecap="round" />
              <motion.circle
                cx={100}
                cy={9}
                r={7}
                fill={antennaOrbBaseColor}
                filter="url(#aurabot-orb-glow)"
                style={{ opacity: antennaGlow }}
              />
              <motion.circle
                cx={100}
                cy={9}
                r={5}
                fill="url(#aurabot-orb)"
                style={{ opacity: antennaGlow }}
              />
            </motion.g>
          </motion.g>
        </motion.g>

        {state === "celebrate" && particles.map((p) => (
          <circle
            key={p.id}
            cx={p.x}
            cy={p.y}
            r={p.size}
            fill={p.color}
            opacity={p.opacity}
            style={{ filter: `drop-shadow(0 0 4px ${p.color})` }}
          />
        ))}
      </svg>
    </motion.div>
  );
}
