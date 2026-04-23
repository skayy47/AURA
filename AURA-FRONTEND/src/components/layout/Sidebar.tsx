"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useStore } from "@/lib/store";
import { cn } from "@/lib/utils";
import { motion } from "framer-motion";

const NAV = [
  { href: "/ingest",   icon: "📂", label: "Ingest",   step: 1 },
  { href: "/clean",    icon: "🧼", label: "Clean",    step: 2 },
  { href: "/explore",  icon: "🔍", label: "Explore",  step: 3 },
  { href: "/ai-chat",  icon: "🤖", label: "AI Chat",  step: 4 },
  { href: "/docs",     icon: "📄", label: "Docs",     step: 5 },
];

export function Sidebar() {
  const path = usePathname();
  const { meta, cleanResult } = useStore();

  return (
    <aside className="fixed left-0 top-0 h-screen w-[280px] bg-sidebar border-r border-border flex flex-col z-40"
           style={{ borderTop: "3px solid #6C3FE5" }}>
      {/* Logo */}
      <div className="flex items-center gap-3 px-5 py-6 border-b border-border">
        <div className="w-10 h-10 rounded-[10px] bg-purple flex items-center justify-center text-xl shrink-0">⚡</div>
        <div>
          <div className="font-heading font-bold text-text text-lg tracking-tight">AURA</div>
          <div className="text-text-d text-xs">data engine</div>
        </div>
      </div>

      {/* Nav */}
      <nav className="flex-1 px-3 py-4 space-y-1">
        <p className="text-text-d text-[11px] font-bold tracking-widest uppercase px-2 mb-3">Workspace</p>
        {NAV.map((item) => {
          const active = path === item.href;
          return (
            <Link key={item.href} href={item.href}>
              <motion.div whileHover={{ x: 2 }} className={cn(
                "flex items-center gap-3 px-3 py-2.5 rounded-sm text-sm font-medium transition-colors relative",
                active
                  ? "bg-surface2 text-purple-l"
                  : "text-text-m hover:bg-surface2/60 hover:text-text"
              )}>
                {active && (
                  <motion.div layoutId="nav-indicator"
                    className="absolute left-0 top-1 bottom-1 w-[3px] rounded-r-full bg-purple" />
                )}
                <span>{item.icon}</span>
                <span>{item.label}</span>
              </motion.div>
            </Link>
          );
        })}
      </nav>

      {/* Dataset status */}
      {meta && (
        <div className="px-3 py-4 border-t border-border">
          <p className="text-text-d text-[11px] font-bold tracking-widest uppercase px-2 mb-2">Dataset</p>
          <div className="aura-card-elevated p-3 rounded-md">
            <p className="text-text font-mono text-xs truncate" title={meta.file_name}>{meta.file_name}</p>
            <p className="text-purple-l text-xs mt-1">{meta.rows.toLocaleString()} rows · {meta.cols} cols</p>
            <span className={cn("aura-tag mt-2", cleanResult ? "aura-tag-success" : "aura-tag-warning")}>
              {cleanResult ? "✓ Cleaned" : "⚠ Raw"}
            </span>
          </div>
        </div>
      )}

      {/* Footer */}
      <div className="px-3 py-3 border-t border-border flex justify-center">
        <button className="aura-btn-neon aura-btn-neon--sm aura-btn-neon--ghost">
          <span>🔄 New Dataset</span>
        </button>
      </div>
    </aside>
  );
}
