#!/usr/bin/env python3
import json
import re
from pathlib import Path

WORK_DIR = Path(
    "/Users/milkcold/Downloads/MC2026/30 Project/38 会计准则知识库/docs/01-企业会计准则"
)


def main():
    # 需要检查的文件列表（基于之前的检查结果）
    warning_files = [
        "09-职工薪酬-2006.md",
        "12-债务重组-2006.md",
        "12-债务重组-2019.md",
        "21-租赁-2006.md",
        "22-金融工具确认和计量-2006.md",
        "22-金融工具确认和计量-2017.md",
        "23-金融资产转移-2017.md",
        "24-套期会计-2017.md",
        "25-保险合同-2020.md",
        "32-中期财务报告.md",
        "33-合并财务报表-2006.md",
        "33-合并财务报表.md",
        "34-每股收益.md",
        "35-分部报告.md",
        "37-金融工具列报-2006.md",
        "37-金融工具列报-2017.md",
    ]

    results = []

    for md_name in warning_files:
        md_file = WORK_DIR / md_name
        if not md_file.exists():
            continue

        with open(md_file, "r", encoding="utf-8") as f:
            content = f.read()

        # 解析 frontmatter
        if not content.startswith("---\n"):
            continue

        end = content.find("\n---\n", 4)
        if end == -1:
            continue

        frontmatter = content[4:end]

        title_match = re.search(r'title:\s*"([^"]+)"', frontmatter)
        url_match = re.search(r'origin_url:\s*"([^"]+)"', frontmatter)

        if not title_match or not url_match:
            continue

        title = title_match.group(1)
        origin_url = url_match.group(1)

        # 提取 md 正文
        body = content[end + 5 :]
        lines = body.split("\n")
        body_lines = []
        in_body = False
        for line in lines:
            if line.startswith("# ") and not in_body:
                continue
            if not in_body and line.strip():
                in_body = True
            if in_body:
                body_lines.append(line)

        md_body = "\n".join(body_lines)

        results.append(
            {
                "file": md_name,
                "title": title,
                "origin_url": origin_url,
                "md_body_length": len(md_body),
                "md_body_preview": md_body[:500],
            }
        )

        print(f"# {md_name}")
        print(f"## Title: {title}")
        print(f"## Origin URL: {origin_url}")
        print(f"## Body Length: {len(md_body)}")
        print(f"## Body Preview:")
        print(md_body[:500])
        print("\n---\n")


if __name__ == "__main__":
    main()
