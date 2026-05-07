"use client";
import { useEffect, useRef } from "react";

const DOTS = [
  { phase: 0,                rx: 118, ry: 36, speed:  0.42, size: 2.8, color: "#6C3FED" },
  { phase: Math.PI * 0.7,   rx: 96,  ry: 30, speed: -0.58, size: 2.2, color: "#22D3EE" },
  { phase: Math.PI * 1.3,   rx: 138, ry: 44, speed:  0.30, size: 2.0, color: "#3B82F6" },
  { phase: Math.PI * 0.3,   rx: 84,  ry: 26, speed: -0.74, size: 2.4, color: "#EC4899" },
  { phase: Math.PI * 1.85,  rx: 126, ry: 40, speed:  0.51, size: 1.6, color: "#22D3EE" },
  { phase: Math.PI * 2.25,  rx: 73,  ry: 23, speed: -0.90, size: 1.8, color: "#6C3FED" },
  { phase: Math.PI * 0.95,  rx: 150, ry: 47, speed:  0.24, size: 2.2, color: "#3B82F6" },
  { phase: Math.PI * 1.55,  rx: 106, ry: 33, speed:  0.66, size: 1.5, color: "#EC4899" },
] as const;

const CX = 160;
const CY = 155;

export function DataConstellation({ className }: { className?: string }) {
  const svgRef  = useRef<SVGSVGElement>(null);
  const rafRef  = useRef<number>(0);
  const t0Ref   = useRef(0);

  useEffect(() => {
    const svg = svgRef.current;
    if (!svg) return;

    t0Ref.current = performance.now();

    const items = DOTS.map((dot) => {
      const g    = document.createElementNS("http://www.w3.org/2000/svg", "g");
      const glow = document.createElementNS("http://www.w3.org/2000/svg", "circle");
      const core = document.createElementNS("http://www.w3.org/2000/svg", "circle");

      glow.setAttribute("r",      String(dot.size * 2.6));
      glow.setAttribute("fill",   dot.color);
      glow.setAttribute("filter", "url(#dc-glow)");

      core.setAttribute("r",    String(dot.size));
      core.setAttribute("fill", dot.color);

      g.appendChild(glow);
      g.appendChild(core);
      svg.appendChild(g);
      return g;
    });

    function tick(now: number) {
      const t = (now - t0Ref.current) / 1000;

      DOTS.forEach((dot, i) => {
        const angle = dot.phase + t * dot.speed;
        const x     = CX + Math.cos(angle) * dot.rx;
        const y     = CY + Math.sin(angle) * dot.ry;

        const depth   = (Math.sin(angle) + 1) * 0.5;
        const opacity = 0.30 + depth * 0.60;
        const scale   = 0.65 + depth * 0.35;

        items[i].setAttribute("transform", `translate(${x.toFixed(1)}, ${y.toFixed(1)}) scale(${scale.toFixed(3)})`);
        items[i].setAttribute("opacity",   opacity.toFixed(3));
      });

      rafRef.current = requestAnimationFrame(tick);
    }

    rafRef.current = requestAnimationFrame(tick);
    return () => {
      cancelAnimationFrame(rafRef.current);
      items.forEach((g) => svg.contains(g) && svg.removeChild(g));
    };
  }, []);

  return (
    <svg
      ref={svgRef}
      viewBox="0 0 320 320"
      className={className}
      aria-hidden="true"
    >
      <defs>
        <filter id="dc-glow" x="-300%" y="-300%" width="700%" height="700%">
          <feGaussianBlur stdDeviation="3.5" />
        </filter>
      </defs>
    </svg>
  );
}
