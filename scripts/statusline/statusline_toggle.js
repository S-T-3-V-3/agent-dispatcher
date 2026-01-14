#!/usr/bin/env node
const fs = require("fs");
const path = require("path");

const MARKETPLACE_NAME = "cc-marketplace";
const PLUGIN_NAME = "cc-distribution";
const MARKER = "ai-architect-statusline";

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

const buildOurCommand = () => {
  const nodePath = process.execPath;
  const bash = [
    'plugin_dir="${CLAUDE_PLUGIN_ROOT:-}"',
    'if [ -z "$plugin_dir" ]; then exit 0; fi',
    `"${nodePath}" "\${plugin_dir}scripts/statusline/statusline.js" # ${MARKER}`,
  ].join("; ");

  return `bash -lc '${bash}'`;
};

const settings = readSettings();
const ourCommand = buildOurCommand();
// Robust regex to find our command block: bash -lc '... # MARKER'
const markerRegex = new RegExp(`bash\\s+-lc\\s+'[^']*#\\s*${MARKER}[^']*'`, 'g');

if (action === "disable") {
  if (settings.statusLine && settings.statusLine.command) {
    const currentCommand = settings.statusLine.command;
    if (currentCommand.includes(MARKER)) {
      // Remove our command and any surrounding separators
      const removeRegex = new RegExp(`\\s*(?:;|&&)?\\s*bash\\s+-lc\\s+'[^']*#\\s*${MARKER}[^']*'\\s*(?:;|&&)?`, 'g');
      let newCommand = currentCommand.replace(removeRegex, ' ; ').trim();

      // Clean up multiple separators or leading/trailing separators
      newCommand = newCommand.replace(/^\s*[;&]+\s*/, '').replace(/\s*[;&]+\s*$/, '').replace(/\s*[;&]+\s*[;&]+\s*/g, ' ; ');

      if (newCommand === "") {
        delete settings.statusLine;
      } else {
        settings.statusLine.command = newCommand;
      }
      writeSettings(settings);
      process.stdout.write("Statusline disabled for this project.\n");
    } else {
      process.stdout.write("Statusline was not enabled by this plugin.\n");
    }
  } else {
    process.stdout.write("Statusline was not enabled.\n");
  }
  process.exit(0);
}

// Enable logic
if (!settings.statusLine) {
  settings.statusLine = {
    type: "command",
    command: ourCommand,
  };
} else if (settings.statusLine.type === "command") {
  let currentCommand = settings.statusLine.command || "";
  if (markerRegex.test(currentCommand)) {
    // Replace existing version
    settings.statusLine.command = currentCommand.replace(markerRegex, ourCommand);
  } else {
    // Append our command
    settings.statusLine.command = currentCommand ? `${currentCommand} ; ${ourCommand}` : ourCommand;
  }
} else {
  // If it's type 'text', we override
  settings.statusLine = {
    type: "command",
    command: ourCommand,
  };
}

writeSettings(settings);
process.stdout.write("Statusline enabled for this project.\n");
