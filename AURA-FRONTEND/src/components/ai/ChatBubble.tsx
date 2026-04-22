import { cn } from "@/lib/utils";

interface Props {
  role: "user" | "assistant";
  content: string;
}

export function ChatBubble({ role, content }: Props) {
  const isUser = role === "user";
  return (
    <div className={cn("flex w-full mb-4", isUser ? "justify-end" : "justify-start")}>
      <div className={cn(
        "max-w-[80%] rounded-lg p-4 text-sm whitespace-pre-wrap leading-relaxed shadow-card",
        isUser 
          ? "bg-purple text-white rounded-br-none" 
          : "bg-surface2 border border-border text-text rounded-bl-none"
      )}>
        {content}
      </div>
    </div>
  );
}
