#!/usr/bin/env node
/* eslint-disable @typescript-eslint/no-require-imports */
/**
 * Reads the paper result CSVs and updates leaderboard-data.ts.
 * Runs automatically as a prebuild step, so you only need to edit the CSV.
 *
 * Manual run: node scripts/csv-to-data.js
 *
 * To add new results:
 * 1. Edit src/data/leaderboard.csv or leaderboard-cost.csv
 * 2. Commit and push — the build will auto-sync the TS file
 */

const fs = require("fs");
const path = require("path");

const csvPath = path.join(__dirname, "../src/data/leaderboard.csv");
const costCsvPath = path.join(__dirname, "../src/data/leaderboard-cost.csv");
const tsPath = path.join(__dirname, "../src/data/leaderboard-data.ts");

function readRows(filePath) {
  const csv = fs.readFileSync(filePath, "utf-8").replace(/\r/g, "").trim();
  return csv.split("\n").slice(1).map((line) => line.split(","));
}

const rows = readRows(csvPath).map((parts) => {
  return {
    agent: parts[0],
    model: parts[1],
    domain: parts[2],
    skillMethod: parts[3],
    vanilla: parseFloat(parts[4]),
    methodScore: parseFloat(parts[5]),
  };
});

const costRows = readRows(costCsvPath).map((parts) => ({
  agent: parts[0],
  model: parts[1],
  skillMethod: parts[2],
  all: parseFloat(parts[3]),
  solved: parseFloat(parts[4]),
  unsolved: parseFloat(parts[5]),
}));

const entries = rows
  .map(
    (r) =>
      `  { agent: "${r.agent}", model: "${r.model}", domain: "${r.domain}", skillMethod: "${r.skillMethod}", vanilla: ${r.vanilla}, methodScore: ${r.methodScore} },`
  )
  .join("\n");

const costEntries = costRows
  .map(
    (r) =>
      `  { agent: "${r.agent}", model: "${r.model}", skillMethod: "${r.skillMethod}", all: ${r.all}, solved: ${r.solved}, unsolved: ${r.unsolved} },`
  )
  .join("\n");

const uniqueMethods = [...new Set(rows.map((r) => r.skillMethod))];
const methodsArrayLiteral = uniqueMethods.map((m) => `"${m}"`).join(", ");

let ts = fs.readFileSync(tsPath, "utf-8");

function replaceBlock(src, startMarker, endMarker, replacement, label) {
  const startIdx = src.indexOf(startMarker);
  if (startIdx === -1) {
    console.error(`Could not find ${label} in leaderboard-data.ts`);
    process.exit(1);
  }
  const endIdx = src.indexOf(endMarker, startIdx);
  if (endIdx === -1) {
    console.error(`Could not find closing marker for ${label}`);
    process.exit(1);
  }
  return src.substring(0, startIdx) + replacement + src.substring(endIdx + endMarker.length);
}

// Replace leaderboardData array
ts = replaceBlock(
  ts,
  "export const leaderboardData: LeaderboardEntry[] = [",
  "];",
  `export const leaderboardData: LeaderboardEntry[] = [\n${entries}\n];`,
  "leaderboardData"
);

// Replace turnCostData array
ts = replaceBlock(
  ts,
  "export const turnCostData: TurnCostEntry[] = [",
  "];",
  `export const turnCostData: TurnCostEntry[] = [\n${costEntries}\n];`,
  "turnCostData"
);

// Replace SKILL_METHODS list (derived from unique CSV values)
ts = replaceBlock(
  ts,
  "export const SKILL_METHODS: SkillMethod[] = [",
  "];",
  `export const SKILL_METHODS: SkillMethod[] = [${methodsArrayLiteral}];`,
  "SKILL_METHODS"
);

fs.writeFileSync(tsPath, ts);
console.log(
  `Synced ${rows.length} scores, ${costRows.length} cost rows, and ${uniqueMethods.length} methods from CSV.`
);
