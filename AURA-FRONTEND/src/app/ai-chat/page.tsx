"use client";
import { useState, useRef, useEffect } from "react";
import { useRouter } from "next/navigation";
import { PipelineBar } from "@/components/layout/PipelineBar";
import { PageHeader } from "@/components/layout/PageHeader";
import { EmptyState } from "@/components/ui/EmptyState";
import { ChatBubble } from "@/components/ai/ChatBubble";
import { ChatInput } from "@/components/ai/ChatInput";
import { streamAsk } from "@/lib/api";
import { useStore } from "@/lib/store";

export default function AiChatPage() {
  const router = useRouter();
  const { sessionId, meta, chatHistory, addMessage } = useStore();
  const [loading, setLoading] = useState(false);
  const [streamedResponse, setStreamedResponse] = useState("");
  const endRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [chatHistory, streamedResponse]);

  if (!meta || !sessionId) return <EmptyState />;

  const handleSend = async (question: string) => {
    setLoading(true);
    addMessage({ role: "user", content: question, ts: Date.now() });
    setStreamedResponse("");

    try {
      let fullText = "";
      for await (const chunk of streamAsk(sessionId, question, "claude")) {
        fullText += chunk;
        setStreamedResponse(fullText);
      }
      addMessage({ role: "assistant", content: fullText, ts: Date.now() });
      setStreamedResponse("");
    } catch (e: any) {
      addMessage({ role: "assistant", content: `Error: ${e.message}`, ts: Date.now() });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-[calc(100vh-8rem)]">
      <PipelineBar />
      <PageHeader icon="🤖" title="AI Assistant"
        subtitle="Ask questions about your dataset. The AI knows its structure and stats." />

      <div className="flex-1 overflow-y-auto pr-4 custom-scrollbar bg-surface border border-border rounded-lg p-6 mb-6">
        {chatHistory.length === 0 && (
          <div className="text-center text-text-m mt-10">
            <p>No messages yet. Ask a question to get started!</p>
            <p className="text-xs mt-2 text-text-d">Example: "What are the key trends in this dataset?"</p>
          </div>
        )}
        
        {chatHistory.map((msg, i) => (
          <ChatBubble key={i} role={msg.role} content={msg.content} />
        ))}
        
        {streamedResponse && (
          <ChatBubble role="assistant" content={streamedResponse} />
        )}
        
        {loading && !streamedResponse && (
          <div className="flex justify-start mb-4">
            <div className="bg-surface2 border border-border rounded-lg p-4 text-sm text-text-m">
              Thinking...
            </div>
          </div>
        )}
        <div ref={endRef} />
      </div>

      <div className="shrink-0 mb-6">
        <ChatInput onSend={handleSend} disabled={loading} />
      </div>

      <div className="flex justify-end pt-4 border-t border-border shrink-0">
        <button className="aura-btn" onClick={() => router.push("/docs")}>
          Next: Export & Docs →
        </button>
      </div>
    </div>
  );
}
