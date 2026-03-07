import { defineConfig } from "astro/config";
import tailwindcss from "@tailwindcss/vite";
import markdownTransform from "./src/integrations/markdown-transform";

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
  integrations: [markdownTransform()],
  vite: {
    plugins: [tailwindcss()],
  },
  build: {
    format: "directory",
  },
});
