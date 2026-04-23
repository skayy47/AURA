"use client";
import { usePathname } from "next/navigation";
import { RoadNode } from "./RoadNode";

const STEPS = [
  { href: "/ingest",  label: "Ingest",  icon: "📂", x: 60,   y: 70  },
  { href: "/clean",   label: "Clean",   icon: "🧼", x: 330,  y: 40  },
  { href: "/explore", label: "Explore", icon: "🔍", x: 600,  y: 100 },
  { href: "/ai-chat", label: "AI Chat", icon: "🤖", x: 870,  y: 40  },
  { href: "/docs",    label: "Docs",    icon: "📄", x: 1140, y: 70  },
];

const PATH_D =
  "M 60 70 C 150 70 240 40 330 40 C 420 40 510 100 600 100 C 690 100 780 40 870 40 C 960 40 1050 70 1140 70";

export function PipelineRoad() {
  const path = usePathname();
  const currentIdx = STEPS.findIndex((s) => s.href === path);
  const safeIdx = currentIdx === -1 ? 0 : currentIdx;

  // Progress = ratio through the 4 segments between 5 nodes
  const progressPct = (safeIdx / (STEPS.length - 1)) * 100;

  return (
    <nav className="aura-road" role="navigation" aria-label="Pipeline progress">
      <svg className="aura-road-svg" viewBox="0 0 1200 140" preserveAspectRatio="xMidYMid meet">
        <defs>
          <linearGradient id="roadGradient" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" stopColor="#6c3fed" />
            <stop offset="50%" stopColor="#22d3ee" />
            <stop offset="100%" stopColor="#3b82f6" />
          </linearGradient>
        </defs>

        {/* base dashed road */}
        <path id="auraRoadPath" d={PATH_D} className="aura-road-base" pathLength={100} />

        {/* progress overlay — reveals via stroke-dashoffset */}
        <path
          d={PATH_D}
          className="aura-road-progress"
          pathLength={100}
          strokeDasharray="100"
          strokeDashoffset={100 - progressPct}
        />

        {/* traveling vehicle dot, loops forever along full path */}
        <circle r={5} className="aura-road-vehicle">
          <animateMotion dur="6s" repeatCount="indefinite" rotate="auto">
            <mpath href="#auraRoadPath" />
          </animateMotion>
        </circle>

        {/* nodes on top */}
        {STEPS.map((step, i) => {
          const state: "done" | "active" | "todo" =
            i < safeIdx ? "done" : i === safeIdx ? "active" : "todo";
          return (
            <RoadNode
              key={step.href}
              x={step.x}
              y={step.y}
              href={step.href}
              icon={step.icon}
              label={step.label}
              state={state}
            />
          );
        })}
      </svg>
    </nav>
  );
}
