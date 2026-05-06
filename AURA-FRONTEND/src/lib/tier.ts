"use client";
import { useState, useEffect } from "react";

export type Tier = "free" | "pro" | "team";

const STORAGE_KEY = "aura_tier";

export function useTier(): { tier: Tier; setTier: (t: Tier) => void } {
  const [tier, setTierState] = useState<Tier>("free");

  useEffect(() => {
    const stored = (typeof window !== "undefined" ? localStorage.getItem(STORAGE_KEY) : null) as Tier | null;
    if (stored === "pro" || stored === "team") setTierState(stored);
  }, []);

  const setTier = (t: Tier) => {
    localStorage.setItem(STORAGE_KEY, t);
    setTierState(t);
  };

  return { tier, setTier };
}

export function tierAtLeast(current: Tier, required: Tier): boolean {
  const rank: Record<Tier, number> = { free: 0, pro: 1, team: 2 };
  return rank[current] >= rank[required];
}
