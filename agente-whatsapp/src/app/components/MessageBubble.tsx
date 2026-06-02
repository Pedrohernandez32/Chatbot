interface MessageBubbleProps {
  message: {
    id: number;
    role: "user" | "assistant" | "human";
    content: string;
    created_at: number;
  };
}

export default function MessageBubble({ message }: MessageBubbleProps) {
  const isFromUser = message.role === "user";
  const isFromHuman = message.role === "human";
  const time = new Date(message.created_at * 1000).toLocaleTimeString("es-ES", {
    hour: "2-digit",
    minute: "2-digit",
  });

  return (
    <div
      className={`flex ${isFromUser ? "justify-end" : "justify-start"}`}
    >
      <div
        className={`max-w-xs rounded-lg px-4 py-2 ${
          isFromUser
            ? "bg-emerald-500 text-white"
            : isFromHuman
              ? "bg-blue-100 text-blue-900"
              : "bg-gray-100 text-gray-900"
        }`}
      >
        <p className="break-words">{message.content}</p>
        <p className={`text-xs mt-1 ${
          isFromUser
            ? "text-emerald-100"
            : isFromHuman
              ? "text-blue-600"
              : "text-gray-500"
        }`}>
          {time}
        </p>
      </div>
    </div>
  );
}
