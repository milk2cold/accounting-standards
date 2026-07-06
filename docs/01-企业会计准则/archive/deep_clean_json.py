#!/usr/bin/env python3
import json
import re
from pathlib import Path

WORK_DIR = Path(
    "/Users/milkcold/Downloads/MC2026/30 Project/38 会计准则知识库/docs/01-企业会计准则"
)


def deep_clean_content(text, title):
    """深度清洗准则内容"""
    if not text:
        return text

    # 1. 处理特殊空格
    text = text.replace("\u00a0", " ")
    text = text.replace("\u3000", " ")

    # 2. 识别准则正文起始位置 - 查找"第X章"或准则标题
    lines = text.split("\n")
    start_index = 0

    # 对于基本准则，跳过修改决定，找到真正的准则正文
    if "基本准则" in title:
        # 查找"企业会计准则——基本准则"这个标题作为正文开始
        for i, line in enumerate(lines):
            if (
                "企业会计准则——基本准则" in line
                and "修改" not in lines[max(0, i - 5) : i]
            ):
                start_index = i
                break
    else:
        # 对于其他准则，查找"第一章"或准则标题
        for i, line in enumerate(lines):
            if re.match(r"^第[一二三四五六七八九十]+章", line.strip()):
                start_index = i
                break
            # 或者查找准则标题
            if (
                title.replace("企业会计准则", "").strip() in line
                and i < len(lines) // 2
            ):
                start_index = i
                break

    if start_index > 0:
        text = "\n".join(lines[start_index:])

    # 3. 删除常见的网页无关内容
    patterns_to_remove = [
        r"^部长\s+[\u4e00-\u9fa5]+\s*$",
        r"^\d{4}年\d{1,2}月\d{1,2}日\s*$",
        r"^财政部关于修改",
        r"^《财政部关于修改",
        r"^本决定自发布之日起施行",
        r"^《企业会计准则.*》根据本决定作相应修改",
        r"^已经财政部部务会议审议通过",
        r"^现予公布",
        r"^为了适应我国企业和资本市场发展",
    ]

    lines = text.split("\n")
    cleaned_lines = []
    for line in lines:
        line_stripped = line.strip()
        if not line_stripped:
            cleaned_lines.append(line)
            continue

        # 检查是否匹配删除模式
        skip = False
        for pattern in patterns_to_remove:
            if re.match(pattern, line_stripped):
                skip = True
                break
        if skip:
            continue

        cleaned_lines.append(line)

    text = "\n".join(cleaned_lines)

    # 4. 优化空格
    text = re.sub(r"[ \t]+", " ", text)

    # 5. 优化段落格式
    lines = [line.strip() for line in text.split("\n")]
    result = []
    prev_empty = False
    for line in lines:
        if not line:
            if not prev_empty:
                result.append("")
                prev_empty = True
        else:
            result.append(line)
            prev_empty = False

    text = "\n".join(result)

    # 6. 删除开头和结尾的空行
    text = text.strip("\n")

    return text


def main():
    print("🚀 开始深度清洗 JSON 文件...\n")

    # 从备份文件读取（因为上一次已经清洗过）
    input_path = WORK_DIR / "企业会计准则_全文.json.backup"
    if not input_path.exists():
        input_path = WORK_DIR / "企业会计准则_全文.json"

    with open(input_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    print(f"📄 文件加载成功,共 {len(data['articles'])} 篇准则\n")

    # 清洗每篇文章
    cleaned_articles = []
    total_before = 0
    total_after = 0

    for article in data["articles"]:
        title = article["title"]
        if "content" in article:
            original_len = len(article["content"])
            total_before += original_len

            article["content"] = deep_clean_content(article["content"], title)

            cleaned_len = len(article["content"])
            total_after += cleaned_len

            if original_len != cleaned_len:
                print(f"✓ 深度清洗: {title} (字符数: {original_len} → {cleaned_len})")

        cleaned_articles.append(article)

    # 更新数据
    data["articles"] = cleaned_articles

    print(f"\n📊 总体统计:")
    print(f"  - 总字符数(清洗前): {total_before:,}")
    print(f"  - 总字符数(清洗后): {total_after:,}")
    print(f"  - 减少字符数: {total_before - total_after:,}")

    # 保存最终清洗后的文件
    output_path = WORK_DIR / "企业会计准则_全文.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"\n✅ 深度清洗完成! 文件已保存到: {output_path}")


if __name__ == "__main__":
    main()
