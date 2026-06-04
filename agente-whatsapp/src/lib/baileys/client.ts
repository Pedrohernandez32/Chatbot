import { Boom } from "@hapi/boom";
import makeWASocket, {
  Browsers,
  DisconnectReason,
  fetchLatestBaileysVersion,
  useMultiFileAuthState,
} from "@whiskeysockets/baileys";
import fs from "fs";
import path from "path";
import pino from "pino";
import qrcode from "qrcode-terminal";
import { setConnectionState } from "../db";

const logger = pino({ level: "silent" });
const authDir = path.resolve(process.cwd(), "auth");

let socket: ReturnType<typeof makeWASocket> | null = null;
let attemptCount = 0;
const MAX_ATTEMPTS = 50;

export async function initializeSocket() {
  attemptCount++;
  console.log(`\n[WhatsApp] 🔄 INTENTO ${attemptCount}/${MAX_ATTEMPTS}`);

  if (socket) {
    try {
      socket.ws?.close?.();
      await socket.end?.();
    } catch (e) {
      //
    }
    socket = null;
    await new Promise((r) => setTimeout(r, 1000));
  }

  try {
    console.log("[WhatsApp] Cargando estado...");
    const { state, saveCreds } = await useMultiFileAuthState(authDir);

    const version = await fetchLatestBaileysVersion();
    console.log("[WhatsApp] Versión Baileys:", version.version.join("."));

    const sock = makeWASocket({
      version: version.version as [number, number, number],
      auth: state,
      logger,
      browser: Browsers.ubuntu("Desktop"),
      syncFullHistory: false,
      shouldIgnoreJid: (jid: string) => !jid.includes("@s.whatsapp.net"),
      markOnlineOnConnect: true,
      retryRequestDelayMs: 100,
      maxMsToWaitForConnection: 60000,
      defaultQueryTimeoutMs: 0,
      qrTimeout: 120000,
      emitOwnEventsOnly: true,
      connectTimeoutMs: 60000,
      keepAliveIntervalMs: 15000,
      connectionConfig: {
        maxRetries: 10,
        retryRequestDelayMs: 100,
      },
    });

    let qrShown = false;

    sock.ev.on("connection.update", async (update) => {
      const { connection, lastDisconnect, qr } = update;

      console.log("[WhatsApp] Evento:", {
        connection,
        hasQR: !!qr,
        errorCode: (lastDisconnect?.error as any)?.output?.statusCode,
      });

      if (qr) {
        if (!qrShown) {
          qrShown = true;
          console.log("[WhatsApp] 📱 QR disponible en: http://localhost:3000/qr");
        }

        attemptCount = 0;
        setConnectionState({
          status: "qr",
          qr_string: qr,
        });
      }

      if (connection === "connecting") {
        console.log("[WhatsApp] ⏳ Conectando a WhatsApp Web...");
        setConnectionState({ status: "connecting" });
      }

      if (connection === "open") {
        qrShown = false;
        console.log("[WhatsApp] ✅ ¡CONECTADO EXITOSAMENTE!");
        console.log(`[WhatsApp] Número: ${sock.user?.id}`);
        console.log("[WhatsApp] Listo para recibir mensajes...");

        attemptCount = 0;
        setConnectionState({
          status: "connected",
          phone: sock.user?.id?.split(":")?.[0] || null,
          qr_string: null,
        });

        // Escuchar TODOS los eventos para diagnosticar
        console.log("[WhatsApp] 🎧 Listeners de eventos activados");

        // Interceptor de TODOS los eventos
        const originalOn = sock.ev.on.bind(sock.ev);
        sock.ev.on = function(event, listener) {
          if (!event.includes('connection') && !event.includes('qr')) {
            console.log(`[WhatsApp] 📡 Evento disponible: ${event}`);
          }
          return originalOn(event, listener);
        };

        // Listeners principales
        sock.ev.on("messages.upsert", async (m) => {
          console.log(`[WhatsApp] 📨 messages.upsert: ${m.messages.length} mensaje(s)`);
          for (const msg of m.messages) {
            console.log(`[WhatsApp] ├─ fromMe=${msg.key.fromMe}, jid=${msg.key.remoteJid}`);
            if (!msg.key.fromMe) {
              try {
                const { handleIncomingMessage } = await import("../baileys/handler");
                await handleIncomingMessage(msg);
              } catch (error) {
                console.error("[WhatsApp] Error:", error);
              }
            }
          }
        });

        // Intentar otros eventos posibles
        sock.ev.on("messages", async (m) => {
          console.log(`[WhatsApp] 🔔 messages event recibido`);
        });

        sock.ev.on("chats.upsert", (chats) => {
          console.log(`[WhatsApp] 💬 chats.upsert: ${chats.length} chat(s)`);
        });

        // Log periódico para confirmar que está escuchando
        setInterval(() => {
          console.log("[WhatsApp] ✓ Bot activo y escuchando...");
        }, 30000);
      }

      if (connection === "close") {
        const reason = (lastDisconnect?.error as Boom)?.output?.statusCode;
        const shouldReconnect =
          reason !== DisconnectReason.loggedOut && attemptCount < MAX_ATTEMPTS;

        if (shouldReconnect) {
          const delay = Math.min(2000 + attemptCount * 500, 30000);
          console.log(
            `[WhatsApp] ❌ Desconectado (código ${reason}). Reintentando en ${(delay / 1000).toFixed(1)}s...`
          );
          setTimeout(() => initializeSocket(), delay);
        } else {
          console.log(`[WhatsApp] ❌ Conexión perdida. ${attemptCount >= MAX_ATTEMPTS ? "Máximo de intentos alcanzado." : "Sesión cerrada."}`);
          setConnectionState({ status: "disconnected" });
        }
      }
    });

    sock.ev.on("creds.update", () => {
      console.log("[WhatsApp] 💾 Guardando credenciales...");
      saveCreds();
    });

    sock.ev.on("call", async (node) => {
      console.log("[WhatsApp] 📞 Llamada entrante (ignorada)");
    });

    process.on("uncaughtException", (error) => {
      console.error("[WhatsApp] Error sin capturar:", error.message);
    });

    socket = sock;
    console.log("[WhatsApp] ✓ Socket inicializado con Opera GX");
    return sock;
  } catch (error) {
    console.error("[WhatsApp] ❌ Error:", String(error).substring(0, 100));

    if (attemptCount < MAX_ATTEMPTS) {
      const delay = 3000 + attemptCount * 500;
      console.log(
        `[WhatsApp] Reintentando en ${(delay / 1000).toFixed(1)}s (${attemptCount}/${MAX_ATTEMPTS})...`
      );
      setTimeout(() => initializeSocket(), delay);
    } else {
      console.log("[WhatsApp] ❌ NO SE PUDO CONECTAR DESPUÉS DE", MAX_ATTEMPTS, "INTENTOS");
      setConnectionState({ status: "disconnected" });
    }
  }
}

export function getSocket() {
  return socket;
}

export async function disconnect() {
  if (socket) {
    try {
      await socket.end?.();
    } catch (e) {
      //
    }
    socket = null;
  }
  setConnectionState({ status: "disconnected" });
}

export async function clearAuth() {
  try {
    if (fs.existsSync(authDir)) {
      fs.rmSync(authDir, { recursive: true, force: true });
    }
  } catch (e) {
    //
  }
  console.log("[WhatsApp] Auth borrado. Reinicia para nuevo QR.");
  setConnectionState({ status: "disconnected", qr_string: null, phone: null });
}
