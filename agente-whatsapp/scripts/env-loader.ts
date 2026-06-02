import fs from "fs";
import path from "path";

const envPath = path.resolve(process.cwd(), ".env.local");

if (fs.existsSync(envPath)) {
  const envContent = fs.readFileSync(envPath, "utf-8");
  const lines = envContent.split("\n");

  for (const line of lines) {
    const trimmed = line.trim();
    if (!trimmed || trimmed.startsWith("#")) continue;

    const [key, ...valueParts] = trimmed.split("=");
    const value = valueParts.join("=").trim();

    if (key && value && !process.env[key]) {
      process.env[key] = value;
    }
  }

  console.log("[env-loader] Loaded .env.local");
} else {
  console.log("[env-loader] .env.local not found, using existing env vars");
}
