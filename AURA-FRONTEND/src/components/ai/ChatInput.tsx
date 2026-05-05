"use client";
import { useState, useRef, useEffect } from "react";

interface Props {
  onSend: (msg: string) => void;
  disabled: boolean;
  externalValue?: string;
  onExternalConsumed?: () => void;
}

const MAX_LINES = 4;
const LINE_HEIGHT = 22;
const BASE_HEIGHT = 48;

export function ChatInput({ onSend, disabled, externalValue, onExternalConsumed }: Props) {
  const [text, setText] = useState("");
  const taRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    if (externalValue && externalValue.length > 0) {
      setText(externalValue);
      onExternalConsumed?.();
      requestAnimationFrame(() => taRef.current?.focus());
    }
  }, [externalValue, onExternalConsumed]);

  const autoresize = () => {
    const ta = taRef.current;
    if (!ta) return;
    ta.style.height = "auto";
    const next = Math.min(ta.scrollHeight, BASE_HEIGHT + LINE_HEIGHT * (MAX_LINES - 1));
    ta.style.height = `${next}px`;
  };

  useEffect(autoresize, [text]);

  const submit = () => {
    const value = text.trim();
    if (!value || disabled) return;
    onSend(value);
    setText("");
    requestAnimationFrame(() => {
      if (taRef.current) taRef.current.style.height = `${BASE_HEIGHT}px`;
    });
  };

  const onKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      submit();
    }
  };

  const hasContent = text.trim().length > 0;

  return (
    <div className="w-full">
      <div className="aura-chat-input relative">
        <textarea
          ref={taRef}
          rows={1}
          className="w-full resize-none bg-transparent outline-none text-sm text-text placeholder-text-d py-3 ps-4 pe-14 leading-[22px]"
          placeholder="Ask about your data…"
          value={text}
          onChange={(e) => setText(e.target.value)}
          onKeyDown={onKeyDown}
          disabled={disabled}
          style={{ minHeight: BASE_HEIGHT }}
        />

        <button
          type="button"
          onClick={submit}
          disabled={disabled || !hasContent}
          aria-label="Send message"
          className={`absolute end-2 bottom-2 w-9 h-9 rounded-full flex items-center justify-center
                      transition-all duration-200
                      ${hasContent && !disabled
                        ? "bg-gradient-to-br from-aurora-purple to-aurora-blue text-white shadow-[0_0_18px_rgba(108,63,237,0.55)] hover:scale-105"
                        : "bg-surface2 text-text-d cursor-not-allowed"}`}
        >
          <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M5 12h14" />
            <path d="m13 6 6 6-6 6" />
          </svg>
        </button>
      </div>
      <p className="text-[0.62rem] text-text-d mt-1.5 px-1 tracking-wide">
        Enter to send <span className="text-text-d/70">·</span> Shift+Enter for new line
      </p>
    </div>
  );
}
