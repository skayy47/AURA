"use client";
import { motion } from "framer-motion";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
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
          "max-w-[80%] px-4 py-3 text-sm leading-relaxed shadow-[0_2px_10px_rgba(0,0,0,0.35)]",
          isUser
            ? "bg-gradient-to-br from-[#6C3FED] to-[#3B82F6] text-white rounded-2xl rounded-ee-[4px] whitespace-pre-wrap"
            : "bg-surface2 border border-border text-text rounded-2xl rounded-es-[4px]"
        )}
      >
        {/* User bubbles and in-flight streams: plain pre-wrap text */}
        {isUser || streaming ? (
          <>
            <span className="whitespace-pre-wrap">{content}</span>
            {streaming && (
              <span className="inline-block w-[2px] h-[1em] align-middle ms-[1px] bg-aurora-cyan animate-pulse" />
            )}
          </>
        ) : (
          /* Completed assistant messages: full markdown */
          <ReactMarkdown
            remarkPlugins={[remarkGfm]}
            components={{
              h1: ({ children }) => (
                <h1 className="text-base font-bold text-white mb-2 mt-4 first:mt-0 pb-1 border-b border-border">
                  {children}
                </h1>
              ),
              h2: ({ children }) => (
                <h2 className="text-sm font-bold text-white mb-2 mt-3 first:mt-0">
                  {children}
                </h2>
              ),
              h3: ({ children }) => (
                <h3 className="text-sm font-semibold text-text mb-1.5 mt-2 first:mt-0">
                  {children}
                </h3>
              ),
              p: ({ children }) => (
                <p className="mb-2 last:mb-0 leading-relaxed">{children}</p>
              ),
              /* Block code: styled pre wraps raw code */
              pre: ({ children }) => (
                <pre className="bg-[rgba(0,0,0,0.5)] border border-border rounded-lg px-4 py-3 overflow-x-auto my-2.5 text-[0.76rem] font-geist-mono text-slate-200 whitespace-pre leading-relaxed">
                  {children}
                </pre>
              ),
              /* Inline code: cyan pill; block code: let pre handle it */
              code: ({ className, children, ...props }: any) => {
                const isBlock = Boolean(className);
                return isBlock ? (
                  <code className={cn("font-geist-mono", className)} {...props}>
                    {children}
                  </code>
                ) : (
                  <code
                    className="bg-[rgba(0,229,255,0.1)] text-aurora-cyan text-[0.8em] px-1.5 py-0.5 rounded font-geist-mono"
                    {...props}
                  >
                    {children}
                  </code>
                );
              },
              ul: ({ children }) => (
                <ul className="space-y-1 mb-2 ml-1">{children}</ul>
              ),
              ol: ({ children }) => (
                <ol className="list-decimal list-inside space-y-1 mb-2 text-text">{children}</ol>
              ),
              li: ({ children }) => (
                <li className="flex gap-2 items-start leading-snug">
                  <span className="text-aurora-cyan mt-[0.35em] shrink-0 text-xs">▸</span>
                  <span className="flex-1">{children}</span>
                </li>
              ),
              strong: ({ children }) => (
                <strong className="font-semibold text-white">{children}</strong>
              ),
              em: ({ children }) => (
                <em className="italic text-text-m">{children}</em>
              ),
              /* Tables */
              table: ({ children }) => (
                <div className="overflow-x-auto my-2.5 rounded-lg border border-border">
                  <table className="text-[0.76rem] border-collapse w-full">{children}</table>
                </div>
              ),
              thead: ({ children }) => (
                <thead className="bg-surface">{children}</thead>
              ),
              th: ({ children }) => (
                <th className="px-3 py-2 text-left font-semibold text-text-m border-b border-border">
                  {children}
                </th>
              ),
              td: ({ children }) => (
                <td className="px-3 py-1.5 text-text border-b border-border/50 last:border-b-0">
                  {children}
                </td>
              ),
              blockquote: ({ children }) => (
                <blockquote className="border-l-2 border-cyan/40 pl-3 my-2 text-text-m italic">
                  {children}
                </blockquote>
              ),
              hr: () => <hr className="border-border my-3" />,
              a: ({ href, children }) => (
                <a
                  href={href}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-aurora-cyan underline underline-offset-2 hover:text-white transition-colors"
                >
                  {children}
                </a>
              ),
            }}
          >
            {content}
          </ReactMarkdown>
        )}
      </div>
    </motion.div>
  );
}
