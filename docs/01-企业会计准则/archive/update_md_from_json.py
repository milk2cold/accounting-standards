#!/usr/bin/env python3
import json
import re
from pathlib import Path

WORK_DIR = Path(
    "/Users/milkcold/Downloads/MC2026/30 Project/38 会计准则知识库/docs/01-企业会计准则"
)


def main():
    print("🔄 用 JSON 完整内容更新 md 文件...")
    print("=" * 80)

    # 读取 JSON 数据
    with open(WORK_DIR / "企业会计准则_全文.json", "r", encoding="utf-8") as f:
        json_data = json.load(f)

    # 建立 URL -> content 映射
    url_to_content = {}
    for article in json_data["articles"]:
        url = article["url"]
        content = article.get("content", "")
        if url and content:
            url_to_content[url] = content

    print(f"\n📄 从 JSON 加载了 {len(url_to_content)} 个完整内容\n")

    # 需要更新的文件
    updates = [
        (
            "32-中期财务报告.md",
            "https://kjs.mof.gov.cn/zt/kjzzss/kuaijizhunzeshishi/200806/t20080618_46249.htm",
        ),
        (
            "33-合并财务报表.md",
            "https://kjs.mof.gov.cn/zt/kjzzss/kuaijizhunzeshishi/200806/t20080618_46248.htm",
        ),
        (
            "34-每股收益.md",
            "https://kjs.mof.gov.cn/zt/kjzzss/kuaijizhunzeshishi/200806/t20080618_46247.htm",
        ),
        (
            "35-分部报告.md",
            "https://kjs.mof.gov.cn/zt/kjzzss/kuaijizhunzeshishi/200806/t20080618_46246.htm",
        ),
        (
            "37-金融工具列报-2006.md",
            "https://kjs.mof.gov.cn/zt/kjzzss/kuaijizhunzeshishi/201709/t20170907_2694118.htm",
        ),
    ]

    updated = 0

    for md_name, url in updates:
        md_path = WORK_DIR / md_name
        if not md_path.exists():
            print(f"❌ 文件不存在: {md_name}")
            continue

        json_content = url_to_content.get(url)
        if not json_content:
            print(f"❌ JSON 未找到: {md_name}")
            continue

        # 读取原文件保留 frontmatter
        with open(md_path, "r", encoding="utf-8") as f:
            md_content = f.read()

        # 提取 frontmatter
        frontmatter = ""
        if md_content.startswith("---\n"):
            end = md_content.find("\n---\n", 4)
            if end != -1:
                frontmatter = md_content[4:end]

        if not frontmatter:
            print(f"❌ 无法解析 frontmatter: {md_name}")
            continue

        # 查找第一章位置
        lines = json_content.split("\n")
        first_chapter = 0
        for i, line in enumerate(lines):
            if "第一章" in line:
                first_chapter = i
                break

        body = "\n".join(lines[first_chapter:])

        # 写回新内容
        new_content = f"---\n{frontmatter}\n---\n\n{body}\n"
        with open(md_path, "w", encoding="utf-8") as f:
            f.write(new_content)

        print(f"✅ 已更新: {md_name} ({len(json_content)} 字符)")
        updated += 1

    print(f"\n{'=' * 80}")
    print(f"🎉 完成! 共更新 {updated}/{len(updates)} 个文件")


if __name__ == "__main__":
    main()
