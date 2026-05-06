"use client";
import { useEffect } from "react";
import { useSearchParams } from "next/navigation";
import { motion } from "framer-motion";
import { Link } from "@/i18n/navigation";
import { useTier } from "@/lib/tier";

export default function BillingSuccessPage() {
  const params = useSearchParams();
  const { setTier } = useTier();

  useEffect(() => {
    // In production, verify the session server-side and set tier from webhook.
    // For now, optimistically set "pro" so the UI unlocks immediately.
    setTier("pro");
  }, []);

  return (
    <div className="flex flex-col items-center justify-center min-h-[calc(100vh-56px)] px-6 text-center">
      <motion.div initial={{ scale: 0.8, opacity: 0 }} animate={{ scale: 1, opacity: 1 }} transition={{ type: "spring", stiffness: 260, damping: 20 }}>
        <div className="w-20 h-20 rounded-full bg-green/10 border border-green/30 flex items-center justify-center mx-auto mb-6">
          <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="#10b981" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
            <polyline points="20 6 9 17 4 12" />
          </svg>
        </div>
        <h1 className="font-brand text-3xl text-text mb-3">You&apos;re on Pro!</h1>
        <p className="text-text-m mb-8 max-w-sm mx-auto">
          Your subscription is active. All Pro features are now unlocked — including PDF export and unlimited AI questions.
        </p>
        <Link href="/explore" className="px-8 py-3 rounded-full bg-gradient-to-r from-purple to-cyan text-white font-medium hover:opacity-90 transition-opacity">
          Go to Explore →
        </Link>
        {params.get("session_id") && (
          <p className="mt-6 text-text-d text-xs font-geist-mono">
            Session: {params.get("session_id")}
          </p>
        )}
      </motion.div>
    </div>
  );
}
