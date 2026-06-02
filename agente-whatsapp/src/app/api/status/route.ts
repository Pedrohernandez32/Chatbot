import { getConnectionState } from "@/lib/db";

export async function GET() {
  try {
    const state = getConnectionState();
    return Response.json({
      status: state.status,
      phone: state.phone,
      hasQr: !!state.qr_string,
      updatedAt: state.updated_at,
    });
  } catch (error) {
    return Response.json(
      { error: String(error) },
      { status: 500 }
    );
  }
}
