import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  output: "export",
  basePath: process.env.NEXT_PUBLIC_BASE_PATH || "",
  // Emit /leaderboard/index.html instead of /leaderboard.html so GitHub Pages
  // serves the route correctly when users land on /EvoAgentBench/leaderboard/.
  trailingSlash: true,
};

export default nextConfig;
