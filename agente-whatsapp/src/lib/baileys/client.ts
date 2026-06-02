import { Client, LocalSession } from "whatsapp-web.js";
import qrcode from "qrcode-terminal";
import path from "path";
import { setConnectionState } from "../db";

const sessionsPath = path.resolve(process.cwd(), "sessions");

let client: Client | null = null;
let reconnectAttempts = 0;

export async function initializeSocket() {
  console.log("[WhatsApp] 🔄 Inicializando cliente WhatsApp...");

  if (client) {
    try {
      await client.destroy();
    } catch (e) {
      // ignore
    }
    client = null;
  }

  try {
    // Crear cliente con sesión persistente
    client = new Client({
      session: new LocalSession({
        dir: sessionsPath,
      }),
      puppeteer: {
        headless: true,
        args: [
          "--no-sandbox",
          "--disable-setuid-sandbox",
          "--disable-dev-shm-usage",
          "--disable-gpu",
          "--single-process=false",
        ],
      },
      ffmpeg: {
        path: "ffmpeg",
      },
      restartOnCrash: true,
      qrMaxRetries: 5,
    });

    // QR Code
    client.on("qr", (qr) => {
      console.log("\n╔════════════════════════════════════════════════╗");
      console.log("║     📱 ESCANEA CON WHATSAPP - QR CODE 📱      ║");
      console.log("║ Abre WhatsApp > Más > Vincular un dispositivo  ║");
      console.log("╚════════════════════════════════════════════════╝\n");

      // Mostrar QR en terminal
      qrcode.generate(qr, { small: true });

      setConnectionState({
        status: "qr",
        qr_string: qr,
      });

      reconnectAttempts = 0;
    });

    // Listo
    client.on("ready", () => {
      console.log("[WhatsApp] ✅ ¡CLIENTE LISTO!");
      console.log(`[WhatsApp] Conectado como: ${client?.info.pushname}`);

      setConnectionState({
        status: "connected",
        phone: client?.info?.me?.user || null,
        qr_string: null,
      });

      reconnectAttempts = 0;
    });

    // Conectando
    client.on("loading_screen", (percent, message) => {
      console.log(`[WhatsApp] ⏳ Cargando ${percent}% - ${message}`);
      setConnectionState({ status: "connecting" });
    });

    // Autenticado
    client.on("authenticated", (session) => {
      console.log("[WhatsApp] ✓ Autenticado");
    });

    // Mensajes entrantes
    client.on("message", async (msg) => {
      console.log(`[WhatsApp] 📨 Mensaje de ${msg.from}: ${msg.body.substring(0, 50)}`);

      try {
        const { handleIncomingMessage } = await import("./handler");

        // Convertir a formato compatible
        const protoMsg = {
          key: {
            fromMe: msg.fromMe,
            remoteJid: msg.from,
          },
          message: {
            conversation: msg.body,
          },
          pushName: msg.notifyName,
        };

        await handleIncomingMessage(protoMsg as any);
      } catch (error) {
        console.error("[WhatsApp] Error procesando mensaje:", error);
      }
    });

    // Desconexión
    client.on("disconnected", (reason) => {
      console.log(`[WhatsApp] ❌ Desconectado: ${reason}`);
      setConnectionState({ status: "disconnected" });

      // Reconectar
      reconnectAttempts++;
      if (reconnectAttempts < 10) {
        const delay = 5000 + reconnectAttempts * 2000;
        console.log(
          `[WhatsApp] 🔄 Reconectando en ${(delay / 1000).toFixed(0)}s (${reconnectAttempts}/10)...`
        );
        setTimeout(() => {
          initializeSocket();
        }, delay);
      } else {
        console.log("[WhatsApp] ❌ No se pudo reconectar después de 10 intentos");
      }
    });

    // Error
    client.on("error", (error) => {
      console.error("[WhatsApp] Error:", error);
    });

    // Inicializar
    console.log("[WhatsApp] Iniciando cliente...");
    await client.initialize();

    console.log("[WhatsApp] ✓ Cliente inicializado");
    return client;
  } catch (error) {
    console.error("[WhatsApp] Error fatal:", error);
    setConnectionState({ status: "disconnected" });

    reconnectAttempts++;
    if (reconnectAttempts < 10) {
      const delay = 5000 + reconnectAttempts * 1000;
      console.log(
        `[WhatsApp] Reintentando en ${(delay / 1000).toFixed(0)}s (${reconnectAttempts}/10)...`
      );
      setTimeout(() => {
        initializeSocket();
      }, delay);
    }
  }
}

export function getSocket() {
  return client;
}

export async function disconnect() {
  if (client) {
    try {
      await client.destroy();
    } catch (e) {
      // ignore
    }
    client = null;
  }
  setConnectionState({ status: "disconnected" });
  console.log("[WhatsApp] Desconectado");
}

export async function clearAuth() {
  try {
    const fs = await import("fs");
    const path = await import("path");
    const sessionsPath = path.resolve(process.cwd(), "sessions");
    if (fs.existsSync(sessionsPath)) {
      fs.rmSync(sessionsPath, { recursive: true, force: true });
    }
  } catch (e) {
    // ignore
  }
  console.log("[WhatsApp] Sesiones eliminadas. Reinicia para nuevo QR.");
  setConnectionState({ status: "disconnected", qr_string: null, phone: null });
}
