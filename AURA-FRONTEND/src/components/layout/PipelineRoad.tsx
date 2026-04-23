"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { motion } from "framer-motion";
import { Upload, Sparkles, BarChart3, Bot, FileText, Check } from "./pipeline-icons";

type StepStatus = "done" | "active" | "pending";
type IconComponent = React.ComponentType<{ size?: number; color?: string; strokeWidth?: number }>;

interface PipelineStep {
  id: string;
  label: string;
  href: string;
  Icon: IconComponent;
  accent: string;
}

const STEPS: PipelineStep[] = [
  { id: "ingest",  label: "Ingest",  href: "/ingest",  Icon: Upload,    accent: "#6C3FE5" },
  { id: "clean",   label: "Clean",   href: "/clean",   Icon: Sparkles,  accent: "#10B981" },
  { id: "explore", label: "Explore", href: "/explore", Icon: BarChart3, accent: "#3B82F6" },
  { id: "ai-chat", label: "AI Chat", href: "/ai-chat", Icon: Bot,       accent: "#8B5CF6" },
  { id: "docs",    label: "Docs",    href: "/docs",    Icon: FileText,  accent: "#F59E0B" },
];

export function PipelineRoad() {
  const path = usePathname();
  const currentIdx = Math.max(0, STEPS.findIndex((s) => s.href === path));

  return (
    <nav
      role="navigation"
      aria-label="Pipeline progress"
      className="sticky top-0 z-40 -mx-8 mb-10 px-8 py-5 backdrop-blur-xl"
      style={{
        background: "rgba(4, 7, 18, 0.72)",
        borderBottom: "1px solid rgba(108, 63, 229, 0.15)",
      }}
    >
      <div className="flex items-center gap-2 max-w-5xl mx-auto">
        {STEPS.map((step, i) => {
          const status: StepStatus =
            i < currentIdx ? "done" : i === currentIdx ? "active" : "pending";
          return (
            <div key={step.id} className="flex items-center flex-1 last:flex-none">
              <StepNode step={step} status={status} />
              {i < STEPS.length - 1 && <Connector done={i < currentIdx} />}
            </div>
          );
        })}
      </div>
    </nav>
  );
}

function StepNode({ step, status }: { step: PipelineStep; status: StepStatus }) {
  const isActive = status === "active";
  const isDone = status === "done";
  const size = isActive ? 64 : 52;
  const iconSize = isActive ? 28 : 22;
  const { Icon } = step;

  return (
    <Link
      href={step.href}
      aria-label={`Go to ${step.label}`}
      aria-current={isActive ? "step" : undefined}
      className="flex flex-col items-center gap-2.5 shrink-0 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2 focus-visible:ring-offset-bg rounded-xl px-1"
      style={{ ["--tw-ring-color" as any]: step.accent }}
    >
      <div className="relative" style={{ width: size, height: size }}>
        {/* Pulsing ring — active only */}
        {isActive && (
          <motion.div
            className="absolute inset-0 rounded-full pointer-events-none"
            animate={{
              boxShadow: [
                `0 0 0 0px ${step.accent}99`,
                `0 0 0 10px ${step.accent}00`,
              ],
            }}
            transition={{ duration: 1.8, repeat: Infinity, ease: "easeOut" }}
          />
        )}

        {/* Icon container with entrance animation on status change */}
        <motion.div
          key={status}
          initial={{ scale: 0.75, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          transition={{ type: "spring", stiffness: 400, damping: 22 }}
          className="w-full h-full rounded-full flex items-center justify-center border-2 transition-all duration-300"
          style={{
            background: isActive
              ? `radial-gradient(circle, ${step.accent}33 0%, ${step.accent}0D 60%, transparent 100%)`
              : isDone
              ? `${step.accent}1A`
              : "rgba(10, 16, 34, 0.7)",
            borderColor: isActive
              ? step.accent
              : isDone
              ? `${step.accent}66`
              : "rgba(108, 63, 229, 0.18)",
            boxShadow: isActive ? `0 0 24px ${step.accent}80` : "none",
            color: isActive || isDone ? step.accent : "#94A3B8",
          }}
        >
          <Icon size={iconSize} strokeWidth={isActive ? 2.2 : 2} />
        </motion.div>

        {/* Done checkmark badge */}
        {isDone && (
          <motion.div
            initial={{ scale: 0, rotate: -20 }}
            animate={{ scale: 1, rotate: 0 }}
            transition={{ type: "spring", stiffness: 500, damping: 20 }}
            className="absolute -bottom-0.5 -right-0.5 w-5 h-5 rounded-full flex items-center justify-center border-2"
            style={{
              background: "#10B981",
              borderColor: "#040712",
            }}
          >
            <Check size={10} color="#040712" strokeWidth={3} />
          </motion.div>
        )}
      </div>

      <motion.span
        className="font-bricolage whitespace-nowrap"
        style={{
          fontWeight: 700,
          fontSize: "0.72rem",
          letterSpacing: "0.08em",
          textTransform: "uppercase",
        }}
        animate={{
          scale: isActive ? 1.1 : 1,
          color: isActive ? "#F1F5F9" : isDone ? "#CBD5E1" : "#94A3B8",
        }}
        transition={{ duration: 0.25, ease: "easeOut" }}
      >
        {step.label}
      </motion.span>
    </Link>
  );
}

function Connector({ done }: { done: boolean }) {
  return (
    <div
      className="flex-1 h-0.5 mx-2 relative overflow-hidden rounded-full"
      style={{ background: "rgba(108, 63, 229, 0.15)" }}
      aria-hidden="true"
    >
      <motion.div
        className="absolute inset-y-0 left-0 right-0 rounded-full"
        style={{
          background: "linear-gradient(90deg, #6C3FE5, #3B82F6)",
          transformOrigin: "left",
        }}
        initial={{ scaleX: 0 }}
        animate={{ scaleX: done ? 1 : 0 }}
        transition={{ duration: 0.5, ease: "easeInOut" }}
      />
    </div>
  );
}
