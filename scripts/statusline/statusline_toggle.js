#!/usr/bin/env node
const fs = require("fs");
const path = require("path");

const MARKETPLACE_NAME = "cc-marketplace";
const PLUGIN_NAME = "agent-dispatcher";
const MARKER = `${PLUGIN_NAME}-statusline`;

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

// Precision regexes - MUST include the PLUGIN_NAME or MARKER to avoid stomping others
const markerRegex = new RegExp(`bash\\s+-lc\\s+'[^']*#\\s*${MARKER}[^']*'`, 'g');
const legacyRegex = new RegExp(`bash\\s+-lc\\s+'[^']*${PLUGIN_NAME}[^']*scripts/statusline/statusline\\.js[^']*'`, 'g');

const removeOurCommand = (currentCommand) => {
  // Use specific patterns for THIS plugin
  const patterns = [
    new RegExp(`\\s*(?:;|&&|\\\\n)?\\s*bash\\s+-lc\\s+'[^']*#\\s*${MARKER}[^']*'\\s*(?:;|&&|\\\\n)?`, 'g'),
    new RegExp(`\\s*(?:;|&&|\\\\n)?\\s*bash\\s+-lc\\s+'[^']*${PLUGIN_NAME}[^']*scripts/statusline/statusline\\.js[^']*'\\s*(?:;|&&|\\\\n)?`, 'g')
  ];

  let newCommand = currentCommand;
  for (const pattern of patterns) {
    newCommand = newCommand.replace(pattern, ' ; ');
  }

  // Clean up: multiple separators, leading/trailing separators, and normalize to the user's preferred separator
  // We'll normalize to " ; " for standard spacing, or " \n " if they wanted columns
  newCommand = newCommand.trim()
    .replace(/^\s*[;&]+\s*/, '')
    .replace(/\s*[;&]+\s*$/, '')
    .replace(/\s*[;&]+\s*[;&]+\s*/g, ' ; ');

  return newCommand;
};

if (action === "disable") {
  if (settings.statusLine && settings.statusLine.command) {
    const currentCommand = settings.statusLine.command;
    const hasMarker = markerRegex.test(currentCommand);
    const hasLegacy = legacyRegex.test(currentCommand);

    if (hasMarker || hasLegacy) {
      const newCommand = removeOurCommand(currentCommand);

      if (newCommand === "") {
        delete settings.statusLine;
      } else {
        settings.statusLine.command = newCommand;
      }
      writeSettings(settings);
      process.stdout.write(`Statusline for ${PLUGIN_NAME} disabled for this project.\n`);
    } else {
      process.stdout.write(`Statusline for ${PLUGIN_NAME} was not enabled.\n`);
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
    // Replace existing version of our command
    settings.statusLine.command = currentCommand.replace(markerRegex, ourCommand);
  } else if (legacyRegex.test(currentCommand)) {
    // Replace legacy version of our command
    settings.statusLine.command = currentCommand.replace(legacyRegex, ourCommand);
  } else {
    // Append our command safely. 
    // We'll use " ; " as a default, but if someone wants it on a "different line" 
    // they might prefer " \n " if Claude supports it. 
    // For now, let's stick to " ; " but make it easy to change.
    const separator = " ; ";
    settings.statusLine.command = currentCommand ? `${currentCommand}${separator}${ourCommand}` : ourCommand;
  }
} else {
  // If it's type 'text', we append or wrap
  const existingText = settings.statusLine.value || "";
  settings.statusLine = {
    type: "command",
    command: existingText ? `echo "${existingText}" ; ${ourCommand}` : ourCommand,
  };
}

writeSettings(settings);
process.stdout.write(`Statusline for ${PLUGIN_NAME} enabled for this project.\n`);
