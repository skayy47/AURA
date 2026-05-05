"use client";
import { motion } from "framer-motion";
import { cn } from "@/lib/utils";
import { BotMiniAvatar } from "./BotMiniAvatar";

interface Props {
  role: "user" | "assistant";
  content: string;
  streaming?: boolean;
  highlight?: boolean;
}

export function ChatBubble({ role, content, streaming, highlight }: Props) {
  const isUser = role === "user";
  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3, ease: "easeOut" }}
      className={cn(
        "flex w-full mb-5 gap-3 items-start",
        isUser ? "justify-end" : "justify-start",
        highlight && "ring-2 ring-purple/40 rounded-2xl -m-1 p-1 transition-shadow"
      )}
    >
      {!isUser && <BotMiniAvatar size={32} className="mt-1" />}
      <div
        className={cn(
          "max-w-[75%] px-4 py-3 text-sm whitespace-pre-wrap leading-relaxed shadow-[0_2px_10px_rgba(0,0,0,0.35)]",
          isUser
            ? "bg-gradient-to-br from-[#6C3FED] to-[#3B82F6] text-white rounded-2xl rounded-ee-[4px]"
            : "bg-surface2 border border-border text-text rounded-2xl rounded-es-[4px]"
        )}
      >
        {content}
        {streaming && (
          <span className="inline-block w-[2px] h-[1em] align-middle ms-[1px] bg-aurora-cyan animate-pulse" />
        )}
      </div>
    </motion.div>
  );
}
