#!/usr/bin/env node
/**
 * Reads leaderboard.csv and updates the leaderboardData array in leaderboard-data.ts.
 *
 * Usage: node scripts/csv-to-data.js
 *
 * To add new results:
 * 1. Edit src/data/leaderboard.csv (add/modify rows)
 * 2. Run: node scripts/csv-to-data.js
 * 3. Commit and push
 */

const fs = require("fs");
const path = require("path");

const csvPath = path.join(__dirname, "../src/data/leaderboard.csv");
const tsPath = path.join(__dirname, "../src/data/leaderboard-data.ts");

// Read CSV
const csv = fs.readFileSync(csvPath, "utf-8").trim();
const lines = csv.split("\n");
const headers = lines[0].split(",");
const rows = lines.slice(1).map((line) => {
  // Handle commas inside cost values like "↓ 21.9% turns"
  const parts = line.split(",");
  return {
    agent: parts[0],
    model: parts[1],
    domain: parts[2],
    skillMethod: parts[3],
    without: parseFloat(parts[4]),
    withSkills: parseFloat(parts[5]),
    cost: parts.slice(6).join(","), // in case cost has commas
  };
});

// Generate TS entries
const entries = rows
  .map(
    (r) =>
      `  { agent: "${r.agent}", model: "${r.model}", domain: "${r.domain}", skillMethod: "${r.skillMethod}", without: ${r.without}, withSkills: ${r.withSkills}, cost: "${r.cost}" },`
  )
  .join("\n");

// Read existing TS file
let ts = fs.readFileSync(tsPath, "utf-8");

// Replace leaderboardData array
const startMarker = "export const leaderboardData: LeaderboardEntry[] = [";
const endMarker = "];";

const startIdx = ts.indexOf(startMarker);
if (startIdx === -1) {
  console.error("Could not find leaderboardData array in leaderboard-data.ts");
  process.exit(1);
}

const endIdx = ts.indexOf(endMarker, startIdx);
if (endIdx === -1) {
  console.error("Could not find closing bracket of leaderboardData array");
  process.exit(1);
}

const newArray = `${startMarker}\n${entries}\n${endMarker}`;
ts = ts.substring(0, startIdx) + newArray + ts.substring(endIdx + endMarker.length);

fs.writeFileSync(tsPath, ts);
console.log(`Updated leaderboard-data.ts with ${rows.length} entries from CSV.`);
