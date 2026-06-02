import { listConversations, deleteConversation } from "@/lib/db";

export async function GET() {
  try {
    const convos = listConversations();
    return Response.json(convos);
  } catch (error) {
    return Response.json(
      { error: String(error) },
      { status: 500 }
    );
  }
}

export async function DELETE(request: Request) {
  try {
    const body = (await request.json()) as { id: number };

    if (!body.id) {
      return Response.json(
        { error: "Missing id" },
        { status: 400 }
      );
    }

    deleteConversation(body.id);
    return Response.json({ success: true });
  } catch (error) {
    return Response.json(
      { error: String(error) },
      { status: 500 }
    );
  }
}
