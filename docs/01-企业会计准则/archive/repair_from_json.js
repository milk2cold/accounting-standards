const fs = require("fs");
const path = require("path");

const WORK_DIR =
  "/Users/milkcold/Downloads/MC2026/30 Project/38 会计准则知识库/docs/01-企业会计准则";
const JSON_FILES = [
  path.join(WORK_DIR, "企业会计准则_全文.json"),
  path.join(WORK_DIR, "企业会计准则_全文.json.backup"),
];
const REPORT_PATH = path.join(WORK_DIR, "检查整理报告-2026-03-07.md");
const MANUAL_HTML_SOURCES = {
  "07-非货币性资产交换-2006.md": {
    htmlPath: "/tmp/cas_old_pages/07-2006.html",
    originUrl: "https://www.casc.org.cn/2018/0815/202808.shtml",
  },
  "09-职工薪酬-2006.md": {
    htmlPath: "/tmp/cas_old_pages/09-2006.html",
    originUrl: "https://www.casc.org.cn/2018/0815/202805.shtml",
  },
  "15-建造合同-2006.md": {
    htmlPath: "/tmp/cas_old_pages/15-2006.html",
    originUrl: "https://www.casc.org.cn/2018/0815/202797.shtml",
  },
  "16-政府补助-2006.md": {
    htmlPath: "/tmp/cas_old_pages/16-2006.html",
    originUrl: "https://www.casc.org.cn/2018/0815/202795.shtml",
  },
  "21-租赁-2006.md": {
    htmlPath: "/tmp/cas_old_pages/21-2006.html",
    originUrl: "https://www.casc.org.cn/2018/0815/202789.shtml",
  },
  "30-财务报表列报-2006.md": {
    htmlPath: "/tmp/cas_old_pages/30-2006.html",
    originUrl: "https://www.casc.org.cn/2018/0815/202776.shtml",
  },
  "33-合并财务报表-2006.md": {
    htmlPath: "/tmp/cas_old_pages/33-2006.html",
    originUrl: "https://www.casc.org.cn/2018/0814/202772.shtml",
  },
};
const EXCLUDED_FILES = new Set([
  "index.md",
  "frontmatter-验证报告.md",
  "origin_url-审计修复报告.md",
  "检查整理报告-2026-03-07.md",
]);

function parseFrontmatter(content) {
  const match = content.match(/^---\n([\s\S]*?)\n---\n([\s\S]*)$/);
  if (!match) {
    return null;
  }
  return {
    raw: match[1],
    body: match[2],
  };
}

function extractField(frontmatter, key) {
  const match = frontmatter.match(new RegExp(`^${key}:\\s*"([^"]+)"`, "m"));
  return match ? match[1] : "";
}

function extractNumber(frontmatter) {
  const match = frontmatter.match(/^number:\s*(\d+)/m);
  return match ? Number(match[1]) : null;
}

function extractVersionYear(text) {
  const versionMatch = text.match(/(?:\(|（)(\d{4})版(?:\)|）)/);
  if (versionMatch) {
    return Number(versionMatch[1]);
  }
  return null;
}

function extractPromulgationYear(content) {
  const match = content.match(/（(\d{4})年/);
  return match ? Number(match[1]) : null;
}

function normalizeTitle(title) {
  return title
    .replace(/（财会〔\d{4}〕\d+号）/g, "")
    .replace(/（\d{4}版）/g, "")
    .replace(/[（(].*?[)）]/g, "")
    .replace(/\s+/g, "")
    .replace(/—+/g, "——")
    .trim();
}

function cleanupLine(line) {
  let output = line.trim();
  if (!output) {
    return "";
  }
  output = output.replace(/\(\(/g, "《").replace(/\)\)/g, "》");
  output = output.replace(/————/g, "——");
  output = output.replace(/《《/g, "《").replace(/》》/g, "》");
  output = output.replace(/([一-龥])\s+([一-龥])/g, "$1$2");
  output = output.replace(/《\s+/g, "《").replace(/\s+》/g, "》");
  return output;
}

function shouldDropLine(line) {
  return (
    !line ||
    /^当前位置/.test(line) ||
    /^\d{4}年\d{1,2}月\d{1,2}日/.test(line) ||
    /^主办单位：/.test(line) ||
    /^网站标识码/.test(line) ||
    /^技术支持：/.test(line) ||
    /^中华人民共和国财政部 版权所有/.test(line)
  );
}

function buildMarkdownBody(fileTitle, articleContent) {
  const rawLines = articleContent
    .split(/\r?\n/)
    .map(cleanupLine)
    .filter((line) => !shouldDropLine(line));

  const contentLines = [...rawLines];
  while (contentLines[0] && contentLines[0] === fileTitle) {
    contentLines.shift();
  }

  const output = [`# ${fileTitle}`];

  for (const line of contentLines) {
    if (!line) {
      continue;
    }
    if (/^第[一二三四五六七八九十百〇零]+章/.test(line)) {
      output.push("", `## ${line}`);
      continue;
    }
    if (/^第[一二三四五六七八九十百〇零\d]+条/.test(line)) {
      const formatted = line.replace(
        /^(第[一二三四五六七八九十百〇零\d]+条)\s*/,
        "**$1** "
      );
      output.push("", formatted);
      continue;
    }
    output.push("", line);
  }

  return `${output.join("\n").trim()}\n`;
}

function decodeHtml(text) {
  return text
    .replace(/&nbsp;/g, " ")
    .replace(/&mdash;/g, "——")
    .replace(/&ldquo;/g, "“")
    .replace(/&rdquo;/g, "”")
    .replace(/&lsquo;/g, "‘")
    .replace(/&rsquo;/g, "’")
    .replace(/&lt;/g, "<")
    .replace(/&gt;/g, ">")
    .replace(/&amp;/g, "&")
    .replace(/&#8226;/g, "•")
    .replace(/&#160;/g, " ");
}

function stripHtmlTags(text) {
  return decodeHtml(text.replace(/<[^>]+>/g, "")).replace(/\s+/g, " ").trim();
}

function buildMarkdownFromHtml(fileTitle, html) {
  const infoConMatch = html.match(/<div class="infoCon">([\s\S]*?)<\/div>\s*<\/div>/);
  if (!infoConMatch) {
    return null;
  }

  const paragraphMatches = [...infoConMatch[1].matchAll(/<p[^>]*>([\s\S]*?)<\/p>/g)];
  const lines = paragraphMatches
    .map((match) => stripHtmlTags(match[1]))
    .map(cleanupLine)
    .filter((line) => line && !/^(来源[:：]|上一篇|下一篇)/.test(line));

  const output = [`# ${fileTitle}`];
  for (const line of lines) {
    if (/^企业会计准则第\d+号/.test(line) && !/第[一二三四五六七八九十百〇零]+章/.test(line)) {
      continue;
    }
    if (/^财会\[\d{4}\]\d+号/.test(line)) {
      output.push(
        "",
        `（${line.replace(/^财会\[(\d{4})\](\d+)号$/, "财会〔$1〕$2号")}）`
      );
      continue;
    }
    if (/^第[一二三四五六七八九十百〇零]+章/.test(line)) {
      output.push("", `## ${line}`);
      continue;
    }
    if (/^第[一二三四五六七八九十百〇零\d]+条/.test(line)) {
      output.push(
        "",
        line.replace(/^(第[一二三四五六七八九十百〇零\d]+条)[\s　]*/, "**$1** ")
      );
      continue;
    }
    output.push("", line);
  }

  return `${output.join("\n").trim()}\n`;
}

function loadArticles() {
  const seen = new Set();
  const articles = [];

  for (const jsonPath of JSON_FILES) {
    const data = JSON.parse(fs.readFileSync(jsonPath, "utf8"));
    for (const article of data.articles) {
      const key = `${article.title}@@${article.url}`;
      if (seen.has(key)) {
        continue;
      }
      seen.add(key);
      const numberMatch = article.title.match(/第(\d+)号/);
      articles.push({
        ...article,
        number: numberMatch ? Number(numberMatch[1]) : 0,
        normalizedTitle: normalizeTitle(article.title),
        promulgationYear: extractPromulgationYear(article.content),
      });
    }
  }

  return articles;
}

function matchArticle(fileInfo, articles) {
  const candidates = articles.filter((article) => article.number === fileInfo.number);
  if (candidates.length === 0) {
    return null;
  }
  if (candidates.length === 1) {
    return candidates[0];
  }

  const desiredYear =
    extractVersionYear(fileInfo.title) ||
    extractVersionYear(fileInfo.fileName) ||
    null;
  if (desiredYear) {
    const exactYearMatch = candidates.find(
      (article) => article.promulgationYear === desiredYear
    );
    if (exactYearMatch) {
      return exactYearMatch;
    }
    return null;
  }

  const normalizedFileTitle = normalizeTitle(fileInfo.title);
  const exactTitleMatch = candidates.find(
    (article) => article.normalizedTitle === normalizedFileTitle
  );
  if (exactTitleMatch) {
    return exactTitleMatch;
  }

  return null;
}

function updateOriginUrl(frontmatter, url) {
  if (/^origin_url:\s*"/m.test(frontmatter)) {
    return frontmatter.replace(/^origin_url:\s*"[^"]*"/m, `origin_url: "${url}"`);
  }
  return `${frontmatter}\norigin_url: "${url}"`;
}

function main() {
  const articles = loadArticles();
  const files = fs
    .readdirSync(WORK_DIR)
    .filter((file) => file.endsWith(".md") && !EXCLUDED_FILES.has(file))
    .sort();

  const repairedContent = [];
  const repairedOrigin = [];
  const unresolved = [];

  for (const fileName of files) {
    const filePath = path.join(WORK_DIR, fileName);
    const original = fs.readFileSync(filePath, "utf8");
    const parsed = parseFrontmatter(original);
    if (!parsed) {
      unresolved.push(`${fileName}: 缺少 frontmatter`);
      continue;
    }

    const title = extractField(parsed.raw, "title");
    const number = extractNumber(parsed.raw);
    const originUrl = extractField(parsed.raw, "origin_url");
    const bodyWithoutHeading = parsed.body.replace(/^# .*\n?/, "").trim();

    const fileInfo = {
      fileName,
      title,
      number,
    };
    const manualSource = MANUAL_HTML_SOURCES[fileName];
    if (manualSource && fs.existsSync(manualSource.htmlPath)) {
      let nextFrontmatter = updateOriginUrl(parsed.raw, manualSource.originUrl);
      const html = fs.readFileSync(manualSource.htmlPath, "utf8");
      const nextBody = buildMarkdownFromHtml(title, html);
      if (!nextBody) {
        unresolved.push(`${fileName}: 历史 HTML 解析失败`);
        continue;
      }
      fs.writeFileSync(filePath, `---\n${nextFrontmatter}\n---\n\n${nextBody}`, "utf8");
      repairedContent.push(`${fileName} (使用准则委历史页重建正文)`);
      repairedOrigin.push(`${fileName} -> ${manualSource.originUrl}`);
      continue;
    }

    const matchedArticle = matchArticle(fileInfo, articles);

    if (!matchedArticle) {
      if (!/mof\.gov\.cn|casc\.org\.cn/.test(originUrl) || bodyWithoutHeading.length < 1200) {
        unresolved.push(`${fileName}: 本地 JSON 无法可靠匹配版本，未自动修复`);
      }
      continue;
    }

    let nextFrontmatter = parsed.raw;
    let nextBody = parsed.body;
    let changed = false;

    if (matchedArticle.url && originUrl !== matchedArticle.url) {
      nextFrontmatter = updateOriginUrl(nextFrontmatter, matchedArticle.url);
      repairedOrigin.push(`${fileName} -> ${matchedArticle.url}`);
      changed = true;
    }

    const contentTooShort = bodyWithoutHeading.length < matchedArticle.content.length * 0.75;
    if (contentTooShort) {
      nextBody = buildMarkdownBody(title, matchedArticle.content);
      repairedContent.push(
        `${fileName} (${bodyWithoutHeading.length} -> ${matchedArticle.content.length})`
      );
      changed = true;
    }

    if (changed) {
      fs.writeFileSync(filePath, `---\n${nextFrontmatter}\n---\n\n${nextBody}`, "utf8");
    }
  }

  const report = [
    "# 企业会计准则检查整理报告",
    "",
    `- 检查日期: 2026-03-07`,
    `- 检查目录: \`docs/01-企业会计准则\``,
    `- 数据源: \`企业会计准则_全文.json\` + \`企业会计准则_全文.json.backup\``,
    "",
    "## 已补齐正文",
    repairedContent.length ? repairedContent.map((line) => `- ${line}`).join("\n") : "- 无",
    "",
    "## 已修正官方来源链接",
    repairedOrigin.length ? repairedOrigin.map((line) => `- ${line}`).join("\n") : "- 无",
    "",
    "## 仍需外部补源的文件",
    unresolved.length ? unresolved.map((line) => `- ${line}`).join("\n") : "- 无",
    "",
  ].join("\n");

  fs.writeFileSync(REPORT_PATH, `${report}\n`, "utf8");
  console.log(`补齐正文: ${repairedContent.length}`);
  console.log(`修正链接: ${repairedOrigin.length}`);
  console.log(`待外部补源: ${unresolved.length}`);
}

main();
