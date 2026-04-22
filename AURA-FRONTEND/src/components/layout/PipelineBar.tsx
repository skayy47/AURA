"use client";
import { usePathname } from "next/navigation";
import Link from "next/link";
import { cn } from "@/lib/utils";

const STEPS = [
  { href: "/ingest",  label: "Ingest",  icon: "📂" },
  { href: "/clean",   label: "Clean",   icon: "🧼" },
  { href: "/explore", label: "Explore", icon: "🔍" },
  { href: "/ai-chat", label: "AI Chat", icon: "🤖" },
  { href: "/docs",    label: "Docs",    icon: "📄" },
];

export function PipelineBar() {
  const path = usePathname();
  const currentIdx = STEPS.findIndex((s) => s.href === path);

  return (
    <div className="flex border-b border-border bg-[#06080e] mb-8 -mx-8 px-0">
      {STEPS.map((step, i) => {
        const active = i === currentIdx;
        const done   = i < currentIdx;
        return (
          <Link key={step.href} href={step.href} className="flex-1">
            <div className={cn(
              "relative text-center py-4 border-r border-border last:border-r-0 transition-colors",
              active && "bg-[#0e0a20]"
            )}>
              {active && <div className="absolute bottom-0 left-0 right-0 h-[3px] bg-purple" />}
              <p className={cn("text-sm font-semibold",
                active ? "text-purple-l" : done ? "text-green" : "text-text-d"
              )}>
                {step.icon}  {step.label}{done ? " ✓" : ""}
              </p>
              {active && <p className="text-[11px] text-text-d mt-0.5">In progress</p>}
            </div>
          </Link>
        );
      })}
    </div>
  );
}
