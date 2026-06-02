import { Boom } from "@hapi/boom";
import makeWASocket, {
  AuthenticationCreds,
  AuthenticationState,
  Browsers,
  DisconnectReason,
  proto,
} from "@whiskeysockets/baileys";
import { randomBytes } from "crypto";
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

const useAuthState = (): { state: AuthenticationState; saveCreds: () => void } => {
  let creds: AuthenticationCreds | null = null;
  let keys: Record<string, string> = {};

  const saveCreds = () => {
    if (!creds) return;
    fs.writeFileSync(authPath, JSON.stringify({ creds, keys }, null, 2));
  };

  if (fs.existsSync(authPath)) {
    const data = JSON.parse(fs.readFileSync(authPath, "utf-8"));
    creds = data.creds;
    keys = data.keys;
  }

  return {
    state: {
      creds: creds || {
        me: { id: "", name: "" },
        registered: false,
        platform: "web",
      },
      keys: new Map(Object.entries(keys)),
    } as any,
    saveCreds,
  };
};

const fetchLatestBaileysVersion = async (): Promise<[number, number, number]> => {
  return [2, 2400, 1];
};

export async function initializeSocket() {
  console.log("[Baileys] Initializing socket...");

  if (socket) {
    socket.end(undefined as any);
  }

  const { state, saveCreds } = useAuthState();
  const version = await fetchLatestBaileysVersion();

  const sock = makeWASocket({
    version,
    logger,
    browser: Browsers.macOS("Desktop"),
    auth: state,
    getMessage: async (key) => {
      return {
        conversation: "",
      };
    },
  }) as ReturnType<typeof makeWASocket>;

  sock.ev.on("creds.update", saveCreds);

  sock.ev.on("connection.update", async (update) => {
    const { connection, lastDisconnect, qr } = update;

    if (qr) {
      console.log("[Baileys] QR Code generated");
      const qrUrl = await qrcode.toDataURL(qr);
      setConnectionState({
        status: "qr",
        qr_string: qr,
      });
      console.log("[Baileys] QR saved to DB");
    }

    if (connection === "connecting") {
      console.log("[Baileys] Connecting...");
      setConnectionState({ status: "connecting" });
      autoReconnectDelay = 0;
    }

    if (connection === "open") {
      console.log("[Baileys] Connected!");
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
      const shouldReconnect = reason !== DisconnectReason.loggedOut;

      if (shouldReconnect) {
        // Handle code 440 (device logged out) with backoff
        if (reason === 440) {
          console.log("[Baileys] Code 440 - device logged out, clearing auth and restarting...");
          if (fs.existsSync(authPath)) {
            fs.unlinkSync(authPath);
          }
          autoReconnectDelay = Math.min(autoReconnectDelay + 1, 10);
          const delay = 15 * 1000 * autoReconnectDelay;
          console.log(`[Baileys] Reconnecting in ${delay}ms...`);
          setTimeout(() => {
            initializeSocket();
          }, delay);
        } else {
          console.log(`[Baileys] Reconnecting due to: ${reason}`);
          autoReconnectDelay = Math.min(autoReconnectDelay + 1, 5);
          setTimeout(() => {
            initializeSocket();
          }, 3000 * autoReconnectDelay);
        }
      } else {
        console.log("[Baileys] Logged out - waiting for manual reconnection");
        setConnectionState({ status: "disconnected" });
      }
    }
  });

  socket = sock;
  return sock;
}

export function getSocket() {
  return socket;
}

export async function disconnect() {
  if (socket) {
    socket.end(undefined as any);
    socket = null;
    setConnectionState({ status: "disconnected" });
  }
}

export function clearAuth() {
  if (fs.existsSync(authPath)) {
    fs.unlinkSync(authPath);
  }
  setConnectionState({ status: "disconnected", qr_string: null, phone: null });
}
