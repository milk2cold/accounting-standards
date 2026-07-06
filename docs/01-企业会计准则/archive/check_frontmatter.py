#!/usr/bin/env python3
import json
import re
from pathlib import Path

WORK_DIR = Path(
    "/Users/milkcold/Downloads/MC2026/30 Project/38 会计准则知识库/docs/01-企业会计准则"
)


def main():
    print("🚀 开始检查并更新 md 文件的 frontmatter...\n")

    # 1. 读取 JSON 数据源，建立标题到 URL 的映射
    json_path = WORK_DIR / "企业会计准则_全文.json"
    with open(json_path, "r", encoding="utf-8") as f:
        json_data = json.load(f)

    title_to_url = {}
    for article in json_data["articles"]:
        title = article["title"]
        url = article["url"]
        title_to_url[title] = url
        # 也建立简化标题映射
        simple_title = re.sub(r"（财会〔\d{4}〕\d+号）", "", title)
        simple_title = re.sub(r"（\d{4}版）", "", simple_title)
        title_to_url[simple_title] = url

    print(f"📄 从 JSON 加载了 {len(title_to_url)} 个标题-URL 映射\n")

    # 2. 检查所有 md 文件
    md_files = list(WORK_DIR.glob("*.md"))
    md_files = [
        f
        for f in md_files
        if f.name not in ("index.md", "analysis-report.md", "SOP.md")
    ]

    print(f"📝 找到 {len(md_files)} 个 Markdown 文件\n")

    missing_url = []
    has_url = []

    for md_file in md_files:
        with open(md_file, "r", encoding="utf-8") as f:
            content = f.read()

        # 解析 frontmatter
        if content.startswith("---\n"):
            end = content.find("\n---\n", 4)
            if end != -1:
                frontmatter = content[4:end]
                body = content[end + 5 :]

                # 检查是否有 origin_url
                has_origin_url = "origin_url:" in frontmatter

                # 提取 title
                title_match = re.search(r'title:\s*"([^"]+)"', frontmatter)
                if title_match:
                    title = title_match.group(1)
                else:
                    title = md_file.stem

                if has_origin_url:
                    has_url.append((md_file.name, title))
                else:
                    missing_url.append(
                        (md_file.name, title, frontmatter, body, md_file)
                    )

    print(f"✅ 已有 origin_url: {len(has_url)} 个文件")
    print(f"❌ 缺少 origin_url: {len(missing_url)} 个文件\n")

    if not missing_url:
        print("🎉 所有文件都已有 origin_url！")
        return

    # 3. 为缺少的文件添加 origin_url
    updated_count = 0
    for filename, title, frontmatter, body, filepath in missing_url:
        print(f"🔄 处理: {filename}")
        print(f"   标题: {title}")

        # 尝试匹配 URL
        matched_url = None
        # 精确匹配
        if title in title_to_url:
            matched_url = title_to_url[title]
        else:
            # 模糊匹配
            for json_title, url in title_to_url.items():
                if title in json_title or json_title in title:
                    matched_url = url
                    break

        if matched_url:
            print(f"   ✅ 找到 URL: {matched_url}")

            # 添加 origin_url 到 frontmatter
            # 找到合适的位置插入（通常在 tags 或 related 之后）
            if "related:" in frontmatter:
                # 在 related 块之后添加
                lines = frontmatter.split("\n")
                insert_idx = None
                in_related = False
                for i, line in enumerate(lines):
                    if line.strip().startswith("related:"):
                        in_related = True
                    elif (
                        in_related and line.strip() and not line.strip().startswith("-")
                    ):
                        insert_idx = i
                        break
                    elif in_related and i == len(lines) - 1:
                        insert_idx = i + 1
                        break

                if insert_idx is not None:
                    lines.insert(insert_idx, f'origin_url: "{matched_url}"')
                else:
                    lines.append(f'origin_url: "{matched_url}"')

                new_frontmatter = "\n".join(lines)
            else:
                # 在末尾添加
                new_frontmatter = (
                    frontmatter.rstrip() + f'\norigin_url: "{matched_url}"'
                )

            # 写回文件
            new_content = f"---\n{new_frontmatter}\n---\n{body}"
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(new_content)

            updated_count += 1
            print(f"   ✅ 文件已更新\n")
        else:
            print(f"   ❌ 未找到匹配的 URL\n")

    print(f"\n🎉 完成! 共更新了 {updated_count}/{len(missing_url)} 个文件")


if __name__ == "__main__":
    main()
