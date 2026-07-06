import { defineConfig } from "astro/config";
import tailwindcss from "@tailwindcss/vite";

const repository = process.env.GITHUB_REPOSITORY ?? "";
const [owner = "", repo = ""] = repository.split("/");
const isUserSite = repo.endsWith(".github.io");
const fallbackRepo = "accounting-standards";
const base = repository
  ? !isUserSite
    ? `/${repo}`
    : "/"
  : `/${fallbackRepo}`;
const site =
  repository && owner
    ? `https://${owner}.github.io${isUserSite ? "" : base}`
    : `https://milk2cold.github.io${base}`;

export default defineConfig({
  site,
  base,
  markdown: {
    // Astro 7 默认使用 Sätteri 处理器，内置 heading ID 生成
    syntaxHighlight: "shiki",
  },
  vite: {
    plugins: [tailwindcss()],
  },
  build: {
    format: "directory",
  },
});
