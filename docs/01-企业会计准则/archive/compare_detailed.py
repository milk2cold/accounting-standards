#!/usr/bin/env python3
import json
import re
from pathlib import Path

WORK_DIR = Path(
    "/Users/milkcold/Downloads/MC2026/30 Project/38 会计准则知识库/docs/01-企业会计准则"
)


def clean_text(text):
    """清理文本用于比较"""
    if not text:
        return ""
    if not isinstance(text, str):
        text = str(text)
    text = re.sub(r"\s+", " ", text)
    text = text.replace("（", "(").replace("）", ")")
    text = text.replace("「", '"').replace("」", '"')
    text = text.replace("『", '"').replace("』", '"')
    return text.strip()
    """清理文本用于比较"""
    if not text:
        return ""
    text = re.sub(r"\s+", " ", text)
    text = text.replace("（", "(").replace("）", ")")
    text = text.replace("「", '"').replace("」", '"')
    text = text.replace("『", '"').replace("』", '"')
    return text.strip()


def extract_md_body(content):
    """从md文件中提取正文"""
    if not content.startswith("---\n"):
        return content

    end = content.find("\n---\n", 4)
    if end == -1:
        return content

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

    return "\n".join(body_lines)


def main():
    print("🔍 开始详细比较 md 文件、JSON 文件和 origin_url...\n")
    print("=" * 80)
    print()

    # 读取 JSON 数据
    json_path = WORK_DIR / "企业会计准则_全文.json"
    with open(json_path, "r", encoding="utf-8") as f:
        json_data = json.load(f)

    # 建立 JSON 映射
    json_map = {}
    for article in json_data["articles"]:
        title = article["title"]
        url = article["url"]
        content = article.get("content", "")
        json_map[title] = (url, content)
        json_map[url] = content  # 也按 URL 索引

    print(f"📄 从 JSON 加载了 {len(json_map)} 个条目\n")

    # 需要检查的文件
    warning_files = [
        (
            "09-职工薪酬-2006.md",
            "企业会计准则第9号——职工薪酬",
            "https://www.casc.org.cn/2018/0815/202805.shtml",
        ),
        (
            "12-债务重组-2006.md",
            "企业会计准则第12号——债务重组",
            "https://www.casc.org.cn/2018/0815/202801.shtml",
        ),
        (
            "12-债务重组-2019.md",
            "企业会计准则第12号——债务重组",
            "https://www.casc.org.cn/2018/0815/202802.shtml",
        ),
        (
            "21-租赁-2006.md",
            "企业会计准则第21号——租赁",
            "https://law.esnai.com/do.aspx?action=show&controller=home&lawid=22783",
        ),
        (
            "22-金融工具确认和计量-2006.md",
            "企业会计准则第22号——金融工具确认和计量",
            "https://zh.m.wikisource.org/wiki/《企业会计准则第22号——金融工具确认和计量》(2006年)",
        ),
        (
            "22-金融工具确认和计量-2017.md",
            "企业会计准则第22号——金融工具确认和计量",
            "https://www.casc.org.cn/2017/0331/202671.shtml",
        ),
        (
            "23-金融资产转移-2017.md",
            "企业会计准则第23号——金融资产转移",
            "https://www.casc.org.cn/2017/0331/202673.shtml",
        ),
        (
            "24-套期会计-2017.md",
            "企业会计准则第24号——套期会计",
            "https://www.casc.org.cn/2017/0331/202674.shtml",
        ),
        (
            "25-保险合同-2020.md",
            "企业会计准则第25号——保险合同",
            "http://kjs.mof.gov.cn/zt/kjzzss/kuaijizhunzeshishi/202012/t20201224_3640041.htm",
        ),
        (
            "32-中期财务报告.md",
            "企业会计准则第32号——中期财务报告",
            "https://kjs.mof.gov.cn/zt/kjzzss/kuaijizhunzeshishi/200806/t20080618_46249.htm",
        ),
        (
            "33-合并财务报表-2006.md",
            "企业会计准则第33号——合并财务报表",
            "http://kjs.mof.gov.cn/zt/kjzzss/kuaijizhunzeshishi/200806/t20080618_46248.htm",
        ),
        (
            "33-合并财务报表.md",
            "企业会计准则第33号——合并财务报表",
            "https://kjs.mof.gov.cn/zt/kjzzss/kuaijizhunzeshishi/200806/t20080618_46248.htm",
        ),
        (
            "34-每股收益.md",
            "企业会计准则第34号——每股收益",
            "https://kjs.mof.gov.cn/zt/kjzzss/kuaijizhunzeshishi/200806/t20080618_46247.htm",
        ),
        (
            "35-分部报告.md",
            "企业会计准则第35号——分部报告",
            "https://kjs.mof.gov.cn/zt/kjzzss/kuaijizhunzeshishi/200806/t20080618_46246.htm",
        ),
        (
            "37-金融工具列报-2006.md",
            "企业会计准则第37号——金融工具列报",
            "https://kjs.mof.gov.cn/zt/kjzzss/kuaijizhunzeshishi/201709/t20170907_2694118.htm",
        ),
        (
            "37-金融工具列报-2017.md",
            "企业会计准则第37号——金融工具列报",
            "https://www.casc.org.cn/2017/0331/202675.shtml",
        ),
    ]

    results = []

    for md_name, json_title_keyword, origin_url in warning_files:
        md_file = WORK_DIR / md_name
        if not md_file.exists():
            continue

        print(f"📄 检查: {md_name}")

        with open(md_file, "r", encoding="utf-8") as f:
            md_content = f.read()

        # 提取 md 正文
        md_body = extract_md_body(md_content)

        # 在 JSON 中查找匹配的内容
        json_content = None
        matched_key = None

        # 先按 URL 精确匹配
        if origin_url in json_map:
            json_content = json_map[origin_url]
            matched_key = origin_url
        else:
            # 模糊匹配标题
            for key, content in json_map.items():
                if json_title_keyword in key:
                    json_content = content
                    matched_key = key
                    break

        # 计算相似度
        md_vs_json = 0
        if json_content:
            md_clean = clean_text(md_body[:1000])
            json_clean = clean_text(json_content[:1000])
            if md_clean and json_clean:
                from difflib import SequenceMatcher

                md_vs_json = SequenceMatcher(None, md_clean, json_clean).ratio()

        results.append(
            {
                "file": md_name,
                "origin_url": origin_url,
                "md_length": len(md_body),
                "json_length": len(json_content) if json_content else 0,
                "md_vs_json": md_vs_json,
                "matched_json_key": matched_key,
                "has_json_match": json_content is not None,
            }
        )

        print(f"   MD 正文长度: {len(md_body)}")
        print(f"   JSON 匹配长度: {len(json_content) if json_content else 0}")
        print(f"   MD vs JSON 相似度: {md_vs_json:.2%}")
        print(f"   JSON 匹配键: {matched_key}")
        print()

    # 总结
    print("=" * 80)
    print("\n📊 总结:")
    for r in results:
        status = "✅" if r["md_vs_json"] > 0.3 else "⚠️"
        print(f"   {status} {r['file']}: 相似度 {r['md_vs_json']:.2%}")


if __name__ == "__main__":
    main()
