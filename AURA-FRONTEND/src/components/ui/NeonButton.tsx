"use client";
import { forwardRef } from "react";
import { cn } from "@/lib/utils";

type Variant = "primary" | "ghost";
type Size = "sm" | "md" | "lg";

interface Props extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: Variant;
  size?: Size;
  showArrow?: boolean;
  children: React.ReactNode;
}

function Arrow({ size }: { size: number }) {
  return (
    <svg
      className="aura-btn-neon-arrow"
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2.2"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
    >
      <path d="M5 12h14" />
      <path d="m12 5 7 7-7 7" />
    </svg>
  );
}

export const NeonButton = forwardRef<HTMLButtonElement, Props>(function NeonButton(
  { variant = "primary", size = "md", showArrow = true, className, children, ...rest },
  ref,
) {
  const iconSize = size === "sm" ? 14 : 16;
  return (
    <button
      ref={ref}
      className={cn(
        "aura-btn-neon",
        size === "sm" && "aura-btn-neon--sm",
        size === "lg" && "aura-btn-neon--lg",
        variant === "ghost" && "aura-btn-neon--ghost",
        className,
      )}
      {...rest}
    >
      <span>{children}</span>
      {showArrow && <Arrow size={iconSize} />}
    </button>
  );
});
