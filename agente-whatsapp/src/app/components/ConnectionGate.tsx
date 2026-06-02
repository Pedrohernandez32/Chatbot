"use client";

import { useEffect, useState } from "react";
import QRScreen from "./QRScreen";
import DashboardHeader from "./DashboardHeader";
import ConversationList from "./ConversationList";

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
    return <QRScreen />;
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
