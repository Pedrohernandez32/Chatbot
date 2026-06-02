import { disconnect, clearAuth } from "@/lib/baileys/client";

export async function POST(request: Request) {
  try {
    const body = (await request.json()) as { clearAuth?: boolean };

    if (body.clearAuth) {
      clearAuth();
      console.log("[API] Auth cleared");
    } else {
      await disconnect();
      console.log("[API] Disconnected");
    }

    return Response.json({ success: true });
  } catch (error) {
    return Response.json(
      { error: String(error) },
      { status: 500 }
    );
  }
}
