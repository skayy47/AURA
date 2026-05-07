"use client";

import { useEffect, useRef, useState } from "react";
import {
  motion,
  useMotionValue,
  useSpring,
  useReducedMotion,
} from "framer-motion";
import { AuraBot, type BotState } from "@/components/ai/AuraBot";

interface RobotStageProps {
  state?: BotState;
  size?: number;
}

/**
 * Hero robot with 3D entry, mouse parallax, and a scroll-driven handoff to the
 * bottom-end corner (where the global BotOrb usually lives — that one is hidden
 * on landing so this stage owns the chat-trigger role).
 */
export function RobotStage({ state = "idle", size = 280 }: RobotStageProps) {
  const reduce = useReducedMotion();
  const containerRef = useRef<HTMLDivElement>(null);
  const sentinelRef = useRef<HTMLDivElement>(null);
  const [docked, setDocked] = useState(false);

  // Mouse parallax — damped springs feed rotation values
  const mx = useMotionValue(0);
  const my = useMotionValue(0);
  const rotateY = useSpring(mx, { stiffness: 110, damping: 18 });
  const rotateX = useSpring(my, { stiffness: 110, damping: 18 });

  useEffect(() => {
    if (reduce) return;
    const handle = (e: MouseEvent) => {
      const w = window.innerWidth;
      const h = window.innerHeight;
      // Range -1..1, then to deg
      mx.set(((e.clientX - w / 2) / (w / 2)) * 9);
      my.set(((e.clientY - h / 2) / (h / 2)) * -6);
    };
    window.addEventListener("mousemove", handle);
    return () => window.removeEventListener("mousemove", handle);
  }, [mx, my, reduce]);

  // Sentinel-driven dock/undock — when sentinel leaves the viewport, robot becomes fixed
  useEffect(() => {
    const node = sentinelRef.current;
    if (!node) return;
    const obs = new IntersectionObserver(
      ([entry]) => setDocked(!entry.isIntersecting),
      { threshold: 0, rootMargin: "-30% 0px 0px 0px" }
    );
    obs.observe(node);
    return () => obs.disconnect();
  }, []);

  return (
    <div ref={containerRef} className="relative w-full">
      {/* Hero-anchored mascot — present until docked */}
      <div ref={sentinelRef} className="relative perspective-stage">
        {!docked && (
          <motion.div
            layoutId="aura-mascot"
            initial={reduce ? { opacity: 0 } : { opacity: 0, y: -120, rotateX: -45, scale: 0.7 }}
            animate={{ opacity: 1, y: 0, rotateX: 0, scale: 1 }}
            transition={{ type: "spring", stiffness: 80, damping: 16, mass: 1.1 }}
            style={reduce ? undefined : { rotateX, rotateY, transformStyle: "preserve-3d" }}
            className="will-change-transform"
            aria-hidden={false}
          >
            <AuraBot size={size} state={state} ariaLabel="AURA — your data assistant" />
          </motion.div>
        )}
      </div>

      {/* Docked mascot — fixed bottom-end after the hero exits */}
      {docked && (
        <motion.button
          layoutId="aura-mascot"
          aria-label="AURA assistant"
          transition={{ type: "spring", stiffness: 110, damping: 22 }}
          className="fixed bottom-6 end-6 z-40 w-12 h-12 rounded-full overflow-hidden cursor-pointer group flex-shrink-0 select-none"
          onClick={() => {
            window.scrollTo({ top: 0, behavior: "smooth" });
          }}
        >
          <div className="absolute inset-0 rounded-full border border-border group-hover:border-purple/60 transition-colors z-10" />
          <div className="absolute inset-0 bg-surface flex items-start justify-center pt-1 overflow-hidden rounded-full">
            <div className="w-[120px] h-[120px] absolute -top-[14px]">
              <AuraBot size={120} state={state} />
            </div>
          </div>
          <div className="absolute -inset-[1px] rounded-full bg-gradient-to-r from-purple via-cyan to-blue opacity-0 group-hover:opacity-100 blur-[2px] transition-opacity -z-10" />
        </motion.button>
      )}
    </div>
  );
}
