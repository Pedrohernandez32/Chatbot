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

const credsPath = path.join(authDir, "creds.json");
const keysPath = path.join(authDir, "keys.json");

let socket: ReturnType<typeof makeWASocket> | null = null;
let retryCount = 0;
let qrShown = false;

const loadCreds = () => {
  try {
    if (fs.existsSync(credsPath)) {
      return JSON.parse(fs.readFileSync(credsPath, "utf-8"));
    }
  } catch (e) {
    console.log("[Baileys] No se pudieron cargar credenciales previas");
  }
  return null;
};

const saveCreds = (creds: any) => {
  fs.writeFileSync(credsPath, JSON.stringify(creds, null, 2));
};

const loadKeys = () => {
  try {
    if (fs.existsSync(keysPath)) {
      const data = JSON.parse(fs.readFileSync(keysPath, "utf-8"));
      return new Map(data);
    }
  } catch {
    // ignore
  }
  return new Map();
};

const saveKeys = (keys: Map<string, any>) => {
  fs.writeFileSync(keysPath, JSON.stringify(Array.from(keys.entries())));
};

export async function initializeSocket() {
  console.log("[Baileys] 🔄 Conectando a WhatsApp Web...");

  if (socket) {
    try {
      socket.ws?.close?.();
      socket.end?.();
    } catch (e) {
      // ignore
    }
    socket = null;
  }

  try {
    const creds = loadCreds();
    const keys = loadKeys();

    console.log("[Baileys] Usando", creds ? "credenciales guardadas" : "NUEVO QR");

    const sock = makeWASocket({
      version: await fetchLatestBaileysVersion(),
      auth: {
        creds:
          creds ||
          {
            me: { id: "" },
            noiseKey: null,
            signalIdentities: [],
            signalKeyStore: {},
            registrationId: 0,
            advSecretKey: "",
            processedHistoryMessages: [],
            nextPreKeyId: 1,
            firstUnuploadedPreKeyId: 1,
            accountSyncCounter: 0,
            accountSettings: { unarchiveChats: false },
            deviceName: "WhatsApp",
            phoneNumber: "",
            platform: "web",
          },
        keys,
      },
      browser: Browsers.ubuntu("Desktop"),
      logger,
      connectTimeoutMs: 60000,
      defaultQueryTimeoutMs: 0,
      keepAliveIntervalMs: 30000,
      qrTimeout: 60000,
      emitOwnEvents: false,
      generateHighQualityLinkPreview: false,
    });

    // QR
    sock.ev.on("connection.update", (update) => {
      const { connection, lastDisconnect, qr } = update;

      if (qr && !qrShown) {
        qrShown = true;
        console.log("\n");
        console.log("╔════════════════════════════════════════╗");
        console.log("║  📱 ESCANEA ESTE QR CON WHATSAPP 📱   ║");
        console.log("║ Más opciones > Vincular un dispositivo ║");
        console.log("╚════════════════════════════════════════╝\n");
        console.log(qr);
        console.log("\n");
        retryCount = 0;
        setConnectionState({ status: "qr", qr_string: qr });
      }

      if (connection === "connecting") {
        console.log("[Baileys] ⏳ Conectando...");
        setConnectionState({ status: "connecting" });
      }

      if (connection === "open") {
        console.log("[Baileys] ✅ CONECTADO!");
        console.log(`[Baileys] Tu número: ${sock.user?.id}`);
        qrShown = false;
        retryCount = 0;
        setConnectionState({
          status: "connected",
          phone: sock.user?.id?.split(":")?.[0] || null,
          qr_string: null,
        });
      }

      if (connection === "close") {
        const reason = (lastDisconnect?.error as Boom)?.output?.statusCode;
        console.log(
          `[Baileys] ❌ Desconectado${reason ? ` (${reason})` : ""}`
        );

        if (reason === DisconnectReason.loggedOut) {
          console.log("[Baileys] Sesión cerrada manualmente");
          fs.rmSync(authDir, { recursive: true, force: true });
          setConnectionState({ status: "disconnected" });
        } else {
          retryCount++;
          if (retryCount <= 20) {
            const delay = 2000 + retryCount * 500;
            console.log(`[Baileys] Reintentando en ${delay}ms (${retryCount}/20)`);
            setTimeout(() => initializeSocket(), delay);
          } else {
            console.log("[Baileys] Máximo de intentos. Reinicia el bot.");
            setConnectionState({ status: "disconnected" });
          }
        }
      }
    });

    sock.ev.on("creds.update", saveCreds);
    sock.ev.on("keys.update", (keys) => {
      const current = loadKeys();
      for (const [key, val] of Object.entries(keys)) {
        if (val) current.set(key, val);
      }
      saveKeys(current);
    });

    socket = sock;
    console.log("[Baileys] ✓ Socket creado - aguardando conexión WebSocket...");

    // Dar tiempo para que se conecte el WebSocket
    await new Promise(resolve => setTimeout(resolve, 2000));

    return sock;
  } catch (error) {
    console.error("[Baileys] Error:", error);
    setConnectionState({ status: "disconnected" });
    retryCount++;
    if (retryCount <= 20) {
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
      socket.end?.();
    } catch (e) {
      // ignore
    }
    socket = null;
  }
  setConnectionState({ status: "disconnected" });
}

export function clearAuth() {
  try {
    fs.rmSync(authDir, { recursive: true, force: true });
  } catch {
    // ignore
  }
  console.log("[Baileys] Auth borrado. Reinicia para nuevo QR.");
  setConnectionState({ status: "disconnected", qr_string: null, phone: null });
}
