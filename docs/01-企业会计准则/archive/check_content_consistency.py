#!/usr/bin/env python3
import json
import re
import requests
from pathlib import Path
from difflib import SequenceMatcher
from bs4 import BeautifulSoup
import time

WORK_DIR = Path(
    "/Users/milkcold/Downloads/MC2026/30 Project/38 会计准则知识库/docs/01-企业会计准则"
)


def clean_text(text):
    """清理文本用于比较"""
    if not text:
        return ""
    # 移除空白字符
    text = re.sub(r"\s+", " ", text)
    # 移除常见的标点差异
    text = text.replace("（", "(").replace("）", ")")
    text = text.replace("「", '"').replace("」", '"')
    text = text.replace("『", '"').replace("』", '"')
    return text.strip()


def content_similarity(content1, content2):
    """计算两个内容的相似度"""
    if not content1 or not content2:
        return 0
    clean1 = clean_text(content1)
    clean2 = clean_text(content2)
    if not clean1 or not clean2:
        return 0
    # 比较前2000个字符
    return SequenceMatcher(None, clean1[:2000], clean2[:2000]).ratio()


def extract_md_body(content):
    """从md文件中提取正文内容（去掉frontmatter和标题）"""
    if not content.startswith("---\n"):
        return content

    end = content.find("\n---\n", 4)
    if end == -1:
        return content

    body = content[end + 5 :]

    # 移除一级标题
    lines = body.split("\n")
    body_lines = []
    in_body = False
    for line in lines:
        if line.startswith("# ") and not in_body:
            continue
        # 跳过空行直到找到正文
        if not in_body and line.strip():
            in_body = True
        if in_body:
            body_lines.append(line)

    return "\n".join(body_lines)


def fetch_url_content(url):
    """从URL获取内容"""
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.encoding = "utf-8"

        if response.status_code != 200:
            return None

        soup = BeautifulSoup(response.text, "html.parser")

        # 尝试多个可能的内容容器
        content_selectors = [
            "#zoom",
            ".TRS_Editor",
            "div[class*='content']",
            "div[class*='main']",
            "article",
            ".content",
        ]

        content = None
        for selector in content_selectors:
            element = soup.select_one(selector)
            if element:
                content = element.get_text("\n", strip=True)
                if len(content) > 200:
                    break

        # 如果没有找到，尝试获取body内的主要文本
        if not content or len(content) < 200:
            body = soup.find("body")
            if body:
                for s in body(["script", "style", "nav", "header", "footer"]):
                    s.decompose()
                content = body.get_text("\n", strip=True)

        return content

    except Exception as e:
        print(f"      获取URL内容失败: {e}")
        return None


def main():
    print("🔍 开始检查准则正文与 origin_url 内容的一致性...\n")
    print("=" * 80)
    print()

    # 1. 读取 JSON 数据源作为参考
    json_path = WORK_DIR / "企业会计准则_全文.json"
    with open(json_path, "r", encoding="utf-8") as f:
        json_data = json.load(f)

    # 建立标题到 JSON 内容的映射
    json_map = {}
    for article in json_data["articles"]:
        title = article["title"]
        url = article["url"]
        content = article.get("content", "")
        json_map[title] = (url, content)

        # 简化标题也加入
        simple_title = re.sub(r"（财会〔\d{4}〕\d+号）", "", title)
        simple_title = re.sub(r"（\d{4}版）", "", simple_title)
        if simple_title not in json_map:
            json_map[simple_title] = (url, content)

    print(f"📄 从 JSON 加载了 {len(json_map)} 个参考内容\n")

    # 2. 检查所有 md 文件
    md_files = list(WORK_DIR.glob("*.md"))
    md_files = [
        f
        for f in md_files
        if f.name
        not in (
            "index.md",
            "analysis-report.md",
            "SOP.md",
            "frontmatter-验证报告.md",
            "origin_url-审计修复报告.md",
        )
    ]
    md_files.sort()

    results = []

    for idx, md_file in enumerate(md_files, 1):
        print(f"[{idx}/{len(md_files)}] 检查: {md_file.name}")

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

        if not title_match:
            continue

        title = title_match.group(1)
        origin_url = url_match.group(1) if url_match else None

        # 提取 md 正文
        md_body = extract_md_body(content)

        # 查找匹配的 JSON 参考内容
        json_content = None
        matched_title = None

        if title in json_map:
            _, json_content = json_map[title]
            matched_title = title
        else:
            for json_title, (_, jc) in json_map.items():
                if title in json_title or json_title in title:
                    json_content = jc
                    matched_title = json_title
                    break

        # 计算相似度
        similarity = 0
        has_json_match = False
        if json_content:
            similarity = content_similarity(md_body, json_content)
            has_json_match = True

        # 判断结果
        status = "✅"
        issue = ""

        if not origin_url:
            status = "❌"
            issue = "缺少 origin_url"
        elif similarity < 0.3 and has_json_match:
            status = "⚠️"
            issue = f"内容相似度较低 ({similarity:.2f})"
        elif len(md_body.strip()) < 200:
            status = "❌"
            issue = "正文内容过短"

        results.append(
            {
                "file": md_file.name,
                "title": title,
                "origin_url": origin_url,
                "similarity": similarity,
                "has_json_match": has_json_match,
                "status": status,
                "issue": issue,
                "md_body_length": len(md_body.strip()),
            }
        )

        print(f"      状态: {status}")
        if issue:
            print(f"      问题: {issue}")
        if has_json_match:
            print(f"      与JSON参考相似度: {similarity:.2%}")
        print()

    # 生成报告
    print("=" * 80)
    print("\n📊 检查总结:")
    print(f"   检查文件数: {len(results)}")
    print(f"   ✅ 正常: {len([r for r in results if r['status'] == '✅'])}")
    print(f"   ⚠️  警告: {len([r for r in results if r['status'] == '⚠️'])}")
    print(f"   ❌ 错误: {len([r for r in results if r['status'] == '❌'])}")

    # 写入详细报告
    report_lines = []
    report_lines.append("# 企业会计准则内容一致性检查报告\n")
    report_lines.append(
        f"> 生成时间: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    )
    report_lines.append("\n---\n")
    report_lines.append("## 检查摘要\n")
    report_lines.append(f"\n- **检查文件数**: {len(results)}\n")
    report_lines.append(
        f"- **✅ 正常**: {len([r for r in results if r['status'] == '✅'])}\n"
    )
    report_lines.append(
        f"- **⚠️  警告**: {len([r for r in results if r['status'] == '⚠️'])}\n"
    )
    report_lines.append(
        f"- **❌ 错误**: {len([r for r in results if r['status'] == '❌'])}\n"
    )

    report_lines.append("\n---\n")
    report_lines.append("## 详细结果\n")
    report_lines.append("\n| 状态 | 文件名 | 标题 | 相似度 | 说明 |\n")
    report_lines.append("|------|--------|------|--------|------|\n")

    for r in results:
        url_display = f"[链接]({r['origin_url']})" if r["origin_url"] else "-"
        sim_display = f"{r['similarity']:.2%}" if r["has_json_match"] else "-"
        report_lines.append(
            f"| {r['status']} | [{r['file']}]({r['file']}) | {r['title']} | {sim_display} | {r['issue'] or '-'} |\n"
        )

    report_path = WORK_DIR / "内容一致性检查报告.md"
    with open(report_path, "w", encoding="utf-8") as f:
        f.writelines(report_lines)

    print(f"\n✅ 详细报告已生成: {report_path}")


if __name__ == "__main__":
    main()
