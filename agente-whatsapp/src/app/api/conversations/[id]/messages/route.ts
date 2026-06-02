import { getMessages, insertMessage, getConversationById } from "@/lib/db";

export async function GET(
  request: Request,
  { params }: { params: { id: string } }
) {
  try {
    const convId = parseInt(params.id);
    const convo = getConversationById(convId);

    if (!convo) {
      return Response.json(
        { error: "Conversation not found" },
        { status: 404 }
      );
    }

    const messages = getMessages(convId, 50);
    return Response.json(messages);
  } catch (error) {
    return Response.json(
      { error: String(error) },
      { status: 500 }
    );
  }
}

export async function POST(
  request: Request,
  { params }: { params: { id: string } }
) {
  try {
    const convId = parseInt(params.id);
    const body = (await request.json()) as {
      role: "user" | "assistant" | "human";
      content: string;
    };

    if (!body.role || !body.content) {
      return Response.json(
        { error: "Missing role or content" },
        { status: 400 }
      );
    }

    const msg = insertMessage(convId, body.role, body.content);
    return Response.json(msg);
  } catch (error) {
    return Response.json(
      { error: String(error) },
      { status: 500 }
    );
  }
}
