import { motion } from "framer-motion";
import { cn } from "@/lib/utils";

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

export function MetricCard({ value, label, variant = "default", index = 0 }: Props) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.05 }}
      className="bg-surface border border-border rounded-md p-4 text-center
                 hover:border-purple/30 transition-colors"
    >
      <p className="text-text-d text-[11px] font-bold tracking-widest uppercase mb-1">{label}</p>
      <p className={cn("text-2xl font-bold font-mono tabular-nums", variantClass[variant])}>
        {typeof value === "number" ? value.toLocaleString() : value}
      </p>
    </motion.div>
  );
}
