"use client";

interface ModeToggleProps {
  conversationId: number;
  currentMode: "AI" | "HUMAN";
  onModeChange: (mode: "AI" | "HUMAN") => void;
}

export default function ModeToggle({
  conversationId,
  currentMode,
  onModeChange,
}: ModeToggleProps) {
  const handleToggle = async () => {
    const newMode = currentMode === "AI" ? "HUMAN" : "AI";
    try {
      const res = await fetch(
        `/api/conversations/${conversationId}/mode`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ mode: newMode }),
        }
      );

      if (res.ok) {
        onModeChange(newMode);
      }
    } catch (error) {
      console.error("Error changing mode:", error);
    }
  };

  return (
    <div className="flex items-center gap-2">
      <span className="text-sm text-gray-600">Modo:</span>
      <button
        onClick={handleToggle}
        className={`px-3 py-1 rounded-full text-sm font-medium transition-colors ${
          currentMode === "AI"
            ? "bg-emerald-100 text-emerald-700 hover:bg-emerald-200"
            : "bg-blue-100 text-blue-700 hover:bg-blue-200"
        }`}
      >
        {currentMode === "AI" ? "🤖 IA" : "👤 Humano"}
      </button>
    </div>
  );
}
