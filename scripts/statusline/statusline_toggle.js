#!/usr/bin/env node
const fs = require("fs");
const path = require("path");

const MARKETPLACE_NAME = "cc-marketplace";
const PLUGIN_NAME = "cc-distribution";

const action = (process.argv[2] || "enable").toLowerCase();
const projectDir = process.env.CLAUDE_PROJECT_DIR || process.cwd();
const settingsPath = path.join(projectDir, ".claude", "settings.json");

const readSettings = () => {
  try {
    return JSON.parse(fs.readFileSync(settingsPath, "utf8"));
  } catch (err) {
    return {};
  }
};

const writeSettings = (settings) => {
  fs.mkdirSync(path.dirname(settingsPath), { recursive: true });
  fs.writeFileSync(settingsPath, JSON.stringify(settings, null, 2) + "\n");
};

const buildStatuslineCommand = () => {
  const nodePath = process.execPath;
  const bash = [
    'plugin_dir="${CLAUDE_PLUGIN_ROOT:-}"',
    `if [ -z "$plugin_dir" ]; then plugin_dir=$(ls -td ~/.claude/plugins/cache/${MARKETPLACE_NAME}/${PLUGIN_NAME}/*/ 2>/dev/null | head -1); fi`,
    'if [ -z "$plugin_dir" ]; then exit 0; fi',
    `"${nodePath}" "\${plugin_dir}scripts/statusline/statusline.js"`,
  ].join("; ");

  return `bash -lc '${bash}'`;
};

const settings = readSettings();

if (action === "disable") {
  if (settings.statusLine) {
    delete settings.statusLine;
    writeSettings(settings);
  }
  process.stdout.write("Statusline disabled for this project.\n");
  process.exit(0);
}

settings.statusLine = {
  type: "command",
  command: buildStatuslineCommand(),
};

writeSettings(settings);
process.stdout.write("Statusline enabled for this project.\n");
