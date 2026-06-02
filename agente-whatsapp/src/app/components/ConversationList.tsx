"use client";

import { useEffect, useState } from "react";
import ConversationPanel from "./ConversationPanel";

interface Conversation {
  id: number;
  phone: string;
  name: string | null;
  mode: "AI" | "HUMAN";
  last_message_preview: string | null;
  last_message_at: number | null;
}

export default function ConversationList() {
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [selectedId, setSelectedId] = useState<number | null>(null);

  useEffect(() => {
    const loadConvos = async () => {
      try {
        const res = await fetch("/api/conversations");
        const data = await res.json();
        setConversations(data);
        if (!selectedId && data.length > 0) {
          setSelectedId(data[0].id);
        }
      } catch (error) {
        console.error("Error loading conversations:", error);
      }
    };

    loadConvos();
    const interval = setInterval(loadConvos, 3000);
    return () => clearInterval(interval);
  }, [selectedId]);

  const handleDelete = async (id: number) => {
    try {
      await fetch("/api/conversations", {
        method: "DELETE",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ id }),
      });
      setConversations(conversations.filter((c) => c.id !== id));
      if (selectedId === id) setSelectedId(null);
    } catch (error) {
      console.error("Error deleting conversation:", error);
    }
  };

  return (
    <div className="flex flex-1 overflow-hidden">
      {/* Sidebar */}
      <div className="w-80 bg-white border-r border-gray-200 overflow-y-auto">
        <div className="p-4">
          <h2 className="font-semibold text-gray-900 mb-4">
            Conversaciones ({conversations.length})
          </h2>

          {conversations.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              <p>No hay conversaciones aún</p>
              <p className="text-sm mt-2">
                Los mensajes de WhatsApp aparecerán aquí
              </p>
            </div>
          ) : (
            <div className="space-y-2">
              {conversations.map((conv) => (
                <div
                  key={conv.id}
                  onClick={() => setSelectedId(conv.id)}
                  className={`p-3 rounded-lg cursor-pointer transition-colors ${
                    selectedId === conv.id
                      ? "bg-emerald-50 border border-emerald-200"
                      : "hover:bg-gray-50 border border-gray-100"
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex-1 min-w-0">
                      <p className="font-medium text-gray-900 truncate">
                        {conv.name || conv.phone}
                      </p>
                      <p className="text-sm text-gray-500 truncate">
                        {conv.last_message_preview || "Sin mensajes"}
                      </p>
                    </div>
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        handleDelete(conv.id);
                      }}
                      className="text-red-500 hover:text-red-700 text-sm ml-2"
                    >
                      ✕
                    </button>
                  </div>
                  <div className="flex items-center gap-2 mt-2">
                    <span
                      className={`text-xs px-2 py-1 rounded-full ${
                        conv.mode === "AI"
                          ? "bg-emerald-100 text-emerald-700"
                          : "bg-blue-100 text-blue-700"
                      }`}
                    >
                      {conv.mode}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Panel */}
      {selectedId ? (
        <ConversationPanel conversationId={selectedId} />
      ) : (
        <div className="flex-1 flex items-center justify-center bg-gray-50">
          <div className="text-center">
            <p className="text-gray-500">
              Selecciona una conversación para empezar
            </p>
          </div>
        </div>
      )}
    </div>
  );
}
