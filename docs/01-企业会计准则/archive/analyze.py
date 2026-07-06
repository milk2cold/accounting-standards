#!/usr/bin/env python3
import os
import re
import json
from pathlib import Path
from datetime import datetime

WORK_DIR = Path(
    "/Users/milkcold/Downloads/MC2026/30 Project/38 会计准则知识库/docs/01-企业会计准则"
)


def parse_frontmatter_simple(content):
    """简单的 frontmatter 解析"""
    frontmatter = {}
    if not content.startswith("---\n"):
        return frontmatter, content

    end = content.find("\n---\n", 4)
    if end == -1:
        return frontmatter, content

    fm_content = content[4:end]
    body = content[end + 5 :]

    for line in fm_content.split("\n"):
        line = line.rstrip()
        if not line or ":" not in line:
            continue
        if line.startswith("  "):
            continue  # 跳过嵌套内容
        key, value = line.split(":", 1)
        key = key.strip()
        value = value.strip().strip('"')
        if value.isdigit():
            frontmatter[key] = int(value)
        else:
            frontmatter[key] = value

    return frontmatter, body


def extract_effective_date(content):
    """提取施行日期"""
    patterns = [
        r"自(\d{4}年\d{1,2}月\d{1,2}日)起施行",
        r"自(\d{4}年\d{1,2}月\d{1,2}日)起执行",
        r"(\d{4}年\d{1,2}月\d{1,2}日)起施行",
    ]
    for pattern in patterns:
        match = re.search(pattern, content)
        if match:
            return match.group(1)
    return None


def extract_doc_number(content):
    """提取文号"""
    match = re.search(r"财会〔(\d{4})〕(\d+)号", content)
    if match:
        return f"财会〔{match.group(1)}〕{match.group(2)}号"
    return None


def main():
    print("🚀 开始分析会计准则文件...\n")

    json_path = WORK_DIR / "企业会计准则_全文.json"
    with open(json_path, "r", encoding="utf-8") as f:
        json_data = json.load(f)
    print(f"📄 JSON 文件加载成功，共 {len(json_data['articles'])} 篇准则\n")

    md_files = []
    for file_path in WORK_DIR.glob("*.md"):
        if file_path.name in ("index.md", "analysis-report.md"):
            continue
        with open(file_path, "r", encoding="utf-8") as f:
            raw_content = f.read()
        frontmatter, body = parse_frontmatter_simple(raw_content)
        md_files.append(
            {
                "filename": file_path.name,
                "frontmatter": frontmatter,
                "rawContent": raw_content,
            }
        )
    print(f"📝 加载了 {len(md_files)} 个 Markdown 文件\n")

    standards = []

    for md in md_files:
        fm = md["frontmatter"]
        num = fm.get("number", 999)
        if num == 999 and "基本准则" in md["filename"]:
            num = 0

        effective_date = extract_effective_date(md["rawContent"])
        doc_number = extract_doc_number(md["rawContent"])

        publish_date = fm.get("date", "未知")

        standards.append(
            {
                "number": num,
                "title": fm.get("title", md["filename"]),
                "shortTitle": fm.get("short_title", md["filename"]),
                "filename": md["filename"],
                "status": fm.get("status", "未知"),
                "publishDate": publish_date,
                "effectiveDate": effective_date,
                "docNumber": doc_number,
            }
        )

    standards.sort(key=lambda x: x["number"])

    index_content = """# 企业会计准则索引

> 本索引包含所有企业会计准则文件，按准则编号排序。

| 编号 | 准则名称 | 状态 | 发布日期 | 施行日期 | 文号 |
|------|----------|------|----------|----------|------|
"""

    for std in standards:
        status_emoji = {"现行有效": "✅", "已废止": "❌", "已修订": "📝"}.get(
            std["status"], "📋"
        )

        index_content += f"| {std['number'] if isinstance(std['number'], int) else '-'} | [{std['shortTitle']}]({std['filename']}) | {status_emoji} {std['status']} | {std['publishDate']} | {std['effectiveDate'] or '-'} | {std['docNumber'] or '-'} |\n"

    index_content += """

---

## 准则版本说明

以下准则包含多个版本（按准则编号分组）：

"""

    version_groups = {}
    for std in standards:
        num = std["number"]
        if num not in version_groups:
            version_groups[num] = []
        version_groups[num].append(std)

    for num in sorted(version_groups.keys()):
        group = version_groups[num]
        if len(group) > 1:
            cleaned_title = group[0]["shortTitle"]
            for suffix in [
                "（2006版）",
                "（2014版）",
                "（2017版）",
                "（2018版）",
                "（2019版）",
                "（2020版）",
            ]:
                cleaned_title = cleaned_title.replace(suffix, "")
            index_content += f"### 第{num}号准则 - {cleaned_title}\n\n"
            for std in sorted(group, key=lambda x: x.get("publishDate", "0")):
                ver_status_emoji = {
                    "现行有效": "✅",
                    "已废止": "❌",
                    "已修订": "📝",
                }.get(std["status"], "📋")
                index_content += f"- [{std['title']}]({std['filename']}) - {ver_status_emoji} {std['status']} (发布: {std['publishDate']})\n"
            index_content += "\n"

    index_content += f"""---

## 统计信息

- **准则总数**: {len(standards)}
- **现行有效**: {len([s for s in standards if s["status"] == "现行有效"])}
- **已废止**: {len([s for s in standards if s["status"] == "已废止"])}
- **JSON 源文件准则数**: {len(json_data["articles"])}

---

*最后更新: {datetime.now().strftime("%Y-%m-%d")}*
"""

    index_path = WORK_DIR / "index.md"
    with open(index_path, "w", encoding="utf-8") as f:
        f.write(index_content)
    print(f"✅ 索引文件已生成: {index_path}\n")

    print("🎉 任务完成！")


if __name__ == "__main__":
    main()
