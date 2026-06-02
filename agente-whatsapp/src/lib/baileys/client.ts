import { Boom } from "@hapi/boom";
import makeWASocket, {
  Browsers,
  DisconnectReason,
  fetchLatestBaileysVersion,
} from "@whiskeysockets/baileys";
import fs from "fs";
import path from "path";
import pino from "pino";
import { setConnectionState } from "../db";

const logger = pino({ level: "silent" });
const authDir = path.resolve(process.cwd(), "auth");
if (!fs.existsSync(authDir)) {
  fs.mkdirSync(authDir, { recursive: true });
}

const authPath = path.join(authDir, "auth.json");

let socket: ReturnType<typeof makeWASocket> | null = null;
let retryCount = 0;
let connectionAttempts = 0;

const loadAuthJson = () => {
  if (fs.existsSync(authPath)) {
    try {
      return JSON.parse(fs.readFileSync(authPath, "utf-8"));
    } catch {
      return null;
    }
  }
  return null;
};

const saveAuthJson = (auth: any) => {
  fs.writeFileSync(authPath, JSON.stringify(auth, null, 2));
};

export async function initializeSocket() {
  connectionAttempts++;
  console.log(`[Baileys] Intentando conectar (${connectionAttempts})...`);

  if (socket) {
    try {
      socket.ws?.close();
      socket.end();
    } catch (e) {
      // ignore
    }
    socket = null;
  }

  try {
    const savedAuth = loadAuthJson();

    const sock = makeWASocket({
      auth: savedAuth
        ? {
            creds: savedAuth.creds,
            keys: new Map(Object.entries(savedAuth.keys || {})),
          }
        : undefined,
      browser: Browsers.ubuntu("Desktop"),
      logger,
      version: await fetchLatestBaileysVersion(),
      // Estos parámetros mejoran la compatibilidad
      syncFullHistory: false,
      generateHighQualityLinkPreview: false,
    });


    sock.ev.on("connection.update", async (update) => {
      const { connection, lastDisconnect, qr } = update;

      if (qr) {
        console.log("\n");
        console.log("╔════════════════════════════════════════════╗");
        console.log("║          📱 CÓDIGO QR - ESCANEA CON       ║");
        console.log("║     WhatsApp > Más opciones > Vincular    ║");
        console.log("╚════════════════════════════════════════════╝");
        console.log(qr);
        console.log("╔════════════════════════════════════════════╗");
        console.log("\n");
        connectionAttempts = 0;
        retryCount = 0;
        setConnectionState({
          status: "qr",
          qr_string: qr,
        });
      }

      if (connection === "connecting") {
        console.log("[Baileys] ⏳ Conectando...");
        setConnectionState({ status: "connecting" });
      }

      if (connection === "open") {
        console.log("[Baileys] ✅ ¡CONECTADO!");
        console.log(`[Baileys] Teléfono: ${sock.user?.id}`);
        const phone = sock.user?.id?.split(":")?.[0];
        connectionAttempts = 0;
        retryCount = 0;
        setConnectionState({
          status: "connected",
          phone: phone || null,
          qr_string: null,
        });
      }

      if (connection === "close") {
        const shouldReconnect =
          (lastDisconnect?.error as Boom)?.output?.statusCode !==
          DisconnectReason.loggedOut;

        if (shouldReconnect) {
          retryCount++;
          const delay = Math.min(2000 + retryCount * 1000, 30000);
          console.log(`[Baileys] ⚠️ Desconectado. Reconectando en ${delay}ms...`);
          setTimeout(() => {
            initializeSocket();
          }, delay);
        } else {
          console.log("[Baileys] ❌ Sesión cerrada. Borra auth/ y escanea nuevamente.");
          if (fs.existsSync(authPath)) {
            fs.unlinkSync(authPath);
          }
          setConnectionState({ status: "disconnected" });
        }
      }
    });

    sock.ev.on("creds.update", (creds) => {
      const state = loadAuthJson() || {};
      state.creds = creds;
      saveAuthJson(state);
    });

    socket = sock;
    console.log("[Baileys] ✓ Socket inicializado");
    return sock;
  } catch (error) {
    console.error("[Baileys] ❌ Error:", error);
    setConnectionState({ status: "disconnected" });

    if (connectionAttempts < 10) {
      const delay = 5000 + Math.random() * 5000;
      console.log(
        `[Baileys] Reintentando en ${Math.round(delay)}ms... (${connectionAttempts}/10)`
      );
      setTimeout(() => {
        initializeSocket();
      }, delay);
    } else {
      console.log("[Baileys] Máximo de intentos alcanzado. Reinicia manualmente.");
    }
  }
}

export function getSocket() {
  return socket;
}

export async function disconnect() {
  if (socket) {
    try {
      socket.ws?.close();
      socket.end();
    } catch (e) {
      // ignore
    }
    socket = null;
  }
  setConnectionState({ status: "disconnected" });
}

export function clearAuth() {
  if (fs.existsSync(authPath)) {
    fs.unlinkSync(authPath);
  }
  setConnectionState({ status: "disconnected", qr_string: null, phone: null });
  console.log("[Baileys] Auth borrado. Reinicia para escanear nuevo QR.");
}
