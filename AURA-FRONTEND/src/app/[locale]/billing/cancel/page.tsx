"use client";
import { motion } from "framer-motion";
import { Link } from "@/i18n/navigation";

export default function BillingCancelPage() {
  return (
    <div className="flex flex-col items-center justify-center min-h-[calc(100vh-56px)] px-6 text-center">
      <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }}>
        <div className="w-20 h-20 rounded-full bg-amber/10 border border-amber/30 flex items-center justify-center mx-auto mb-6">
          <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="#f59e0b" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M10.29 3.86 1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z" />
            <line x1="12" x2="12" y1="9" y2="13" />
            <line x1="12" x2="12.01" y1="17" y2="17" />
          </svg>
        </div>
        <h1 className="font-brand text-3xl text-text mb-3">Checkout cancelled</h1>
        <p className="text-text-m mb-8 max-w-sm mx-auto">
          No worries — you weren&apos;t charged. You can upgrade any time from the pricing page.
        </p>
        <div className="flex items-center justify-center gap-4">
          <Link href="/pricing" className="px-8 py-3 rounded-full bg-gradient-to-r from-purple to-cyan text-white font-medium hover:opacity-90 transition-opacity">
            View Pricing
          </Link>
          <Link href="/ingest" className="px-8 py-3 rounded-full border border-white/[0.1] text-text-m hover:text-text transition-colors">
            Continue free
          </Link>
        </div>
      </motion.div>
    </div>
  );
}
