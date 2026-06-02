import { Boom } from "@hapi/boom";
import makeWASocket, {
  Browsers,
  DisconnectReason,
} from "@whiskeysockets/baileys";
import fs from "fs";
import path from "path";
import pino from "pino";
import qrcode from "qrcode";
import { setConnectionState } from "../db";

const logger = pino({ level: "silent" });
const authDir = path.resolve(process.cwd(), "auth");
if (!fs.existsSync(authDir)) {
  fs.mkdirSync(authDir, { recursive: true });
}

const authPath = path.join(authDir, "auth_info.json");

let socket: ReturnType<typeof makeWASocket> | null = null;
let autoReconnectDelay = 0;

const loadAuthState = () => {
  if (fs.existsSync(authPath)) {
    try {
      const data = JSON.parse(fs.readFileSync(authPath, "utf-8"));
      return data;
    } catch {
      return null;
    }
  }
  return null;
};

const saveAuthState = (state: any) => {
  fs.writeFileSync(authPath, JSON.stringify(state, null, 2));
};

export async function initializeSocket() {
  console.log("[Baileys] Initializing socket...");

  if (socket) {
    try {
      socket.end(undefined as any);
    } catch (e) {
      console.error("[Baileys] Error closing previous socket:", e);
    }
  }

  try {
    const authState = loadAuthState();

    const sock = makeWASocket({
      browser: Browsers.ubuntu("Desktop"),
      auth: authState?.creds ? { creds: authState.creds } : undefined,
      logger,
      printQRInTerminal: true,
    }) as ReturnType<typeof makeWASocket>;

    sock.ev.on("connection.update", async (update) => {
      const { connection, lastDisconnect, qr } = update;

      if (qr) {
        console.log("\n[Baileys] ====== QR CODE ======");
        console.log(qr);
        console.log("[Baileys] ====== Scan with WhatsApp ======\n");
        setConnectionState({
          status: "qr",
          qr_string: qr,
        });
      }

      if (connection === "connecting") {
        console.log("[Baileys] Connecting...");
        setConnectionState({ status: "connecting" });
        autoReconnectDelay = 0;
      }

      if (connection === "open") {
        console.log("[Baileys] ✓ Connected successfully!");
        const phone = sock.user?.id?.split(":")?.[0];
        setConnectionState({
          status: "connected",
          phone: phone || null,
          qr_string: null,
        });
        autoReconnectDelay = 0;
      }

      if (connection === "close") {
        const reason = (lastDisconnect?.error as Boom)?.output?.statusCode;
        console.log(`[Baileys] Connection closed. Reason: ${reason}`);

        if (reason === DisconnectReason.loggedOut) {
          console.log("[Baileys] Logged out");
          setConnectionState({ status: "disconnected" });
        } else if (reason === 440) {
          console.log("[Baileys] Code 440 - device logged out");
          if (fs.existsSync(authPath)) {
            fs.unlinkSync(authPath);
          }
          autoReconnectDelay = 0;
          setTimeout(() => initializeSocket(), 5000);
        } else if (reason) {
          console.log(`[Baileys] Reconnecting due to error: ${reason}`);
          autoReconnectDelay = Math.min(autoReconnectDelay + 1, 5);
          setTimeout(() => initializeSocket(), 3000 * autoReconnectDelay);
        } else {
          console.log("[Baileys] Reconnecting...");
          setTimeout(() => initializeSocket(), 3000);
        }
      }
    });

    sock.ev.on("creds.update", async (creds) => {
      const state = loadAuthState() || {};
      state.creds = creds;
      saveAuthState(state);
    });

    socket = sock;
    return sock;
  } catch (error) {
    console.error("[Baileys] Error initializing socket:", error);
    setConnectionState({ status: "disconnected" });
    setTimeout(() => initializeSocket(), 5000);
  }
}

export function getSocket() {
  return socket;
}

export async function disconnect() {
  if (socket) {
    try {
      socket.end(undefined as any);
    } catch (e) {
      console.error("[Baileys] Error disconnecting:", e);
    }
    socket = null;
    setConnectionState({ status: "disconnected" });
  }
}

export function clearAuth() {
  if (fs.existsSync(authPath)) {
    fs.unlinkSync(authPath);
  }
  setConnectionState({ status: "disconnected", qr_string: null, phone: null });
  console.log("[Baileys] Auth cleared");
}
