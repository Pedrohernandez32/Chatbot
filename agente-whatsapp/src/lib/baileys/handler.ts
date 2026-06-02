import { proto } from "@whiskeysockets/baileys";
import {
  getOrCreateConversation,
  insertMessage,
  getRecentHistory,
  enqueueOutbox,
  getConversationById,
} from "../db";
import { callOpenRouter } from "../openrouter";
import { getSocket } from "./client";

export async function handleIncomingMessage(
  message: proto.IWebMessageInfo
) {
  try {
    if (!message.key?.remoteJid || !message.message) return;

    const phoneNumber = message.key.remoteJid.split("@")?.[0];
    const pushName = message.pushName;

    // Get text content
    let textContent = "";
    if (message.message.conversation) {
      textContent = message.message.conversation;
    } else if (message.message.extendedTextMessage?.text) {
      textContent = message.message.extendedTextMessage.text;
    }

    if (!textContent) return;

    console.log(`[Handler] Message from ${phoneNumber}: ${textContent}`);

    // Get or create conversation
    const convo = getOrCreateConversation(phoneNumber, pushName);

    // Store user message
    insertMessage(convo.id, "user", textContent);

    // Check mode and generate response
    if (convo.mode === "HUMAN") {
      console.log(`[Handler] Conversation ${convo.id} in HUMAN mode - escalating`);
      // In human mode, just acknowledge
      enqueueOutbox(
        convo.id,
        phoneNumber,
        "👤 Un asesor humano te responderá pronto. Gracias por tu paciencia."
      );
      return;
    }

    // AI mode - get history and call LLM
    const history = getRecentHistory(convo.id, 10);
    const messages = history.map((msg) => ({
      role: msg.role === "assistant" ? "assistant" as const : "user" as const,
      content: msg.content,
    }));

    // Add current message if not already there (recent history may not include it immediately)
    if (!messages.length || messages[messages.length - 1].content !== textContent) {
      messages.push({ role: "user", content: textContent });
    }

    try {
      const response = await callOpenRouter(messages);
      insertMessage(convo.id, "assistant", response);
      enqueueOutbox(convo.id, phoneNumber, response);
      console.log(`[Handler] Response queued for ${phoneNumber}`);
    } catch (error) {
      console.error(`[Handler] LLM error: ${error}`);
      const errorMsg =
        "Lo siento, hubo un problema procesando tu mensaje. Por favor intenta de nuevo.";
      insertMessage(convo.id, "assistant", errorMsg);
      enqueueOutbox(convo.id, phoneNumber, errorMsg);
    }
  } catch (error) {
    console.error(`[Handler] Error in handleIncomingMessage: ${error}`);
  }
}

export async function sendOutboxMessages() {
  try {
    const { getPendingOutbox, markOutboxSent } = await import("../db");
    const pending = getPendingOutbox(20);

    if (!pending.length) return;

    const sock = getSocket();
    if (!sock) {
      console.log("[Outbox] Socket not ready");
      return;
    }

    for (const msg of pending) {
      try {
        const jid = `${msg.phone}@s.whatsapp.net`;
        await sock.sendMessage(jid, {
          text: msg.content,
        });
        markOutboxSent(msg.id);
        console.log(`[Outbox] Sent message ${msg.id} to ${msg.phone}`);
      } catch (error) {
        console.error(`[Outbox] Failed to send ${msg.id}: ${error}`);
      }
    }
  } catch (error) {
    console.error(`[Outbox] Error in sendOutboxMessages: ${error}`);
  }
}

export function attachHandlers(socket: ReturnType<typeof getSocket>) {
  if (!socket) return;

  socket.ev.on("messages.upsert", async (m) => {
    console.log("[Handler] Messages upsert event");
    for (const msg of m.messages) {
      if (!msg.key.fromMe) {
        await handleIncomingMessage(msg);
      }
    }
  });

  // Send outbox messages periodically
  setInterval(sendOutboxMessages, 5000);
}
