import { Boom } from "@hapi/boom";
import makeWASocket, {
  AuthenticationCreds,
  AuthenticationState,
  Browsers,
  BufferJSON,
  DisconnectReason,
  isJidBroadcast,
  isJidStatusBroadcast,
  makeCacheableSignalKeyStore,
  makeInMemoryStore,
  proto,
  useMultiFileAuthState,
} from "@whiskeysockets/baileys";
import fs from "fs";
import path from "path";
import pino from "pino";
import { setConnectionState } from "../db";

const logger = pino({ level: "silent" });

const authDir = path.resolve(process.cwd(), "auth");

let socket: ReturnType<typeof makeWASocket> | null = null;
let retryCount = 0;
let connectionAttempts = 0;

export async function initializeSocket() {
  connectionAttempts++;
  console.log(`[Baileys] 🔄 Intento ${connectionAttempts} de conexión a WhatsApp...`);

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
    // Usar el sistema de autenticación multi-archivo de Baileys
    const { state, saveCreds } = await useMultiFileAuthState(authDir);

    console.log("[Baileys] Usando sistema de autenticación multi-archivo");

    const sock = makeWASocket({
      auth: state,
      logger,
      browser: Browsers.ubuntu("Desktop"),
      generateHighQualityLinkPreview: false,
      shouldSyncHistoryMessage: () => false,
      markOnlineOnConnect: false,
      defaultQueryTimeoutMs: 0,
      retryRequestDelayMs: 100,
      maxMsToWaitForConnection: 30000,
      emitOwnEventsOnly: false,
      linkPreviewImageThumbnailWidth: 192,
      transactionTimeout: 40000,
      keepAliveIntervalMs: 30000,
      qrTimeout: 60000,
    });

    // Guardar credenciales cada vez que se actualicen
    sock.ev.on("creds.update", saveCreds);

    // Manejo de conexión
    sock.ev.on("connection.update", async (update) => {
      const { connection, lastDisconnect, qr, isNewLogin } = update;

      console.log("[Baileys] Estado:", { connection, hasQR: !!qr, isNewLogin });

      // QR Code
      if (qr) {
        console.log("\n╔═══════════════════════════════════════════════════╗");
        console.log("║        📱 ESCANEA CON WHATSAPP - QR CODE 📱       ║");
        console.log("║  WhatsApp > Más opciones > Vincular un dispositivo ║");
        console.log("╚═══════════════════════════════════════════════════╝\n");
        console.log(qr);
        console.log("\n");

        connectionAttempts = 0;
        retryCount = 0;
        setConnectionState({
          status: "qr",
          qr_string: qr,
        });
      }

      // Conectando
      if (connection === "connecting") {
        console.log("[Baileys] ⏳ Conectando a WebSocket de WhatsApp...");
        setConnectionState({ status: "connecting" });
      }

      // Conectado
      if (connection === "open") {
        console.log("[Baileys] ✅ ¡CONECTADO EXITOSAMENTE!");
        console.log(`[Baileys] Tu número WhatsApp: ${sock.user?.id}`);

        connectionAttempts = 0;
        retryCount = 0;

        setConnectionState({
          status: "connected",
          phone: sock.user?.id?.split(":")?.[0] || null,
          qr_string: null,
        });

        // Escuchar mensajes entrantes
        sock.ev.on("messages.upsert", async (m) => {
          for (const msg of m.messages) {
            // Solo procesar mensajes que no sean nuestros
            if (!msg.key.fromMe) {
              const remoteJid = msg.key.remoteJid;

              // Ignorar broadcasts y estados
              if (isJidBroadcast(remoteJid!) || isJidStatusBroadcast(remoteJid!)) {
                continue;
              }

              const text = msg.message?.conversation ||
                msg.message?.extendedTextMessage?.text ||
                "";

              if (text) {
                const from = remoteJid?.split("@")?.[0];
                console.log(`[Baileys] 📨 Mensaje de ${from}: ${text.substring(0, 50)}`);

                // Importar y usar handler
                try {
                  const { handleIncomingMessage } = await import("./handler");
                  await handleIncomingMessage(msg);
                } catch (error) {
                  console.error("[Baileys] Error procesando mensaje:", error);
                }
              }
            }
          }
        });
      }

      // Desconectado
      if (connection === "close") {
        const reason = (lastDisconnect?.error as Boom)?.output?.statusCode;
        console.log(`[Baileys] ❌ Desconectado${reason ? ` (código: ${reason})` : ""}`);

        if (reason === DisconnectReason.loggedOut) {
          console.log("[Baileys] Sesión finalizada por el usuario");
          fs.rmSync(authDir, { recursive: true, force: true });
          setConnectionState({ status: "disconnected" });
        } else {
          // Reintentar reconexión
          retryCount++;
          if (retryCount < 30) {
            const delay = Math.min(2000 + retryCount * 1000, 60000);
            console.log(
              `[Baileys] 🔄 Reconectando en ${(delay / 1000).toFixed(0)}s (intento ${retryCount}/30)...`
            );
            await new Promise((resolve) => setTimeout(resolve, delay));
            await initializeSocket();
          } else {
            console.log("[Baileys] ❌ Máximo de intentos de reconexión alcanzado");
            setConnectionState({ status: "disconnected" });
          }
        }
      }
    });

    socket = sock;
    console.log("[Baileys] ✓ Socket creado correctamente");
    return sock;
  } catch (error) {
    console.error("[Baileys] Error fatal:", error);
    setConnectionState({ status: "disconnected" });

    connectionAttempts++;
    if (connectionAttempts < 20) {
      const delay = 5000 + Math.random() * 5000;
      console.log(
        `[Baileys] Reintentando en ${(delay / 1000).toFixed(0)}s (${connectionAttempts}/20)...`
      );
      await new Promise((resolve) => setTimeout(resolve, delay));
      await initializeSocket();
    } else {
      console.log("[Baileys] No se pudo conectar después de 20 intentos");
    }
  }
}

export function getSocket() {
  return socket;
}

export async function disconnect() {
  if (socket) {
    try {
      socket.end();
    } catch (e) {
      // ignore
    }
    socket = null;
  }
  setConnectionState({ status: "disconnected" });
  console.log("[Baileys] Desconectado");
}

export async function clearAuth() {
  try {
    if (fs.existsSync(authDir)) {
      fs.rmSync(authDir, { recursive: true, force: true });
    }
  } catch (e) {
    // ignore
  }
  console.log("[Baileys] Credenciales eliminadas. Reinicia para nuevo QR.");
  setConnectionState({ status: "disconnected", qr_string: null, phone: null });
}
