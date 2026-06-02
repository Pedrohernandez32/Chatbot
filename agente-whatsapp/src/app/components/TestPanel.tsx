"use client";

import { useState } from "react";

export default function TestPanel() {
  const [phone, setPhone] = useState("573001234567");
  const [message, setMessage] = useState("");
  const [name, setName] = useState("Usuario Test");
  const [loading, setLoading] = useState(false);
  const [response, setResponse] = useState<string>("");

  const handleSendTest = async () => {
    if (!message.trim()) return;

    setLoading(true);
    setResponse("");

    try {
      const res = await fetch("/api/test/send-message", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          phone,
          message,
          name,
        }),
      });

      const data = (await res.json()) as {
        ai_response?: string;
        error?: string;
      };

      if (data.ai_response) {
        setResponse(data.ai_response);
        setMessage("");
      } else if (data.error) {
        setResponse(`Error: ${data.error}`);
      }

      // Refresh page to see new conversation
      setTimeout(() => {
        window.location.reload();
      }, 1500);
    } catch (error) {
      setResponse(`Error: ${String(error)}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-yellow-50 border-2 border-yellow-400 rounded-lg p-6 mb-6">
      <h3 className="text-lg font-bold text-yellow-900 mb-4">
        🧪 Modo Testing (Sin Baileys)
      </h3>

      <div className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            📱 Teléfono
          </label>
          <input
            type="text"
            value={phone}
            onChange={(e) => setPhone(e.target.value)}
            placeholder="573001234567"
            className="input"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            👤 Nombre
          </label>
          <input
            type="text"
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="Tu Nombre"
            className="input"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            💬 Mensaje
          </label>
          <textarea
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            placeholder="Escribe un mensaje para probar el bot..."
            className="input resize-none"
            rows={3}
          />
        </div>

        <button
          onClick={handleSendTest}
          disabled={loading || !message.trim()}
          className="btn btn-primary w-full disabled:opacity-50"
        >
          {loading ? "⏳ Enviando..." : "✅ Enviar Mensaje de Test"}
        </button>

        {response && (
          <div className="bg-blue-50 border border-blue-300 rounded p-4">
            <p className="text-sm font-medium text-blue-900 mb-2">
              Respuesta de IA:
            </p>
            <p className="text-blue-800">{response}</p>
          </div>
        )}
      </div>
    </div>
  );
}
