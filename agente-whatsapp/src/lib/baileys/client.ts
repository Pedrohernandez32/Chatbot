import { Boom } from "@hapi/boom";
import makeWASocket, {
  Browsers,
  DisconnectReason,
  fetchLatestBaileysVersion,
  proto,
} from "@whiskeysockets/baileys";
import fs from "fs";
import path from "path";
import pino from "pino";
import { setConnectionState } from "../db";

const logger = pino({
  level: "debug",
  transport: {
    target: "pino-pretty",
    options: {
      colorize: false,
    },
  },
});

const authDir = path.resolve(process.cwd(), "auth");
if (!fs.existsSync(authDir)) {
  fs.mkdirSync(authDir, { recursive: true });
}

const credsPath = path.join(authDir, "creds.json");
const keysPath = path.join(authDir, "keys.json");

let socket: ReturnType<typeof makeWASocket> | null = null;
let retryCount = 0;

const loadCreds = () => {
  if (fs.existsSync(credsPath)) {
    try {
      return JSON.parse(fs.readFileSync(credsPath, "utf-8"));
    } catch {
      return null;
    }
  }
  return null;
};

const saveCreds = (creds: any) => {
  fs.writeFileSync(credsPath, JSON.stringify(creds, null, 2));
};

const loadKeys = () => {
  if (fs.existsSync(keysPath)) {
    try {
      const data = JSON.parse(fs.readFileSync(keysPath, "utf-8"));
      return new Map(data);
    } catch {
      return new Map();
    }
  }
  return new Map();
};

const saveKeys = (keys: Map<string, any>) => {
  fs.writeFileSync(keysPath, JSON.stringify(Array.from(keys.entries()), null, 2));
};

export async function initializeSocket() {
  console.log("[Baileys] 🔄 Intentando conectar a WhatsApp...");

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
    const creds = loadCreds();
    const keys = loadKeys();

    console.log("[Baileys] Usando credenciales:", creds ? "existentes" : "nuevas");

    const version = await fetchLatestBaileysVersion();
    console.log("[Baileys] Versión:", version);

    const sock = makeWASocket({
      version,
      auth: {
        creds: creds || {
          me: { id: "" },
          noiseKey: null,
          pairingEphemeralKeyPair: null,
          signalIdentities: [],
          signalKeyStore: {},
          registrationId: 0,
          advSecretKey: "",
          processedHistoryMessages: [],
          nextPreKeyId: 1,
          firstUnuploadedPreKeyId: 1,
          accountSyncCounter: 0,
          accountSettings: { unarchiveChats: false },
          deviceName: "WhatsApp Web",
          phoneNumber: "",
          identityId: { timestamp: 0 },
          backup: null,
          platform: "web",
        },
        keys: keys,
      },
      browser: Browsers.chrome("120.0"),
      logger,
      shouldIgnoreJid: (jid: string) => {
        return jid.includes("broadcast") || jid.includes("status");
      },
      retryRequestDelayMs: 100,
      maxMsToWaitForConnection: 10000,
      handshakeTimeout: 20000,
      syncFullHistory: false,
      markOnlineOnConnect: true,
    });

    sock.ev.on("connection.update", async (update) => {
      const { connection, lastDisconnect, qr, receivedPendingNotifications } =
        update;

      console.log("[Baileys] Estado:", {
        connection,
        hasQR: !!qr,
        receivedPending: receivedPendingNotifications,
      });

      if (qr) {
        console.log("\n");
        console.log("╔═══════════════════════════════════════════════╗");
        console.log("║     📱 ESCANEA ESTE CÓDIGO CON WHATSAPP 📱   ║");
        console.log("║    Abre WhatsApp > Más > Vincular dispositivo ║");
        console.log("╚═══════════════════════════════════════════════╝");
        console.log(qr);
        console.log("╔═══════════════════════════════════════════════╗");
        console.log("\n");

        retryCount = 0;
        setConnectionState({
          status: "qr",
          qr_string: qr,
        });
      }

      if (connection === "connecting") {
        console.log("[Baileys] ⏳ Conectando a WhatsApp Web...");
        setConnectionState({ status: "connecting" });
      }

      if (connection === "open") {
        console.log("[Baileys] ✅ ¡CONECTADO!");
        console.log(`[Baileys] ID: ${sock.user?.id}`);
        const phone = sock.user?.id?.split(":")?.[0];

        retryCount = 0;
        setConnectionState({
          status: "connected",
          phone: phone || null,
          qr_string: null,
        });

        // Escuchar mensajes
        sock.ev.on("messages.upsert", async (m) => {
          console.log("[Baileys] 📨 Nuevo mensaje recibido");
          for (const msg of m.messages) {
            if (!msg.key.fromMe && msg.message?.conversation) {
              const from = msg.key.remoteJid?.split("@")?.[0];
              const text = msg.message.conversation;
              console.log(`[Baileys] De: ${from}, Mensaje: ${text}`);

              // Importar handlers aquí para evitar circular dependencies
              const { handleIncomingMessage } = await import("./handler");
              await handleIncomingMessage(msg);
            }
          }
        });
      }

      if (connection === "close") {
        const reason = (lastDisconnect?.error as Boom)?.output?.statusCode;
        console.log(`[Baileys] ❌ Desconectado. Código: ${reason}`);

        if (reason === DisconnectReason.loggedOut) {
          console.log("[Baileys] Sesión cerrada por el usuario");
          if (fs.existsSync(credsPath)) {
            fs.unlinkSync(credsPath);
          }
          if (fs.existsSync(keysPath)) {
            fs.unlinkSync(keysPath);
          }
          setConnectionState({ status: "disconnected" });
        } else if (reason === 440 || reason === 401) {
          console.log("[Baileys] Dispositivo desvinculado. Limpiando auth...");
          if (fs.existsSync(credsPath)) {
            fs.unlinkSync(credsPath);
          }
          if (fs.existsSync(keysPath)) {
            fs.unlinkSync(keysPath);
          }
          retryCount = 0;
          setTimeout(() => initializeSocket(), 3000);
        } else if (reason === undefined) {
          retryCount++;
          if (retryCount < 15) {
            const delay = 2000 + retryCount * 1000;
            console.log(
              `[Baileys] Reconectando en ${delay}ms... (intento ${retryCount}/15)`
            );
            setTimeout(() => initializeSocket(), delay);
          } else {
            console.log("[Baileys] Máximo de intentos. Reinicia el bot.");
            setConnectionState({ status: "disconnected" });
          }
        } else {
          retryCount++;
          if (retryCount < 10) {
            setTimeout(() => initializeSocket(), 3000);
          }
        }
      }
    });

    sock.ev.on("creds.update", (creds) => {
      console.log("[Baileys] 💾 Guardando credenciales...");
      saveCreds(creds);
    });

    sock.ev.on("keys.update", (keys: any) => {
      console.log("[Baileys] 🔑 Guardando claves...");
      const keysArray = Object.entries(keys);
      for (const [key, value] of keysArray) {
        if (value !== null) {
          const map = loadKeys();
          map.set(key, value);
          saveKeys(map);
        }
      }
    });

    socket = sock;
    console.log("[Baileys] ✓ Socket inicializado correctamente");
    return sock;
  } catch (error) {
    console.error("[Baileys] ❌ Error fatal:", error);
    setConnectionState({ status: "disconnected" });

    retryCount++;
    if (retryCount < 10) {
      const delay = 5000 + Math.random() * 5000;
      console.log(
        `[Baileys] Reintentando en ${Math.round(delay)}ms... (${retryCount}/10)`
      );
      setTimeout(() => initializeSocket(), delay);
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
  if (fs.existsSync(credsPath)) {
    fs.unlinkSync(credsPath);
  }
  if (fs.existsSync(keysPath)) {
    fs.unlinkSync(keysPath);
  }
  console.log("[Baileys] Auth borrado. Reinicia el bot para nuevo QR.");
  setConnectionState({ status: "disconnected", qr_string: null, phone: null });
}
