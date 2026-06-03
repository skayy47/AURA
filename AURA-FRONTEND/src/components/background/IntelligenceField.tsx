"use client";

import { useEffect, useRef } from "react";

/**
 * IntelligenceField — a living "superintelligence" background.
 *
 * Canvas layer: flowing luminous data streams + self-organizing neural nodes
 * that form and dissolve connections, with a slow cursor-reactive parallax.
 * Sits behind everything (fixed, z -10), pointer-events: none, reduced-motion safe.
 * Aurora/fog/gradient-mesh layers are CSS (see .if-* in globals.css).
 */
export function IntelligenceField() {
  const ref = useRef<HTMLCanvasElement>(null);
  const raf = useRef<number>(0);
  const mouse = useRef({ x: 0.5, y: 0.5 });

  useEffect(() => {
    const canvas = ref.current;
    if (!canvas) return;
    if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    let dpr = 1;
    let W = 0;
    let H = 0;

    type Node = { x: number; y: number; vx: number; vy: number; r: number; hue: number };
    type Stream = { x: number; y: number; len: number; speed: number; hue: number; phase: number };

    let nodes: Node[] = [];
    let streams: Stream[] = [];

    // 2045 palette (cyan / quantum-blue / neural-violet / energy-mint)
    const HUES = [187, 217, 258, 162]; // hsl hues for #00E5FF, #3B82F6, #8B5CF6, #00FFB2

    function size() {
      if (!canvas) return;
      dpr = Math.min(window.devicePixelRatio || 1, 2);
      W = canvas.width = window.innerWidth * dpr;
      H = canvas.height = window.innerHeight * dpr;
      canvas.style.width = window.innerWidth + "px";
      canvas.style.height = window.innerHeight + "px";
    }

    function seed() {
      const nodeCount = Math.min(64, Math.floor(window.innerWidth / 26));
      nodes = Array.from({ length: nodeCount }, () => ({
        x: Math.random() * W,
        y: Math.random() * H,
        vx: (Math.random() - 0.5) * 0.22 * dpr,
        vy: (Math.random() - 0.5) * 0.22 * dpr,
        r: (Math.random() * 1.5 + 0.7) * dpr,
        hue: HUES[(Math.random() * HUES.length) | 0],
      }));
      const streamCount = Math.min(26, Math.floor(window.innerWidth / 60));
      streams = Array.from({ length: streamCount }, () => ({
        x: Math.random() * W,
        y: Math.random() * H,
        len: (Math.random() * 90 + 50) * dpr,
        speed: (Math.random() * 0.7 + 0.4) * dpr,
        hue: HUES[(Math.random() * HUES.length) | 0],
        phase: Math.random() * Math.PI * 2,
      }));
    }

    size();
    seed();
    const ro = new ResizeObserver(() => { size(); seed(); });
    ro.observe(document.documentElement);

    const onMove = (e: MouseEvent) => {
      mouse.current = { x: e.clientX / window.innerWidth, y: e.clientY / window.innerHeight };
    };
    window.addEventListener("mousemove", onMove);

    let t = 0;
    function frame() {
      if (!canvas || !ctx) return;
      t += 0.005;
      ctx.clearRect(0, 0, W, H);
      ctx.globalCompositeOperation = "lighter";

      // parallax offset from cursor (very subtle, deep)
      const px = (mouse.current.x - 0.5) * 26 * dpr;
      const py = (mouse.current.y - 0.5) * 26 * dpr;

      // ── flowing data streams (vertical luminous trails) ──
      for (const s of streams) {
        s.y -= s.speed;
        s.x += Math.sin(t + s.phase) * 0.15 * dpr;
        if (s.y + s.len < 0) {
          s.y = H + s.len;
          s.x = Math.random() * W;
        }
        const gx = s.x + px * 0.4;
        const grad = ctx.createLinearGradient(gx, s.y, gx, s.y + s.len);
        grad.addColorStop(0, `hsla(${s.hue}, 100%, 65%, 0)`);
        grad.addColorStop(0.5, `hsla(${s.hue}, 100%, 65%, 0.22)`);
        grad.addColorStop(1, `hsla(${s.hue}, 100%, 65%, 0)`);
        ctx.strokeStyle = grad;
        ctx.lineWidth = 1.1 * dpr;
        ctx.beginPath();
        ctx.moveTo(gx, s.y);
        ctx.lineTo(gx, s.y + s.len);
        ctx.stroke();
      }

      // ── neural nodes + forming/dissolving links ──
      for (const n of nodes) {
        n.x += n.vx;
        n.y += n.vy;
        if (n.x < 0 || n.x > W) n.vx *= -1;
        if (n.y < 0 || n.y > H) n.vy *= -1;
      }

      const LINK = 150 * dpr;
      for (let i = 0; i < nodes.length; i++) {
        const a = nodes[i];
        for (let j = i + 1; j < nodes.length; j++) {
          const b = nodes[j];
          const dx = a.x - b.x;
          const dy = a.y - b.y;
          const d = Math.hypot(dx, dy);
          if (d < LINK) {
            // pulsing opacity = "forming and dissolving"
            const pulse = 0.5 + 0.5 * Math.sin(t * 2 + (a.x + b.y) * 0.002);
            const o = (1 - d / LINK) * 0.26 * pulse;
            ctx.strokeStyle = `hsla(${a.hue}, 90%, 68%, ${o})`;
            ctx.lineWidth = 0.7 * dpr;
            ctx.beginPath();
            ctx.moveTo(a.x + px, a.y + py);
            ctx.lineTo(b.x + px, b.y + py);
            ctx.stroke();
          }
        }
      }

      for (const n of nodes) {
        const glow = 0.6 + 0.4 * Math.sin(t * 1.6 + n.x * 0.01);
        ctx.fillStyle = `hsla(${n.hue}, 100%, 72%, ${0.5 * glow})`;
        ctx.beginPath();
        ctx.arc(n.x + px, n.y + py, n.r, 0, Math.PI * 2);
        ctx.fill();
      }

      ctx.globalCompositeOperation = "source-over";
      raf.current = requestAnimationFrame(frame);
    }

    raf.current = requestAnimationFrame(frame);

    return () => {
      ro.disconnect();
      window.removeEventListener("mousemove", onMove);
      cancelAnimationFrame(raf.current);
    };
  }, []);

  return (
    <div className="if-root" aria-hidden="true">
      {/* CSS layers: deep base, drifting aurora mesh, volumetric fog */}
      <div className="if-base" />
      <div className="if-aurora if-aurora-1" />
      <div className="if-aurora if-aurora-2" />
      <div className="if-aurora if-aurora-3" />
      <div className="if-fog" />
      {/* Canvas layer: data streams + neural network */}
      <canvas ref={ref} className="if-canvas" />
      {/* Vignette to sink edges and lift content */}
      <div className="if-vignette" />
    </div>
  );
}
