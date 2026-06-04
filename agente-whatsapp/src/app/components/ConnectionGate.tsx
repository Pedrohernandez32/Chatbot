"use client";

import { useEffect, useState } from "react";
import QRScreen from "./QRScreen";
import DashboardHeader from "./DashboardHeader";
import ConversationList from "./ConversationList";
import TestPanel from "./TestPanel";

interface ConnectionStatus {
  status: "disconnected" | "qr" | "connecting" | "connected";
  phone: string | null;
}

export default function ConnectionGate() {
  const [connStatus, setConnStatus] = useState<ConnectionStatus | null>(null);

  useEffect(() => {
    const checkStatus = async () => {
      try {
        const res = await fetch("/api/status");
        const data = (await res.json()) as {
          status: ConnectionStatus["status"];
          phone: string | null;
        };
        setConnStatus(data);
      } catch (error) {
        console.error("Error checking status:", error);
      }
    };

    checkStatus();
    const interval = setInterval(checkStatus, 2000);
    return () => clearInterval(interval);
  }, []);

  if (!connStatus) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-emerald-500"></div>
          <p className="mt-4 text-gray-600">Iniciando...</p>
        </div>
      </div>
    );
  }

  if (connStatus.status === "disconnected" || connStatus.status === "qr") {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
        <div className="bg-white rounded-2xl shadow-2xl p-8 max-w-md w-full text-center">
          <h2 className="text-2xl font-bold text-gray-800 mb-4">
            📱 WhatsApp Desconectado
          </h2>
          <p className="text-gray-600 mb-6">
            {connStatus.status === "qr"
              ? "Escanea el QR para conectar"
              : "Bot no conectado"}
          </p>
          <a
            href="/qr"
            target="_blank"
            rel="noopener noreferrer"
            className="inline-block bg-indigo-600 text-white px-6 py-3 rounded-lg font-semibold hover:bg-indigo-700 transition mb-4"
          >
            📲 Abrir QR en Nueva Pestaña
          </a>
          <p className="text-sm text-gray-500 mt-6">
            O usa <strong>Testing Mode</strong> abajo
          </p>
          <div className="mt-8 p-4 bg-gray-50 rounded-lg">
            <TestPanel />
          </div>
        </div>
      </div>
    );
  }

  if (connStatus.status === "connecting") {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-emerald-500"></div>
          <p className="mt-4 text-gray-600">Conectando...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex h-screen flex-col">
      <DashboardHeader phone={connStatus.phone} />
      <ConversationList />
    </div>
  );
}
