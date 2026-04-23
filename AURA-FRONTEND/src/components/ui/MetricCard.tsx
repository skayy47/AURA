"use client";
import { useEffect, useRef, useState } from "react";
import { motion } from "framer-motion";
import { cn } from "@/lib/utils";

type Accent = "purple" | "green" | "amber" | "blue" | "default" | "warn" | "success" | "accent";

interface Props {
  label: string;
  value: string | number;
  variant?: Accent;
  index?: number;
  animate?: boolean;
}

const accentColors: Record<Accent, string> = {
  purple:  "#8B5CF6",
  green:   "#10B981",
  amber:   "#F59E0B",
  blue:    "#3B82F6",
  default: "#F1F5F9",
  warn:    "#F59E0B",
  success: "#10B981",
  accent:  "#8B5CF6",
};

function useCountUp(target: number, duration = 800) {
  const [value, setValue] = useState(target);
  const rafRef = useRef<number | null>(null);

  useEffect(() => {
    if (rafRef.current !== null) cancelAnimationFrame(rafRef.current);
    const start = performance.now();
    const from = 0;
    const tick = (now: number) => {
      const progress = Math.min((now - start) / duration, 1);
      const eased = 1 - Math.pow(1 - progress, 3); // ease-out-cubic
      setValue(Math.round(from + eased * (target - from)));
      if (progress < 1) rafRef.current = requestAnimationFrame(tick);
    };
    rafRef.current = requestAnimationFrame(tick);
    return () => {
      if (rafRef.current !== null) cancelAnimationFrame(rafRef.current);
    };
  }, [target, duration]);

  return value;
}

export function MetricCard({
  label,
  value,
  variant = "default",
  index = 0,
  animate = true,
}: Props) {
  const isNumber = typeof value === "number";
  const target = isNumber ? (value as number) : 0;
  const count = useCountUp(target);
  const displayValue = isNumber && animate
    ? count.toLocaleString()
    : isNumber
    ? (value as number).toLocaleString()
    : value;

  const color = accentColors[variant] ?? accentColors.default;

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.05, duration: 0.35, ease: "easeOut" }}
      className={cn(
        "relative overflow-hidden rounded-2xl p-5 group",
        "border border-white/[0.06]",
        "bg-gradient-to-b from-white/[0.04] to-transparent",
        "transition-[border-color,box-shadow] duration-300",
        "hover:border-[rgba(108,63,229,0.3)]",
        "hover:shadow-[0_0_24px_rgba(108,63,229,0.12)]"
      )}
    >
      <p className="text-[0.65rem] font-bold tracking-[0.1em] uppercase text-text-d mb-2">
        {label}
      </p>
      <p
        className="font-geist-mono font-bold text-2xl leading-none tabular-nums"
        style={{ color }}
      >
        {displayValue}
      </p>
    </motion.div>
  );
}
