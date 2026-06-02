"use client";

import { useEffect, useState } from "react";
import QRCode from "qrcode.react";

interface QRState {
  qr_string: string | null;
  status: string;
}

export default function QRScreen() {
  const [qrState, setQrState] = useState<QRState | null>(null);

  useEffect(() => {
    const checkQR = async () => {
      try {
        const res = await fetch("/api/status");
        const data = (await res.json()) as { hasQr: boolean; qr_string?: string };

        // Note: QR string is not exposed via API for security
        // This is just for visual feedback
        setQrState({
          qr_string: data.hasQr ? "qr-pending" : null,
          status: data.status,
        });
      } catch (error) {
        console.error("Error checking QR:", error);
      }
    };

    checkQR();
    const interval = setInterval(checkQR, 2000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="flex items-center justify-center h-screen bg-gradient-to-br from-emerald-50 to-gray-50">
      <div className="text-center p-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-4">
          Agente WhatsApp
        </h1>
        <p className="text-gray-600 mb-8">
          Abre WhatsApp en tu teléfono y escanea el código QR
        </p>

        <div className="bg-white rounded-lg shadow-lg p-8 mb-6 inline-block">
          {qrState?.qr_string ? (
            <div className="flex justify-center items-center h-64 w-64 bg-gray-100 rounded-lg">
              <div className="text-center">
                <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-emerald-500"></div>
                <p className="mt-4 text-sm text-gray-600">
                  Generando código QR...
                </p>
              </div>
            </div>
          ) : (
            <div className="text-gray-500 text-sm">
              Esperando QR...
            </div>
          )}
        </div>

        <div className="text-sm text-gray-500 space-y-2">
          <p>📱 Mantén tu teléfono cerca</p>
          <p>🔐 Tu código es privado y único</p>
          <p>⏱️ Válido por 60 segundos</p>
        </div>
      </div>
    </div>
  );
}
