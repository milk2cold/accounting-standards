#!/usr/bin/env python3
import json
import re
from pathlib import Path

WORK_DIR = Path(
    "/Users/milkcold/Downloads/MC2026/30 Project/38 会计准则知识库/docs/01-企业会计准则"
)


def main():
    print("📋 会计准则文件 Frontmatter 验证报告\n")
    print("=" * 80)
    print()

    # 1. 检查所有 md 文件
    md_files = list(WORK_DIR.glob("*.md"))
    md_files = [
        f
        for f in md_files
        if f.name not in ("index.md", "analysis-report.md", "SOP.md")
    ]
    md_files.sort()

    all_good = True
    report_lines = []
    report_lines.append("# 企业会计准则文件 Frontmatter 验证报告\n")
    report_lines.append(
        f"> 生成时间: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    )
    report_lines.append("\n---\n")
    report_lines.append("## 文件清单\n")
    report_lines.append("\n| 序号 | 文件名 | 标题 | 状态 | 原始链接 |\n")
    report_lines.append("|------|--------|------|------|----------|\n")

    for idx, md_file in enumerate(md_files, 1):
        with open(md_file, "r", encoding="utf-8") as f:
            content = f.read()

        status = "✅"
        origin_url = "-"
        title = md_file.stem

        # 解析 frontmatter
        if content.startswith("---\n"):
            end = content.find("\n---\n", 4)
            if end != -1:
                frontmatter = content[4:end]

                # 提取 title
                title_match = re.search(r'title:\s*"([^"]+)"', frontmatter)
                if title_match:
                    title = title_match.group(1)

                # 提取 origin_url
                url_match = re.search(r'origin_url:\s*"([^"]+)"', frontmatter)
                if url_match:
                    origin_url = url_match.group(1)
                else:
                    status = "❌"
                    all_good = False

                # 提取 status
                status_match = re.search(r'status:\s*"([^"]+)"', frontmatter)
                doc_status = status_match.group(1) if status_match else "未知"
        else:
            status = "❌"
            all_good = False

        # 生成表格行
        url_display = f"[链接]({origin_url})" if origin_url != "-" else "-"
        report_lines.append(
            f"| {idx} | [{md_file.name}]({md_file.name}) | {title} | {status} {doc_status} | {url_display} |\n"
        )

    # 统计信息
    report_lines.append("\n---\n")
    report_lines.append("## 统计信息\n")
    report_lines.append(f"\n- **总文件数**: {len(md_files)}\n")

    # 最终检查
    print()
    print("=" * 80)
    if all_good:
        print("✅ 所有文件检查通过！")
    else:
        print("⚠️  部分文件存在问题，请查看上方详细信息")

    # 写入报告
    report_path = WORK_DIR / "frontmatter-验证报告.md"
    with open(report_path, "w", encoding="utf-8") as f:
        f.writelines(report_lines)

    print(f"\n📄 详细报告已保存到: {report_path}")


if __name__ == "__main__":
    main()
