#!/usr/bin/env node
const fs = require("fs");
const path = require("path");

const ROLE_TITLE_OVERRIDES = {
  qa: "QA",
};

const PROVIDER_TITLE_OVERRIDES = {
  claude: "Claude",
  codex: "Codex",
  gemini: "Gemini",
};

const titleize = (name, overrides) => {
  if (overrides && overrides[name]) return overrides[name];
  return name
    .split(/[-_]+/)
    .filter(Boolean)
    .map((part) => part[0].toUpperCase() + part.slice(1))
    .join(" ");
};

const projectDir = process.env.CLAUDE_PROJECT_DIR || process.cwd();
const settingsPath = path.join(projectDir, ".claude", "settings.json");

let settings = {};
try {
  settings = JSON.parse(fs.readFileSync(settingsPath, "utf8"));
} catch (err) {
  settings = {};
}

const config = settings.aiArchitect || {};
const roles = config.roles || {};

const entries = Object.entries(roles)
  .filter(([, cfg]) => cfg && cfg.enabled !== false)
  .map(([role, cfg]) => {
    const provider = (cfg && cfg.provider) || "claude";
    const roleTitle = titleize(role, ROLE_TITLE_OVERRIDES);
    const providerTitle = titleize(provider, PROVIDER_TITLE_OVERRIDES);
    return `${roleTitle} [${providerTitle}]`;
  });

process.stdout.write(entries.join(" | "));
