"use client";

import { useEffect, useState } from "react";

export default function QRPage() {
  const [qr, setQr] = useState<string | null>(null);
  const [status, setStatus] = useState<string>("loading");
  const [retries, setRetries] = useState(0);

  useEffect(() => {
    const fetchQR = async () => {
      try {
        const res = await fetch("/api/qr");
        if (res.ok) {
          const data = await res.json();
          setQr(data.qr);
          setStatus("ready");
        } else {
          const data = await res.json();
          setStatus(data.status || "error");
        }
      } catch (error) {
        setStatus("error");
      }
    };

    const timer = setInterval(fetchQR, 2000);
    fetchQR();

    return () => clearInterval(timer);
  }, []);

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl shadow-2xl p-8 max-w-md w-full">
        <div className="text-center">
          <h1 className="text-3xl font-bold text-gray-800 mb-2">
            📱 WhatsApp Bot
          </h1>
          <p className="text-gray-600 mb-6">Universidad de Medellín</p>

          {status === "loading" && (
            <div className="py-8">
              <div className="animate-spin rounded-full h-12 w-12 border-4 border-indigo-200 border-t-indigo-600 mx-auto"></div>
              <p className="text-gray-600 mt-4">Cargando QR...</p>
            </div>
          )}

          {status === "ready" && qr && (
            <div className="py-8">
              <div className="bg-gray-50 p-4 rounded-lg mb-6 inline-block">
                <img src={qr} alt="QR Code" className="w-64 h-64" />
              </div>
              <div className="bg-green-50 border border-green-200 rounded-lg p-4 mb-6">
                <p className="text-green-800 font-semibold">✅ QR Listo</p>
                <p className="text-green-700 text-sm mt-2">
                  Escanea con WhatsApp
                </p>
              </div>
              <div className="text-left bg-blue-50 border border-blue-200 rounded-lg p-4 text-sm text-blue-900">
                <strong>Pasos:</strong>
                <ol className="mt-2 space-y-1 ml-4 list-decimal">
                  <li>Abre WhatsApp</li>
                  <li>Más opciones (⋮)</li>
                  <li>Dispositivos vinculados</li>
                  <li>Vincular un dispositivo</li>
                  <li>Escanea este código</li>
                </ol>
              </div>
            </div>
          )}

          {status === "qr" && (
            <div className="py-8">
              <div className="animate-pulse">
                <div className="h-64 w-64 bg-gray-200 rounded-lg mx-auto"></div>
              </div>
              <p className="text-gray-600 mt-4">Generando QR...</p>
            </div>
          )}

          {status === "connected" && (
            <div className="py-8">
              <div className="text-6xl mb-4">✅</div>
              <p className="text-green-600 font-bold text-xl">
                ¡CONECTADO!
              </p>
              <p className="text-gray-600 mt-2">
                Ve a <a href="/" className="text-indigo-600 underline">
                  Dashboard
                </a>
              </p>
            </div>
          )}

          {status === "disconnected" && (
            <div className="py-8">
              <div className="text-6xl mb-4">⏳</div>
              <p className="text-gray-600">Esperando conexión...</p>
              <p className="text-sm text-gray-500 mt-2">
                Reinicia el bot si es necesario
              </p>
            </div>
          )}

          {status === "error" && (
            <div className="py-8">
              <div className="text-6xl mb-4">❌</div>
              <p className="text-red-600 font-semibold">Error</p>
              <p className="text-gray-600 text-sm mt-2">
                No se pudo cargar el QR
              </p>
              <button
                onClick={() => window.location.reload()}
                className="mt-4 bg-indigo-600 text-white px-4 py-2 rounded-lg hover:bg-indigo-700 transition"
              >
                Reintentar
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
