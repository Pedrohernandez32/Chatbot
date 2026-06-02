import { Boom } from "@hapi/boom";
import makeWASocket, {
  Browsers,
  DisconnectReason,
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

const credsPath = path.join(authDir, "creds.json");

let socket: ReturnType<typeof makeWASocket> | null = null;
let retryCount = 0;

const loadOrCreateCreds = () => {
  if (fs.existsSync(credsPath)) {
    try {
      return JSON.parse(fs.readFileSync(credsPath, "utf-8"));
    } catch (e) {
      console.error("[Baileys] Error loading creds:", e);
    }
  }

  return {
    me: { id: "", name: "" },
    noiseKey: undefined,
    pairingEphemeralKeyPair: undefined,
    signalIdentities: [],
    signalKeyStore: {},
    accountSettings: undefined,
  };
};

const saveCreds = (creds: any) => {
  const state = { creds };
  fs.writeFileSync(credsPath, JSON.stringify(state, null, 2));
};

export async function initializeSocket() {
  console.log("[Baileys] Inicializando socket...");

  if (socket) {
    try {
      socket.end(undefined as any);
      await new Promise((r) => setTimeout(r, 500));
    } catch (e) {
      // ignore
    }
    socket = null;
  }

  try {
    const creds = loadOrCreateCreds();

    const sock = makeWASocket({
      browser: ["Linux", "5.0.4", "4.19.128-microsoft-standard"],
      auth: {
        creds: creds,
        keys: {
          get: () => undefined,
          set: () => {},
          del: () => {},
        },
      },
      logger,
      patchMessageBeforeSending: (message) => {
        const requiresPatch = !!(
          message.buttonsMessage
          || message.templateMessage
          || message.listMessage
        );
        if (requiresPatch) {
          message = {
            viewOnceMessage: {
              message: {
                messageContextInfo: {
                  deviceListMetadata: {},
                  deviceListMetadataVersion: 2,
                },
                ...message,
              },
            },
          };
        }
        return message;
      },
    }) as any;

    sock.ev.on("connection.update", async (update) => {
      const { connection, lastDisconnect, qr } = update;

      if (qr) {
        console.log("\n╔════════════════════════════════════════╗");
        console.log("║  📱 ESCANEA CON WHATSAPP 📱          ║");
        console.log("║  Abre WhatsApp > Más > Vincular      ║");
        console.log("╚════════════════════════════════════════╝\n");
        console.log(qr);
        console.log("\n");
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
        console.log("[Baileys] ✅ ¡Conectado! Listo para recibir mensajes.");
        const phone = sock.user?.id?.split(":")?.[0];
        setConnectionState({
          status: "connected",
          phone: phone || null,
          qr_string: null,
        });
        retryCount = 0;
      }

      if (connection === "close") {
        const reason = (lastDisconnect?.error as Boom)?.output?.statusCode;

        if (reason === DisconnectReason.loggedOut) {
          console.log("[Baileys] ❌ Sesión cerrada. Borra auth/ e intenta de nuevo.");
          if (fs.existsSync(credsPath)) {
            fs.unlinkSync(credsPath);
          }
          setConnectionState({ status: "disconnected" });
          retryCount = 0;
        } else if (reason === 440) {
          console.log("[Baileys] Code 440 - Dispositivo desvinculado");
          if (fs.existsSync(credsPath)) {
            fs.unlinkSync(credsPath);
          }
          retryCount = 0;
          console.log("[Baileys] Reintentando en 5 segundos...");
          setTimeout(() => initializeSocket(), 5000);
        } else {
          retryCount++;
          if (retryCount < 5) {
            const delay = 3000 + retryCount * 1000;
            console.log(`[Baileys] Reconectando (intento ${retryCount}/5) en ${delay}ms...`);
            setTimeout(() => initializeSocket(), delay);
          } else {
            console.log("[Baileys] Máximo de reintentos alcanzado. Manualmente reinicia el bot.");
            setConnectionState({ status: "disconnected" });
          }
        }
      }
    });

    sock.ev.on("creds.update", (creds) => {
      console.log("[Baileys] 💾 Actualizando credenciales...");
      saveCreds(creds);
    });

    socket = sock;
    return sock;
  } catch (error) {
    console.error("[Baileys] Error grave al inicializar socket:", error);
    setConnectionState({ status: "disconnected" });
    retryCount++;
    if (retryCount < 5) {
      setTimeout(() => initializeSocket(), 5000);
    }
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
      // ignore
    }
    socket = null;
    setConnectionState({ status: "disconnected" });
  }
}

export function clearAuth() {
  if (fs.existsSync(credsPath)) {
    fs.unlinkSync(credsPath);
  }
  console.log("[Baileys] Credenciales eliminadas. Reinicia el bot.");
  setConnectionState({ status: "disconnected", qr_string: null, phone: null });
}
