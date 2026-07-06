import {
  existsSync,
  mkdirSync,
  readdirSync,
  readFileSync,
  rmSync,
  statSync,
  writeFileSync,
} from "node:fs";
import { join, resolve, relative, normalize } from "node:path";

const repoRoot = resolve(import.meta.dir, "..");
const targetDir = join(repoRoot, "src", "content", "docs");

// 安全白名单：targetDir 必须在 repoRoot/src/content/docs 下
const EXPECTED_TARGET_SUBPATH = join("src", "content", "docs");

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

/**
 * 安全校验：确认目标目录路径合法，防止误删重要文件。
 *
 * 检查规则：
 * 1. targetDir 必须位于 repoRoot 之下
 * 2. targetDir 的相对路径必须与预期白名单一致
 * 3. 路径中不得包含 ..（防止路径遍历）
 */
function assertSafeTargetDir(target: string, root: string): void {
  const normalizedTarget = normalize(target);
  const normalizedRoot = normalize(root);

  // 规则1：targetDir 必须在 repoRoot 之下
  const rel = relative(normalizedRoot, normalizedTarget);
  if (!rel || rel.startsWith("..") || rel === "") {
    throw new Error(
      `[安全校验失败] targetDir 不在 repoRoot 之下\n` +
        `  targetDir: ${normalizedTarget}\n` +
        `  repoRoot:  ${normalizedRoot}\n` +
        `  relative:  ${rel || "(同目录)"}`
    );
  }

  // 规则2：相对路径必须与预期白名单一致
  if (rel !== EXPECTED_TARGET_SUBPATH) {
    throw new Error(
      `[安全校验失败] targetDir 相对路径不匹配预期\n` +
        `  实际路径:   ${rel}\n` +
        `  预期路径:   ${EXPECTED_TARGET_SUBPATH}\n` +
        `  完整路径:   ${normalizedTarget}`
    );
  }

  // 规则3：路径中不得包含 ..
  if (normalizedTarget.includes("..")) {
    throw new Error(
      `[安全校验失败] targetDir 路径包含 ..\n` +
        `  targetDir: ${normalizedTarget}\n` +
        `  路径遍历攻击风险！`
    );
  }
}

/**
 * 安全删除目录：在 rmSync 之前执行多重校验。
 */
function safeRemoveDir(dir: string, root: string): void {
  // 校验路径合法性
  assertSafeTargetDir(dir, root);

  // 二次确认：目录确实存在且不为根目录
  if (!existsSync(dir)) {
    return;
  }

  if (dir === root || dir === "/" || dir === normalize(root)) {
    throw new Error(
      `[安全校验失败] 拒绝删除根目录\n` +
        `  targetDir: ${dir}\n` +
        `  repoRoot:  ${root}`
    );
  }

  console.log(`[安全删除] 正在清理目录: ${dir}`);
  rmSync(dir, { recursive: true, force: true });
}

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

// === 主流程 ===

// 步骤1：执行安全校验（在任何删除操作之前）
assertSafeTargetDir(targetDir, repoRoot);

const sourceDir = findSourceDir();

if (!sourceDir) {
  if (existsSync(targetDir)) {
    console.log(
      `[跳过] 未找到外部 docs 目录，保留已检入内容: ${targetDir}`
    );
    process.exit(0);
  }

  console.error(
    `[错误] 无法定位 docs 源目录用于站点同步。\n` +
      `查找位置:\n` +
      `  - ${join(repoRoot, "docs")}\n` +
      `  - ${join(resolve(repoRoot, ".."), "docs")}\n\n` +
      `请确保 docs 目录存在且包含以下子目录:\n` +
      syncedDirectories.map((d) => `  - ${d}`).join("\n")
  );
  process.exit(1);
}

// 步骤2：备份现有 index.md 文件
const existingIndexFiles: Record<string, string> = {};
for (const directory of syncedDirectories) {
  const indexPath = join(targetDir, directory, "index.md");
  if (existsSync(indexPath)) {
    existingIndexFiles[directory] = readFileSync(indexPath, "utf8");
  }
}

// 步骤3：安全删除目标目录（带校验）
safeRemoveDir(targetDir, repoRoot);
ensureDir(targetDir);

// 步骤4：执行同步
for (const directory of syncedDirectories) {
  syncDirectory(sourceDir, join(sourceDir, directory), join(targetDir, directory));
}

// 步骤5：恢复 index.md 文件
for (const [directory, content] of Object.entries(existingIndexFiles)) {
  const indexPath = join(targetDir, directory, "index.md");
  writeFileSync(indexPath, content);
}

console.log(`[完成] 文档已同步: ${sourceDir} -> ${targetDir}`);
