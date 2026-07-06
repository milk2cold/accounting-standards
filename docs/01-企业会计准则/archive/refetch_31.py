#!/usr/bin/env python3
import json
import re
import requests
from pathlib import Path
from bs4 import BeautifulSoup
import time

WORK_DIR = Path(
    "/Users/milkcold/Downloads/MC2026/30 Project/38 会计准则知识库/docs/01-企业会计准则"
)


def fetch_content(url):
    """从URL抓取内容"""
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.encoding = "utf-8"

        if response.status_code != 200:
            print(f"  ❌ HTTP {response.status_code}")
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
                # 移除script和style
                for s in body(["script", "style", "nav", "header", "footer"]):
                    s.decompose()
                content = body.get_text("\n", strip=True)

        # 清理内容
        if content:
            # 移除多余空行
            lines = [line.strip() for line in content.split("\n")]
            cleaned_lines = []
            prev_empty = False
            for line in lines:
                if not line:
                    if not prev_empty:
                        cleaned_lines.append("")
                        prev_empty = True
                else:
                    cleaned_lines.append(line)
                    prev_empty = False
            content = "\n".join(cleaned_lines).strip("\n")

        return content

    except Exception as e:
        print(f"  ❌ 错误: {e}")
        return None


def main():
    print("🔄 重新抓取第31号现金流量表...\n")

    json_path = WORK_DIR / "企业会计准则_全文.json"
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # 找到第31号
    for i, article in enumerate(data["articles"]):
        title = article["title"]
        if "第31号" in title and "现金流量表" in title:
            url = article["url"]
            print(f"正在抓取: {title}")
            print(f"URL: {url}")

            new_content = fetch_content(url)

            if new_content and len(new_content) > 500:
                data["articles"][i]["content"] = new_content
                print(f"✅ 成功! (字符数: {len(new_content)})")
                break
            else:
                print(f"❌ 抓取失败或内容过少")

    # 保存更新后的JSON
    output_path = WORK_DIR / "企业会计准则_全文.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"\n📄 文件已保存到: {output_path}")


if __name__ == "__main__":
    main()
