// CRITICAL: env-loader MUST be the first import
import "./env-loader";

import { initializeSocket, getSocket } from "../src/lib/baileys/client";
import { attachHandlers } from "../src/lib/baileys/handler";

async function main() {
  console.log("[Bot] Starting WhatsApp agent...");
  console.log(`[Bot] Environment: ${process.env.NODE_ENV || "development"}`);
  console.log(`[Bot] OpenRouter Model: ${process.env.OPENROUTER_MODEL || "openai/gpt-4o-mini"}`);

  try {
    const socket = await initializeSocket();
    console.log("[Bot] Socket initialized");

    // Wait 15 seconds before attaching handlers to allow for proper state setup
    // This helps with code 440 recovery
    await new Promise((resolve) => setTimeout(resolve, 15000));

    attachHandlers(socket);
    console.log("[Bot] Handlers attached");

    // Keep the process alive
    process.on("SIGINT", () => {
      console.log("[Bot] Shutting down gracefully...");
      process.exit(0);
    });

    console.log("[Bot] Waiting for connections...");
  } catch (error) {
    console.error("[Bot] Fatal error:", error);
    process.exit(1);
  }
}

main();
