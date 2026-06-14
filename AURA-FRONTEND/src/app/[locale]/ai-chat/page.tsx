"use client";
import { useEffect, useRef, useState, useCallback } from "react";
import { useTranslations, useLocale } from "next-intl";
import { motion } from "framer-motion";
import { EmptyState } from "@/components/ui/EmptyState";
import { AuraLoader } from "@/components/ui/AuraLoader";
import { ChatBubble } from "@/components/ai/ChatBubble";
import { ChatInput } from "@/components/ai/ChatInput";
import { AuraBot, type BotState } from "@/components/ai/AuraBot";
import { IntelPanel } from "@/components/ai/IntelPanel";
// GlowCard removed from suggestions — replaced with clean glass cards
import { streamAsk, fetchAnalysis } from "@/lib/api";
import { useStore } from "@/lib/store";
import { Link } from "@/i18n/navigation";

import { SettingsPopover } from "@/components/ai/SettingsPopover";

const PROVIDER_BADGE: Record<string, { label: string; color: string }> = {
  gemini:  { label: "Gemini · Flash 2.0", color: "#4285F4" },
  groq:    { label: "Groq · Free",        color: "#00FFB2" },
  claude:  { label: "Claude",             color: "#8B5CF6" },
  openai:  { label: "OpenAI",             color: "#3B82F6" },
};

const ACCENTS = ["purple", "cyan", "blue"] as const;

export default function AiChatPage() {
  const t = useTranslations("ai");
  const locale = useLocale();
  const { sessionId, meta, chatHistory, addMessage } = useStore();
  const [loading, setLoading] = useState(false);
  const [streamedResponse, setStreamedResponse] = useState("");
  const [botState, setBotState] = useState<BotState>("idle");
  const [settingsOpen, setSettingsOpen] = useState(false);
  const [suggestions, setSuggestions] = useState<string[] | null>(null);
  const rawProvider = useStore((s) => s.provider).toLowerCase();
  const currentProvider = (
    ["gemini", "groq", "claude", "openai"].includes(rawProvider) ? rawProvider : "gemini"
  ) as "gemini" | "groq" | "claude" | "openai";

  const endRef = useRef<HTMLDivElement>(null);
  const messageRefs = useRef<Record<number, HTMLDivElement | null>>({});

  const transitionTimer = useRef<ReturnType<typeof setTimeout> | null>(null);
  useEffect(() => () => { if (transitionTimer.current) clearTimeout(transitionTimer.current); }, []);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth", block: "end" });
  }, [chatHistory.length, streamedResponse]);

  // Data-specific suggested questions, derived server-side from the analysis.
  useEffect(() => {
    if (!sessionId) return;
    fetchAnalysis(sessionId, locale)
      .then((res) => setSuggestions(res.suggested_questions ?? []))
      .catch(() => setSuggestions([]));
  }, [sessionId, locale]);

  const handleSend = useCallback(async (question: string) => {
    if (!sessionId) return;
    setLoading(true);
    setBotState("thinking");
    addMessage({ role: "user", content: question, ts: Date.now() });
    setStreamedResponse("");

    try {
      let fullText = "";
      let firstChunk = true;
      for await (const chunk of streamAsk(sessionId, question, currentProvider, locale)) {
        if (firstChunk) {
          setBotState("speaking");
          firstChunk = false;
        }
        fullText += chunk;
        setStreamedResponse(fullText);
      }
      addMessage({ role: "assistant", content: fullText, ts: Date.now() });
      setStreamedResponse("");

      const shouldCelebrate = fullText.length > 60 && Math.random() < 0.35;
      setBotState(shouldCelebrate ? "celebrate" : "idle");
      if (shouldCelebrate) {
        if (transitionTimer.current) clearTimeout(transitionTimer.current);
        transitionTimer.current = setTimeout(() => setBotState("idle"), 1800);
      }
    } catch (e: any) {
      addMessage({ role: "assistant", content: `${t("error")} (${e.message})`, ts: Date.now() });
      setBotState("error");
      if (transitionTimer.current) clearTimeout(transitionTimer.current);
      transitionTimer.current = setTimeout(() => setBotState("idle"), 2000);
    } finally {
      setLoading(false);
    }
  }, [sessionId, addMessage, currentProvider, locale, t]);

  const scrollToMessage = useCallback((index: number) => {
    const el = messageRefs.current[index];
    if (el) {
      el.scrollIntoView({ behavior: "smooth", block: "center" });
      el.classList.add("ring-2", "ring-purple/40");
      setTimeout(() => el.classList.remove("ring-2", "ring-purple/40"), 1400);
    }
  }, []);

  const triggerWave = useCallback(() => {
    if (loading) return;
    setBotState("celebrate");
    if (transitionTimer.current) clearTimeout(transitionTimer.current);
    transitionTimer.current = setTimeout(() => setBotState("idle"), 1500);
  }, [loading]);

  if (!meta || !sessionId) {
    return <EmptyState />;
  }

  const isEmpty = chatHistory.length === 0 && !streamedResponse && !loading;
  // null = still loading; [] = loaded but empty (use fallbacks); string[] = data-specific
  const questionList: string[] =
    suggestions && suggestions.length > 0
      ? suggestions
      : suggestions === null
      ? []
      : [t("fallbackQ1"), t("fallbackQ2"), t("fallbackQ3")];
  const heroSuggestions = questionList.slice(0, 3).map((question, i) => ({
    question,
    accent: ACCENTS[i % ACCENTS.length],
  }));
  const provider = PROVIDER_BADGE[rawProvider] || PROVIDER_BADGE["gemini"];

  return (
    <div className="flex gap-6 h-[calc(100vh-4rem)] -mx-2">
      <IntelPanel
        botState={botState}
        suggestions={questionList}
        onSuggestionClick={handleSend}
        onHistoryClick={scrollToMessage}
        onBotClick={triggerWave}
        disabled={loading}
      />

      <section className="flex-1 flex flex-col min-w-0 bg-surface border border-border rounded-2xl overflow-hidden">

        <header className="flex items-center justify-between px-5 h-12 border-b border-border shrink-0">
          <p className="font-bricolage font-semibold text-[0.78rem] text-text-m tracking-wide">
            AURA AI
          </p>
          <div className="flex items-center gap-2">
            <span className="w-1.5 h-1.5 rounded-full" style={{ backgroundColor: provider.color, boxShadow: `0 0 6px ${provider.color}` }} />
            <span className="text-[0.75rem] text-text font-medium">{provider.label}</span>
            <span className="text-text-d text-[0.7rem] truncate max-w-[260px] ml-2 font-geist-mono" title={meta.name}>
              {meta.name}
            </span>
          </div>
          <div className="flex items-center gap-3">
            <Link
              href="/docs"
              className="inline-flex items-center gap-1.5 text-[0.74rem] font-semibold text-text rounded-lg px-3 py-1.5 bg-gradient-to-r from-cyan/15 to-purple/15 border border-cyan/30 hover:border-cyan/60 hover:from-cyan/25 hover:to-purple/25 transition-colors"
            >
              {t("exportReport")}
              <svg viewBox="0 0 24 24" width="13" height="13" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M5 12h14M13 6l6 6-6 6" />
              </svg>
            </Link>
            {(loading || streamedResponse) && (
              <span className="text-[0.72rem] font-medium text-aurora-cyan flex items-center gap-1.5">
                <motion.span
                  animate={{ scale: [1, 1.4, 1], opacity: [0.6, 1, 0.6] }}
                  transition={{ duration: 1.2, repeat: Infinity }}
                  className="w-1.5 h-1.5 rounded-full bg-aurora-cyan"
                />
                {t("thinking")}
              </span>
            )}
            <div className="relative">
              <button
                type="button"
                aria-label="Settings"
                onClick={() => setSettingsOpen(!settingsOpen)}
                className="w-7 h-7 rounded-md flex items-center justify-center text-text-d hover:text-text-m transition-colors"
              >
                <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <circle cx="12" cy="12" r="3" />
                  <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 1 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 1 1-4 0v-.09a1.65 1.65 0 0 0-1-1.51 1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 1 1-2.83-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 1 1 0-4h.09a1.65 1.65 0 0 0 1.51-1 1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 1 1 2.83-2.83l.06-.06a1.65 1.65 0 0 0 1.82.33h0a1.65 1.65 0 0 0 1-1.51V3a2 2 0 1 1 4 0v.09a1.65 1.65 0 0 0 1 1.51h0a1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 1 1 2.83 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82v0a1.65 1.65 0 0 0 1.51 1H21a2 2 0 1 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z" />
                </svg>
              </button>
              <SettingsPopover isOpen={settingsOpen} onClose={() => setSettingsOpen(false)} />
            </div>
          </div>
        </header>

        <div className="flex-1 overflow-y-auto custom-scrollbar px-6 py-6">
          {isEmpty ? (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ duration: 0.6 }}
              className="h-full flex flex-col items-center justify-center text-center"
            >
              <AuraBot state="idle" size={260} />
              <h2 className="font-bricolage font-semibold text-text text-2xl mt-6 mb-2">
                {t("analyzed")}
              </h2>
              <p className="text-text-m text-sm mb-8">
                {t("rowColSummary", { rows: meta.n_rows.toLocaleString(), cols: meta.n_cols })}
              </p>
              {suggestions === null ? (
                <div className="grid grid-cols-1 md:grid-cols-3 gap-3 max-w-[640px] w-full">
                  {[0, 1, 2].map((i) => (
                    <div
                      key={i}
                      className="rounded-xl min-h-[84px] bg-[rgba(11,20,38,0.7)] border border-border animate-pulse"
                    />
                  ))}
                </div>
              ) : heroSuggestions.length > 0 ? (
                <div className="grid grid-cols-1 md:grid-cols-3 gap-3 max-w-[640px] w-full">
                  {heroSuggestions.map((s, i) => {
                    const dot =
                      s.accent === "cyan" ? "#00e5ff" : s.accent === "blue" ? "#3b82f6" : "#8b5cf6";
                    return (
                      <motion.button
                        key={i}
                        initial={{ opacity: 0, y: 12 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: 0.4 + i * 0.08, duration: 0.4 }}
                        onClick={() => handleSend(s.question)}
                        className="group text-left rounded-xl p-4 min-h-[84px] flex items-start gap-2.5 bg-[rgba(11,20,38,0.7)] border border-border hover:border-cyan/45 hover:bg-[rgba(11,20,38,0.95)] transition-colors duration-200 cursor-pointer"
                      >
                        <span
                          className="mt-1.5 w-1.5 h-1.5 rounded-full shrink-0"
                          style={{ backgroundColor: dot, boxShadow: `0 0 8px ${dot}` }}
                        />
                        <p className="text-[0.85rem] leading-snug text-text font-medium group-hover:text-white">
                          {s.question}
                        </p>
                      </motion.button>
                    );
                  })}
                </div>
              ) : null}
            </motion.div>
          ) : (
            <>
              {chatHistory.map((msg, i) => (
                <div key={i} ref={(el) => { messageRefs.current[i] = el; }}>
                  <ChatBubble role={msg.role} content={msg.content} />
                </div>
              ))}

              {streamedResponse && (
                <ChatBubble role="assistant" content={streamedResponse} streaming />
              )}

              {loading && !streamedResponse && (
                <div className="flex items-start gap-3 mb-5">
                  <div className="shrink-0" style={{ width: 32 }} />
                  <div className="bg-surface2 border border-border rounded-2xl rounded-bl-[4px] px-4 py-3">
                    <AuraLoader size="sm" label={t("thinking")} />
                  </div>
                </div>
              )}

              <div ref={endRef} />
            </>
          )}
        </div>

        <div className="px-5 pb-5 pt-3 border-t border-border shrink-0">
          <ChatInput onSend={handleSend} disabled={loading} />
        </div>

      </section>
    </div>
  );
}
