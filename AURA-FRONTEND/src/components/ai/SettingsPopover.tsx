"use client";
import { useStore } from "@/lib/store";
import { motion, AnimatePresence } from "framer-motion";
import { useRef, useEffect } from "react";

interface Props {
  isOpen: boolean;
  onClose: () => void;
}

export function SettingsPopover({ isOpen, onClose }: Props) {
  const provider = useStore((s) => s.provider);
  const setProvider = useStore((s) => s.setProvider);
  const temperature = useStore((s) => s.temperature);
  const setTemperature = useStore((s) => s.setTemperature);
  const popoverRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (popoverRef.current && !popoverRef.current.contains(e.target as Node)) {
        onClose();
      }
    };
    if (isOpen) {
      document.addEventListener("mousedown", handleClickOutside);
      const handleEscape = (e: KeyboardEvent) => e.key === "Escape" && onClose();
      document.addEventListener("keydown", handleEscape);
      return () => {
        document.removeEventListener("mousedown", handleClickOutside);
        document.removeEventListener("keydown", handleEscape);
      };
    }
  }, [isOpen, onClose]);

  return (
    <AnimatePresence>
      {isOpen && (
      <motion.div
        key="settings-popover"
        initial={{ opacity: 0, scale: 0.95, y: 10 }}
        animate={{ opacity: 1, scale: 1, y: 0 }}
        exit={{ opacity: 0, scale: 0.95, y: 10 }}
        transition={{ duration: 0.15 }}
        ref={popoverRef}
        className="absolute top-10 right-0 z-50 w-72 bg-[#070C1A] border border-[#1E2A50] rounded-xl shadow-aura-lg p-5"
      >
        <h3 className="font-bricolage font-semibold text-[0.85rem] uppercase tracking-wide text-text mb-4">
          AI Settings
        </h3>

        <div className="mb-5">
          <label className="block text-[0.75rem] text-text-m mb-2">Provider</label>
          <div className="space-y-2">
            {["Claude", "OpenAI", "Ollama (local)"].map((p) => {
              const val = p.split(" ")[0];
              return (
                <label key={p} className="flex items-center gap-2 text-sm text-text cursor-pointer">
                  <input
                    type="radio"
                    name="provider"
                    value={val}
                    checked={provider === val}
                    onChange={(e) => setProvider(e.target.value)}
                    className="accent-purple"
                  />
                  {p}
                </label>
              );
            })}
          </div>
        </div>

        <div className="mb-5">
          <label className="flex justify-between text-[0.75rem] text-text-m mb-2">
            <span>Temperature</span>
            <span>{temperature.toFixed(1)}</span>
          </label>
          <input
            type="range"
            min="0"
            max="1"
            step="0.1"
            value={temperature}
            onChange={(e) => setTemperature(parseFloat(e.target.value))}
            className="w-full accent-cyan"
          />
        </div>

        <div className="mb-5">
          <label className="block text-[0.75rem] text-text-m mb-2">Context window</label>
          <div className="space-y-2">
            <label className="flex items-center gap-2 text-sm text-text cursor-pointer">
              <input type="checkbox" defaultChecked className="accent-purple" />
              Include dataset structure
            </label>
            <label className="flex items-center gap-2 text-sm text-text cursor-pointer">
              <input type="checkbox" defaultChecked className="accent-purple" />
              Include cleaning log
            </label>
            <label className="flex items-center gap-2 text-sm text-text cursor-pointer">
              <input type="checkbox" className="accent-purple" />
              Include sample rows (5)
            </label>
          </div>
        </div>

        <div className="pt-3 border-t border-border">
          <button
            onClick={() => {
              setProvider("Claude");
              setTemperature(0.7);
            }}
            className="text-[0.75rem] text-text-d hover:text-text-m underline transition-colors"
          >
            Reset to defaults
          </button>
        </div>
      </motion.div>
      )}
    </AnimatePresence>
  );
}
