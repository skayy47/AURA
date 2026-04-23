import { motion } from "framer-motion";
import { cn } from "@/lib/utils";
import { GlowCard } from "./GlowCard";

interface Props {
  value: string | number;
  label: string;
  variant?: "default" | "warn" | "success" | "accent";
  index?: number;
}

const variantClass = {
  default:  "text-text",
  warn:     "text-amber",
  success:  "text-green",
  accent:   "text-purple-l",
};

const variantAccent = {
  default: "purple",
  warn:    "cyan",
  success: "blue",
  accent:  "purple",
} as const;

export function MetricCard({ value, label, variant = "default", index = 0 }: Props) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.05 }}
    >
      <GlowCard accent={variantAccent[variant]} intensity="low" innerClassName="text-center p-4">
        <p className="text-text-d text-[11px] font-bold tracking-widest uppercase mb-1">{label}</p>
        <p className={cn("text-2xl font-bold font-mono tabular-nums", variantClass[variant])}>
          {typeof value === "number" ? value.toLocaleString() : value}
        </p>
      </GlowCard>
    </motion.div>
  );
}
