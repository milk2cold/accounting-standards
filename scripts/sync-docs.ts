import {
  existsSync,
  mkdirSync,
  readdirSync,
  readFileSync,
  rmSync,
  statSync,
  writeFileSync,
} from "node:fs";
import { join, resolve } from "node:path";

const repoRoot = resolve(import.meta.dir, "..");
const targetDir = join(repoRoot, "src", "content", "docs");
const syncedDirectories = [
  "01-企业会计准则",
  "02-企业会计准则解释",
  "03-企业会计准则指南",
  "08-每月更新",
  "09-推荐资源",
];

const ignoredFiles = new Set([
  ".DS_Store",
  "企业会计准则_全文.json",
  "企业会计准则_全文.json.backup",
  "企业会计准则解释_全文.json",
  "企业会计准则指南_全文.json",
  "frontmatter-验证报告.md",
  "origin_url-审计修复报告.md",
  "检查整理报告-2026-03-07.md",
]);
const ignoredDirectories = new Set(["archive"]);

const ignoredExtensions = new Set([
  ".json",
  ".backup",
  ".doc",
  ".docx",
  ".pdf",
  ".txt",
  ".py",
]);

function ensureDir(path: string) {
  if (!existsSync(path)) mkdirSync(path, { recursive: true });
}

function shouldCopy(fileName: string) {
  if (ignoredFiles.has(fileName)) return false;
  return ![...ignoredExtensions].some((ext) => fileName.endsWith(ext));
}

function findSourceDir() {
  const candidates = [
    join(repoRoot, "docs"),
    join(resolve(repoRoot, ".."), "docs"),
  ];

  for (const candidate of candidates) {
    if (
      existsSync(candidate) &&
      syncedDirectories.every((directory) => existsSync(join(candidate, directory)))
    ) {
      return candidate;
    }
  }

  return null;
}

function ensureFrontmatter(sourcePath: string, targetPath: string, relativeDir: string) {
  const content = readFileSync(sourcePath, "utf8");
  const normalizedContent = content.replaceAll("](/docs/", "](docs/");
  if (content.startsWith("---\n")) {
    const sanitized = normalizedContent.replace(/^layout:\s*.+\n/m, "");
    writeFileSync(targetPath, sanitized);
    return;
  }

  const heading = normalizedContent.match(/^#\s+(.+)$/m)?.[1]?.trim();
  if (!heading) return;

  const category = relativeDir.split("/")[0];
  const wrapped = [
    "---",
    `title: "${heading.replace(/"/g, '\\"')}"`,
    `category: "${category}"`,
    "---",
    "",
    normalizedContent,
  ].join("\n");
  writeFileSync(targetPath, wrapped);
}

function syncDirectory(sourceDir: string, from: string, to: string) {
  ensureDir(to);
  for (const entry of readdirSync(from)) {
    const sourcePath = join(from, entry);
    const targetPath = join(to, entry);
    const stat = statSync(sourcePath);

    if (stat.isDirectory()) {
      if (ignoredDirectories.has(entry)) continue;
      syncDirectory(sourceDir, sourcePath, targetPath);
      continue;
    }

    if (!shouldCopy(entry)) continue;
    if (entry.endsWith(".md")) {
      const relativeDir = from.replace(`${sourceDir}/`, "");
      ensureFrontmatter(sourcePath, targetPath, relativeDir);
      continue;
    }

    writeFileSync(targetPath, readFileSync(sourcePath));
  }
}

const sourceDir = findSourceDir();

if (!sourceDir) {
  if (existsSync(targetDir)) {
    console.log(`No external docs directory found. Keep checked-in content at ${targetDir}`);
    process.exit(0);
  }

  throw new Error("Unable to locate docs source directory for site sync.");
}

const existingIndexFiles: Record<string, string> = {};
for (const directory of syncedDirectories) {
  const indexPath = join(targetDir, directory, "index.md");
  if (existsSync(indexPath)) {
    existingIndexFiles[directory] = readFileSync(indexPath, "utf8");
  }
}

rmSync(targetDir, { recursive: true, force: true });
ensureDir(targetDir);

for (const directory of syncedDirectories) {
  syncDirectory(sourceDir, join(sourceDir, directory), join(targetDir, directory));
}

for (const [directory, content] of Object.entries(existingIndexFiles)) {
  const indexPath = join(targetDir, directory, "index.md");
  writeFileSync(indexPath, content);
}

console.log(`Synced docs from ${sourceDir} into ${targetDir}`);
