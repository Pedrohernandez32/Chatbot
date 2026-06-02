"use client";

import { useEffect, useState } from "react";
import MessageBubble from "./MessageBubble";
import ModeToggle from "./ModeToggle";

interface Message {
  id: number;
  role: "user" | "assistant" | "human";
  content: string;
  created_at: number;
}

interface ConversationPanelProps {
  conversationId: number;
}

export default function ConversationPanel({
  conversationId,
}: ConversationPanelProps) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [mode, setMode] = useState<"AI" | "HUMAN">("AI");

  useEffect(() => {
    const loadMessages = async () => {
      try {
        const res = await fetch(
          `/api/conversations/${conversationId}/messages`
        );
        const data = await res.json();
        setMessages(data);
      } catch (error) {
        console.error("Error loading messages:", error);
      }
    };

    loadMessages();
    const interval = setInterval(loadMessages, 2000);
    return () => clearInterval(interval);
  }, [conversationId]);

  return (
    <div className="flex-1 flex flex-col bg-white">
      {/* Header */}
      <div className="border-b border-gray-200 p-4 flex items-center justify-between">
        <h2 className="font-semibold text-gray-900">
          Conversación #{conversationId}
        </h2>
        <ModeToggle conversationId={conversationId} currentMode={mode} onModeChange={setMode} />
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 ? (
          <div className="flex items-center justify-center h-full text-gray-500">
            <p>No hay mensajes</p>
          </div>
        ) : (
          messages.map((msg) => (
            <MessageBubble key={msg.id} message={msg} />
          ))
        )}
      </div>
    </div>
  );
}
