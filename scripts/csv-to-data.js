#!/usr/bin/env node
/**
 * Reads leaderboard.csv and updates leaderboard-data.ts.
 * Runs automatically as a prebuild step, so you only need to edit the CSV.
 *
 * Manual run: node scripts/csv-to-data.js
 *
 * To add new results:
 * 1. Edit src/data/leaderboard.csv (add/modify rows)
 * 2. Commit and push — the build will auto-sync the TS file
 */

const fs = require("fs");
const path = require("path");

const csvPath = path.join(__dirname, "../src/data/leaderboard.csv");
const tsPath = path.join(__dirname, "../src/data/leaderboard-data.ts");

const csv = fs.readFileSync(csvPath, "utf-8").replace(/\r/g, "").trim();
const lines = csv.split("\n");
const rows = lines.slice(1).map((line) => {
  const parts = line.split(",");
  return {
    agent: parts[0],
    model: parts[1],
    domain: parts[2],
    skillMethod: parts[3],
    without: parseFloat(parts[4]),
    withSkills: parseFloat(parts[5]),
    cost: parts.slice(6).join(","),
  };
});

const entries = rows
  .map(
    (r) =>
      `  { agent: "${r.agent}", model: "${r.model}", domain: "${r.domain}", skillMethod: "${r.skillMethod}", without: ${r.without}, withSkills: ${r.withSkills}, cost: "${r.cost}" },`
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
  `Synced ${rows.length} entries and ${uniqueMethods.length} skill methods from CSV.`
);
