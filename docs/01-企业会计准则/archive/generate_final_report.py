#!/usr/bin/env python3
import json
import re
from pathlib import Path

WORK_DIR = Path(
    "/Users/milkcold/Downloads/MC2026/30 Project/38 会计准则知识库/docs/01-企业会计准则"
)


def main():
    print("📋 生成最终验证报告...\n")

    # 1. 读取 JSON 数据源
    json_path = WORK_DIR / "企业会计准则_全文.json"
    with open(json_path, "r", encoding="utf-8") as f:
        json_data = json.load(f)

    # 建立标题到 URL 的映射
    json_title_to_url = {}
    for article in json_data["articles"]:
        title = article["title"]
        url = article["url"]
        json_title_to_url[title] = url

        # 简化标题也加入
        simple_title = re.sub(r"（财会〔\d{4}〕\d+号）", "", title)
        simple_title = re.sub(r"（\d{4}版）", "", simple_title)
        if simple_title not in json_title_to_url:
            json_title_to_url[simple_title] = url

    # 2. 检查所有 md 文件
    md_files = list(WORK_DIR.glob("*.md"))
    md_files = [
        f
        for f in md_files
        if f.name
        not in ("index.md", "analysis-report.md", "SOP.md", "frontmatter-验证报告.md")
    ]
    md_files.sort()

    report_lines = []
    report_lines.append("# 企业会计准则 origin_url 审计与修复报告\n")
    report_lines.append(
        f"> 生成时间: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    )
    report_lines.append("\n---\n")
    report_lines.append("## 修复摘要\n")

    fixed_files = []
    ok_files = []

    for md_file in md_files:
        with open(md_file, "r", encoding="utf-8") as f:
            content = f.read()

        if not content.startswith("---\n"):
            continue

        end = content.find("\n---\n", 4)
        if end == -1:
            continue

        frontmatter = content[4:end]

        title_match = re.search(r'title:\s*"([^"]+)"', frontmatter)
        url_match = re.search(r'origin_url:\s*"([^"]+)"', frontmatter)

        if not title_match:
            continue

        title = title_match.group(1)
        origin_url = url_match.group(1) if url_match else None

        # 检查是否是正确的 URL
        is_generic = False
        if origin_url:
            if (
                origin_url.rstrip("/")
                == "http://kjs.mof.gov.cn/zt/kjzzss/kuaijizhunzeshishi"
            ):
                is_generic = True

        if is_generic:
            fixed_files.append(
                {
                    "file": md_file.name,
                    "title": title,
                    "url": origin_url,
                    "status": "❌ 仍为错误链接",
                }
            )
        elif origin_url:
            ok_files.append(
                {
                    "file": md_file.name,
                    "title": title,
                    "url": origin_url,
                    "status": "✅ 正确",
                }
            )
        else:
            fixed_files.append(
                {"file": md_file.name, "title": title, "url": "-", "status": "⚠️  缺失"}
            )

    report_lines.append(f"\n- **已修复/正确**: {len(ok_files)} 个文件\n")
    report_lines.append(f"- **仍有问题**: {len(fixed_files)} 个文件\n")

    # 详细列表
    report_lines.append("\n---\n")
    report_lines.append("## 文件详情\n")
    report_lines.append("\n| 状态 | 文件名 | 标题 | origin_url |\n")
    report_lines.append("|------|--------|------|------------|\n")

    for f in ok_files:
        report_lines.append(
            f"| {f['status']} | [{f['file']}]({f['file']}) | {f['title']} | [链接]({f['url']}) |\n"
        )

    for f in fixed_files:
        url_display = f"[链接]({f['url']})" if f["url"] != "-" else "-"
        report_lines.append(
            f"| {f['status']} | [{f['file']}]({f['file']}) | {f['title']} | {url_display} |\n"
        )

    # 写入报告
    report_path = WORK_DIR / "origin_url-审计修复报告.md"
    with open(report_path, "w", encoding="utf-8") as f:
        f.writelines(report_lines)

    print(f"✅ 报告已生成: {report_path}")
    print(f"\n📊 统计:")
    print(f"   正确: {len(ok_files)}")
    print(f"   有问题: {len(fixed_files)}")


if __name__ == "__main__":
    main()
