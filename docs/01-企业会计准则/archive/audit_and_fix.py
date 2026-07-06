#!/usr/bin/env python3
import json
import re
from pathlib import Path
from difflib import SequenceMatcher

WORK_DIR = Path(
    "/Users/milkcold/Downloads/MC2026/30 Project/38 会计准则知识库/docs/01-企业会计准则"
)


def content_similarity(content1, content2):
    """计算两个内容的相似度"""
    if not content1 or not content2:
        return 0
    return SequenceMatcher(None, content1[:500], content2[:500]).ratio()


def main():
    print("🚀 开始全面检查和修复 md 文件的 origin_url...\n")
    print("=" * 80)
    print()

    # 1. 读取 JSON 数据源
    json_path = WORK_DIR / "企业会计准则_全文.json"
    with open(json_path, "r", encoding="utf-8") as f:
        json_data = json.load(f)

    # 建立标题到 (url, content) 的映射
    json_map = {}
    for article in json_data["articles"]:
        title = article["title"]
        url = article["url"]
        content = article.get("content", "")
        json_map[title] = (url, content)

        # 简化标题也加入映射
        simple_title = re.sub(r"（财会〔\d{4}〕\d+号）", "", title)
        simple_title = re.sub(r"（\d{4}版）", "", simple_title)
        if simple_title not in json_map:
            json_map[simple_title] = (url, content)

    print(f"📄 从 JSON 加载了 {len(json_map)} 个标题映射\n")

    # 2. 检查所有 md 文件
    md_files = list(WORK_DIR.glob("*.md"))
    md_files = [
        f
        for f in md_files
        if f.name
        not in ("index.md", "analysis-report.md", "SOP.md", "frontmatter-验证报告.md")
    ]
    md_files.sort()

    issues_found = []
    fixed_count = 0

    for md_file in md_files:
        with open(md_file, "r", encoding="utf-8") as f:
            content = f.read()

        # 解析 frontmatter
        if not content.startswith("---\n"):
            continue

        end = content.find("\n---\n", 4)
        if end == -1:
            continue

        frontmatter = content[4:end]
        body = content[end + 5 :]

        # 提取信息
        title_match = re.search(r'title:\s*"([^"]+)"', frontmatter)
        current_url_match = re.search(r'origin_url:\s*"([^"]+)"', frontmatter)

        if not title_match:
            continue

        title = title_match.group(1)
        current_url = current_url_match.group(1) if current_url_match else None

        # 问题1: 检查是否是错误的通用链接
        bad_generic_url = False
        if (
            current_url
            and current_url.rstrip("/")
            == "http://kjs.mof.gov.cn/zt/kjzzss/kuaijizhunzeshishi"
        ):
            bad_generic_url = True
            issues_found.append(
                {
                    "type": "generic_url",
                    "file": md_file.name,
                    "title": title,
                    "current_url": current_url,
                }
            )

        # 问题2: 查找匹配的 JSON 条目
        matched_json = None
        matched_url = None
        matched_json_content = None

        # 精确匹配
        if title in json_map:
            matched_url, matched_json_content = json_map[title]
            matched_json = title
        else:
            # 模糊匹配
            for json_title, (url, json_content) in json_map.items():
                if title in json_title or json_title in title:
                    matched_url = url
                    matched_json_content = json_content
                    matched_json = json_title
                    break

        # 问题3: 内容相似度检查
        content_match_ok = True
        if matched_json_content:
            # 提取 md 文件正文内容（去掉 frontmatter）
            md_body_clean = re.sub(r"^#.*$", "", body, flags=re.MULTILINE).strip()
            md_body_clean = re.sub(
                r"^##.*$", "", md_body_clean, flags=re.MULTILINE
            ).strip()

            similarity = content_similarity(md_body_clean, matched_json_content)

            if similarity < 0.3:
                content_match_ok = False
                issues_found.append(
                    {
                        "type": "content_mismatch",
                        "file": md_file.name,
                        "title": title,
                        "current_url": current_url,
                        "matched_json": matched_json,
                        "matched_url": matched_url,
                        "similarity": similarity,
                    }
                )

        # 修复问题
        needs_fix = False
        new_url = current_url

        if bad_generic_url and matched_url:
            new_url = matched_url
            needs_fix = True
            print(f"❌ {md_file.name}: 发现错误的通用链接")
            print(f"   标题: {title}")
            print(f"   当前: {current_url}")
            print(f"   更正: {matched_url}")
            print()

        elif not current_url and matched_url:
            new_url = matched_url
            needs_fix = True
            print(f"⚠️  {md_file.name}: 缺少 origin_url")
            print(f"   标题: {title}")
            print(f"   添加: {matched_url}")
            print()

        # 执行修复
        if needs_fix:
            # 更新 frontmatter
            if current_url:
                new_frontmatter = frontmatter.replace(
                    f'origin_url: "{current_url}"', f'origin_url: "{new_url}"'
                )
            else:
                # 在合适的位置添加 origin_url
                if "related:" in frontmatter:
                    lines = frontmatter.split("\n")
                    insert_idx = None
                    in_related = False
                    for i, line in enumerate(lines):
                        if line.strip().startswith("related:"):
                            in_related = True
                        elif (
                            in_related
                            and line.strip()
                            and not line.strip().startswith("-")
                        ):
                            insert_idx = i
                            break
                        elif in_related and i == len(lines) - 1:
                            insert_idx = i + 1
                            break

                    if insert_idx is not None:
                        lines.insert(insert_idx, f'origin_url: "{new_url}"')
                    else:
                        lines.append(f'origin_url: "{new_url}"')

                    new_frontmatter = "\n".join(lines)
                else:
                    new_frontmatter = (
                        frontmatter.rstrip() + f'\norigin_url: "{new_url}"'
                    )

            # 写回文件
            new_content = f"---\n{new_frontmatter}\n---\n{body}"
            with open(md_file, "w", encoding="utf-8") as f:
                f.write(new_content)

            fixed_count += 1

    # 总结
    print("=" * 80)
    print(f"\n📊 检查总结:")
    print(f"   检查文件数: {len(md_files)}")
    print(f"   发现问题数: {len(issues_found)}")
    print(f"   已修复数: {fixed_count}")

    if issues_found:
        print(f"\n📋 问题详情:")
        for i, issue in enumerate(issues_found, 1):
            if issue["type"] == "generic_url":
                print(f"   {i}. [{issue['file']}] 错误的通用链接")
            elif issue["type"] == "content_mismatch":
                print(
                    f"   {i}. [{issue['file']}] 内容可能不匹配 (相似度: {issue['similarity']:.2f})"
                )

    print("\n✅ 检查完成!")


if __name__ == "__main__":
    main()
