import {
  getOrCreateConversation,
  insertMessage,
  getRecentHistory,
  enqueueOutbox,
} from "@/lib/db";
import { callOpenRouter } from "@/lib/openrouter";

export async function POST(request: Request) {
  try {
    const body = (await request.json()) as {
      phone: string;
      message: string;
      name?: string;
    };

    if (!body.phone || !body.message) {
      return Response.json(
        { error: "Missing phone or message" },
        { status: 400 }
      );
    }

    // Create or get conversation
    const convo = getOrCreateConversation(body.phone, body.name);

    // Store user message
    insertMessage(convo.id, "user", body.message);

    // Get conversation history
    const history = getRecentHistory(convo.id, 10);
    const messages = history.map((msg) => ({
      role: msg.role === "assistant" ? ("assistant" as const) : ("user" as const),
      content: msg.content,
    }));

    // Add current message if not already there
    if (!messages.length || messages[messages.length - 1].content !== body.message) {
      messages.push({ role: "user", content: body.message });
    }

    // Call LLM
    try {
      const response = await callOpenRouter(messages);
      insertMessage(convo.id, "assistant", response);
      enqueueOutbox(convo.id, body.phone, response);

      return Response.json({
        success: true,
        conversation_id: convo.id,
        user_message: body.message,
        ai_response: response,
      });
    } catch (error) {
      const errorMsg =
        "Lo siento, hubo un problema procesando tu mensaje. Por favor intenta de nuevo.";
      insertMessage(convo.id, "assistant", errorMsg);
      enqueueOutbox(convo.id, body.phone, errorMsg);

      return Response.json({
        success: true,
        conversation_id: convo.id,
        user_message: body.message,
        ai_response: errorMsg,
        error: String(error),
      });
    }
  } catch (error) {
    return Response.json(
      { error: String(error) },
      { status: 500 }
    );
  }
}
