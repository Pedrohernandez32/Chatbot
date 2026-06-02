import { setMode, getConversationById } from "@/lib/db";

export async function POST(
  request: Request,
  { params }: { params: { id: string } }
) {
  try {
    const convId = parseInt(params.id);
    const body = (await request.json()) as { mode: "AI" | "HUMAN" };

    if (!body.mode || !["AI", "HUMAN"].includes(body.mode)) {
      return Response.json(
        { error: "Invalid mode" },
        { status: 400 }
      );
    }

    const convo = getConversationById(convId);
    if (!convo) {
      return Response.json(
        { error: "Conversation not found" },
        { status: 404 }
      );
    }

    setMode(convId, body.mode);
    return Response.json({ success: true, mode: body.mode });
  } catch (error) {
    return Response.json(
      { error: String(error) },
      { status: 500 }
    );
  }
}
