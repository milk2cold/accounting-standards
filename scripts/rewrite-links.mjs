// scripts/rewrite-links.mjs
// 构建后处理：将 dist 中所有 HTML 的内部相对链接（docs/、./、../ 开头）
// 重写为完整绝对 URL，避免依赖 <base href> 解析，使链接在源码中可见地包含站点前缀。
// 外部链接（http(s)://、//、#、mailto:、data:）及以 / 开头的链接保持不变。
import { readdirSync, readFileSync, writeFileSync, statSync } from "node:fs";
import { join } from "node:path";

function resolveSite() {
  const repo = process.env.GITHUB_REPOSITORY;
  if (repo && repo.includes("/")) {
    const [owner, name] = repo.split("/");
    const base = name.endsWith(".github.io") ? "" : `/${name}`;
    return `https://${owner}.github.io${base}`;
  }
  return "https://milk2cold.github.io/accounting-standards";
}

const SITE = resolveSite().replace(/\/+$/, "");
const DIST = join(process.cwd(), "dist");

const hrefRe = /(href=")(docs\/|\.\/|\.\.\/)([^"]*)(")/g;

function rewriteHtml(html) {
  return html.replace(hrefRe, (_m, open, prefix, rest, close) => {
    const clean = rest.replace(/^\.\//, "").replace(/^(\.\.\/)+/, "");
    return `${open}${SITE}/${clean}${close}`;
  });
}

function walk(dir) {
  for (const entry of readdirSync(dir)) {
    const full = join(dir, entry);
    const st = statSync(full);
    if (st.isDirectory()) {
      walk(full);
    } else if (entry.endsWith(".html")) {
      const html = readFileSync(full, "utf-8");
      const out = rewriteHtml(html);
      if (out !== html) writeFileSync(full, out, "utf-8");
    }
  }
}

walk(DIST);
console.log(`[rewrite-links] 已将 dist 内部相对链接重写为绝对 URL（站点前缀：${SITE}）`);
