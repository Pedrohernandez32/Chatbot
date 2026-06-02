"use client";

async function handleDisconnect(clearAuth: boolean) {
  try {
    await fetch("/api/disconnect", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ clearAuth }),
    });
    window.location.reload();
  } catch (error) {
    console.error("Disconnect error:", error);
  }
}

interface DashboardHeaderProps {
  phone: string | null;
}

export default function DashboardHeader({ phone }: DashboardHeaderProps) {
  return (
    <header className="bg-white border-b border-gray-200 shadow-sm">
      <div className="px-6 py-4 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="flex-1">
            <h1 className="text-2xl font-bold text-gray-900">
              Agente WhatsApp
            </h1>
            {phone && (
              <p className="text-sm text-gray-500 mt-1">
                Conectado como: {phone}
              </p>
            )}
          </div>
        </div>

        <div className="flex gap-2">
          <button
            onClick={() => handleDisconnect(false)}
            className="btn btn-secondary"
          >
            Desconectar
          </button>
          <button
            onClick={() => handleDisconnect(true)}
            className="btn btn-danger"
          >
            Cerrar Sesión
          </button>
        </div>
      </div>
    </header>
  );
}
