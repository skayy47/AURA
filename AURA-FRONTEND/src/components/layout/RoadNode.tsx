import Link from "next/link";

type State = "done" | "active" | "todo";

interface Props {
  x: number;
  y: number;
  href: string;
  icon: string;
  label: string;
  state: State;
}

export function RoadNode({ x, y, href, icon, label, state }: Props) {
  return (
    <Link href={href} aria-label={`Go to ${label}`} aria-current={state === "active" ? "step" : undefined}>
      <g className="aura-road-node" tabIndex={0}>
        {state === "active" && (
          <circle cx={x} cy={y} r={14} className="aura-road-node-pulse" />
        )}

        <circle
          cx={x}
          cy={y}
          r={14}
          className="aura-road-node-core"
          data-state={state}
        />

        <text x={x} y={y} className="aura-road-node-icon">
          {state === "done" ? "✓" : icon}
        </text>

        <text
          x={x}
          y={y + 34}
          className="aura-road-node-label"
          data-state={state}
        >
          {label}
        </text>

        {/* invisible larger hit target */}
        <circle cx={x} cy={y} r={24} fill="transparent" />
      </g>
    </Link>
  );
}
