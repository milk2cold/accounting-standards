#!/usr/bin/env python3
import json
import re
from pathlib import Path

WORK_DIR = Path(
    "/Users/milkcold/Downloads/MC2026/30 Project/38 会计准则知识库/docs/01-企业会计准则"
)


def clean_content(text):
    """清洗内容: 删除无效格式和重复"""
    if not text:
        return text

    # 删除网页导航信息 (如 "2026年03月06日  星期五\n\n当前位置：首页>...")
    text = re.sub(
        r"^\d{4}年\d{2}月\d{2}日\s*[\u4e00-\u9fa5]+\s*\n\n当前位置[^\n]*\n\n", "", text
    )

    # 处理特殊空格 (全角空格、不间断空格等)
    text = text.replace("\u00a0", " ")  # 不间断空格
    text = text.replace("\u3000", " ")  # 全角空格

    # 合并多余的空格 (但保留段落换行)
    text = re.sub(r"[ \t]+", " ", text)

    # 处理段落间的空行 - 保留2个换行作为段落分隔
    # 先统一换行符
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    # 删除行首行尾空格
    lines = [line.strip() for line in text.split("\n")]

    # 重新组合,段落之间保留一个空行
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

    # 删除开头和结尾的空行
    text = text.strip("\n")

    return text


def main():
    print("🚀 开始清洗 JSON 文件...\n")

    # 读取原始文件
    input_path = WORK_DIR / "企业会计准则_全文.json"
    with open(input_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    print(f"📄 原始文件加载成功,共 {len(data['articles'])} 篇准则\n")

    # 备份原始文件
    backup_path = WORK_DIR / "企业会计准则_全文.json.backup"
    with open(backup_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"💾 原始文件已备份到: {backup_path}\n")

    # 清洗每篇文章的 content
    seen_titles = set()
    cleaned_articles = []
    duplicates_removed = 0

    for article in data["articles"]:
        # 检查重复 (通过标题)
        title = article["title"]
        if title in seen_titles:
            duplicates_removed += 1
            print(f"⚠️  发现重复,跳过: {title}")
            continue
        seen_titles.add(title)

        # 清洗内容
        if "content" in article:
            original_len = len(article["content"])
            article["content"] = clean_content(article["content"])
            cleaned_len = len(article["content"])
            if original_len != cleaned_len:
                print(f"✓ 清洗: {title} (字符数: {original_len} → {cleaned_len})")

        cleaned_articles.append(article)

    # 更新数据
    data["articles"] = cleaned_articles
    data["total_count"] = len(cleaned_articles)

    print(f"\n📊 清洗统计:")
    print(f"  - 原始文章数: {len(seen_titles) + duplicates_removed}")
    print(f"  - 删除重复: {duplicates_removed}")
    print(f"  - 最终文章数: {len(cleaned_articles)}")

    # 保存清洗后的文件
    output_path = WORK_DIR / "企业会计准则_全文.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"\n✅ 清洗完成! 文件已保存到: {output_path}")


if __name__ == "__main__":
    main()
