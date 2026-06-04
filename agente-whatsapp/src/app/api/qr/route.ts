import { NextRequest, NextResponse } from "next/server";
import { getConnectionState } from "@/lib/db";
import QRCode from "qrcode";

export async function GET(req: NextRequest) {
  try {
    const state = getConnectionState();

    if (!state?.qr_string) {
      return NextResponse.json(
        { error: "No QR available", status: state?.status || "disconnected" },
        { status: 404 }
      );
    }

    const qrImage = await QRCode.toDataURL(state.qr_string);

    return NextResponse.json({
      qr: qrImage,
      status: "qr",
      message: "Escanea con WhatsApp",
    });
  } catch (error) {
    return NextResponse.json(
      { error: "Failed to generate QR" },
      { status: 500 }
    );
  }
}
