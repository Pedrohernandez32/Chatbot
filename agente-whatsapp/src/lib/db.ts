import Database from "better-sqlite3";
import path from "path";
import fs from "fs";
import type BetterSqlite3 from "better-sqlite3";

const dataDir = path.resolve(process.cwd(), "data");
if (!fs.existsSync(dataDir)) {
  fs.mkdirSync(dataDir, { recursive: true });
}

const dbPath = path.join(dataDir, "messages.db");
const db: BetterSqlite3.Database = new Database(dbPath);

// Enable WAL mode for concurrency
db.pragma("journal_mode = WAL");
db.pragma("foreign_keys = ON");

// Initialize schema
const initSchema = () => {
  db.exec(`
    CREATE TABLE IF NOT EXISTS conversations (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      phone TEXT UNIQUE NOT NULL,
      name TEXT,
      mode TEXT CHECK(mode IN ('AI','HUMAN')) NOT NULL DEFAULT 'AI',
      last_message_at INTEGER,
      created_at INTEGER NOT NULL DEFAULT (unixepoch())
    );

    CREATE TABLE IF NOT EXISTS messages (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      conversation_id INTEGER NOT NULL REFERENCES conversations(id),
      role TEXT CHECK(role IN ('user','assistant','human')) NOT NULL,
      content TEXT NOT NULL,
      created_at INTEGER NOT NULL DEFAULT (unixepoch())
    );

    CREATE INDEX IF NOT EXISTS idx_messages_conv
      ON messages(conversation_id, created_at);

    CREATE TABLE IF NOT EXISTS connection_state (
      id INTEGER PRIMARY KEY CHECK (id = 1),
      status TEXT CHECK(status IN ('disconnected','qr','connecting','connected'))
        NOT NULL DEFAULT 'disconnected',
      qr_string TEXT,
      phone TEXT,
      updated_at INTEGER NOT NULL DEFAULT (unixepoch())
    );

    INSERT OR IGNORE INTO connection_state (id, status) VALUES (1, 'disconnected');

    CREATE TABLE IF NOT EXISTS outbox (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      conversation_id INTEGER NOT NULL,
      phone TEXT NOT NULL,
      content TEXT NOT NULL,
      sent INTEGER NOT NULL DEFAULT 0,
      created_at INTEGER NOT NULL DEFAULT (unixepoch())
    );

    CREATE INDEX IF NOT EXISTS idx_outbox_pending
      ON outbox(sent, created_at);
  `);
};

initSchema();

// Types
export interface Conversation {
  id: number;
  phone: string;
  name: string | null;
  mode: "AI" | "HUMAN";
  last_message_at: number | null;
  created_at: number;
}

export interface Message {
  id: number;
  conversation_id: number;
  role: "user" | "assistant" | "human";
  content: string;
  created_at: number;
}

export interface ConnectionState {
  id: 1;
  status: "disconnected" | "qr" | "connecting" | "connected";
  qr_string: string | null;
  phone: string | null;
  updated_at: number;
}

// Helpers
export const getOrCreateConversation = (
  phone: string,
  name?: string
): Conversation => {
  const existing = db
    .prepare("SELECT * FROM conversations WHERE phone = ?")
    .get(phone) as Conversation | undefined;

  if (existing) return existing;

  db.prepare(
    "INSERT INTO conversations (phone, name, created_at) VALUES (?, ?, unixepoch())"
  ).run(phone, name || null);

  return db
    .prepare("SELECT * FROM conversations WHERE phone = ?")
    .get(phone) as Conversation;
};

export const getConversationById = (id: number): Conversation | null => {
  return (
    (db
      .prepare("SELECT * FROM conversations WHERE id = ?")
      .get(id) as Conversation | undefined) || null
  );
};

export const insertMessage = (
  conversationId: number,
  role: "user" | "assistant" | "human",
  content: string
): Message => {
  const insert = db.prepare(
    "INSERT INTO messages (conversation_id, role, content, created_at) VALUES (?, ?, ?, unixepoch())"
  );
  const updateConvo = db.prepare(
    "UPDATE conversations SET last_message_at = unixepoch() WHERE id = ?"
  );

  const transaction = db.transaction(() => {
    insert.run(conversationId, role, content);
    updateConvo.run(conversationId);
  });

  transaction();

  return db
    .prepare("SELECT * FROM messages WHERE conversation_id = ? ORDER BY id DESC LIMIT 1")
    .get(conversationId) as Message;
};

export const getMessages = (conversationId: number, limit = 50): Message[] => {
  return db
    .prepare(
      "SELECT * FROM messages WHERE conversation_id = ? ORDER BY created_at DESC LIMIT ?"
    )
    .all(conversationId, limit) as Message[];
};

export const getRecentHistory = (
  conversationId: number,
  limit = 20
): Message[] => {
  const messages = db
    .prepare(
      "SELECT * FROM messages WHERE conversation_id = ? ORDER BY created_at DESC LIMIT ?"
    )
    .all(conversationId, limit) as Message[];
  return messages.reverse();
};

export const setMode = (conversationId: number, mode: "AI" | "HUMAN") => {
  db.prepare("UPDATE conversations SET mode = ? WHERE id = ?").run(
    mode,
    conversationId
  );
};

export const listConversations = (): (Conversation & { last_message_preview: string | null })[] => {
  return db
    .prepare(
      `SELECT c.*,
        (SELECT content FROM messages WHERE conversation_id = c.id ORDER BY created_at DESC LIMIT 1) as last_message_preview
      FROM conversations c
      ORDER BY c.last_message_at DESC NULLS LAST`
    )
    .all() as (Conversation & { last_message_preview: string | null })[];
};

export const getConnectionState = (): ConnectionState => {
  return db
    .prepare("SELECT * FROM connection_state WHERE id = 1")
    .get() as ConnectionState;
};

export const setConnectionState = (
  updates: Partial<Omit<ConnectionState, "id">>
) => {
  const current = getConnectionState();
  const newState = {
    status: updates.status ?? current.status,
    qr_string: updates.qr_string === null ? null : (updates.qr_string ?? current.qr_string),
    phone: updates.phone === null ? null : (updates.phone ?? current.phone),
    updated_at: Math.floor(Date.now() / 1000),
  };

  db.prepare(
    "UPDATE connection_state SET status = ?, qr_string = ?, phone = ?, updated_at = ? WHERE id = 1"
  ).run(newState.status, newState.qr_string, newState.phone, newState.updated_at);
};

export const enqueueOutbox = (
  conversationId: number,
  phone: string,
  content: string
) => {
  db.prepare(
    "INSERT INTO outbox (conversation_id, phone, content, created_at) VALUES (?, ?, ?, unixepoch())"
  ).run(conversationId, phone, content);
};

export const getPendingOutbox = (limit = 20) => {
  return db
    .prepare("SELECT * FROM outbox WHERE sent = 0 ORDER BY created_at ASC LIMIT ?")
    .all(limit) as Array<{
      id: number;
      conversation_id: number;
      phone: string;
      content: string;
      sent: number;
      created_at: number;
    }>;
};

export const markOutboxSent = (id: number) => {
  db.prepare("UPDATE outbox SET sent = 1 WHERE id = ?").run(id);
};

export const deleteConversation = (id: number) => {
  const transaction = db.transaction(() => {
    db.prepare("DELETE FROM messages WHERE conversation_id = ?").run(id);
    db.prepare("DELETE FROM outbox WHERE sent = 0 AND conversation_id = ?").run(id);
    db.prepare("DELETE FROM conversations WHERE id = ?").run(id);
  });

  transaction();
};

export default db;
