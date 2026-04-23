"use client";
import { useState } from "react";
import { NeonButton } from "@/components/ui/NeonButton";

interface Props {
  onSend: (msg: string) => void;
  disabled: boolean;
}

export function ChatInput({ onSend, disabled }: Props) {
  const [text, setText] = useState("");

  const handleSend = () => {
    if (text.trim() && !disabled) {
      onSend(text.trim());
      setText("");
    }
  };

  return (
    <div className="flex gap-3 mt-4 items-center">
      <input
        type="text"
        className="aura-input flex-1"
        placeholder="Ask a question about your data..."
        value={text}
        onChange={(e) => setText(e.target.value)}
        onKeyDown={(e) => e.key === "Enter" && handleSend()}
        disabled={disabled}
      />
      <NeonButton onClick={handleSend} disabled={disabled || !text.trim()} size="sm">
        Send
      </NeonButton>
    </div>
  );
}
