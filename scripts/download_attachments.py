import json
import urllib.request
import re
import os

# 定义有附件的解释
attachments_info = [
    {
        "title": "第19号",
        "url": "https://kjs.mof.gov.cn/zhengcefabu/202512/t20251218_3979556.htm",
        "date": "2025-12-19",
    },
    {
        "title": "第18号",
        "url": "https://kjs.mof.gov.cn/zhengcefabu/202412/t20241223_3950344.htm",
        "date": "2024-12-31",
    },
    {
        "title": "第17号",
        "url": "https://kjs.mof.gov.cn/zhengcefabu/202311/t20231109_3915491.htm",
        "date": "2023-11-09",
    },
    {
        "title": "第16号",
        "url": "https://kjs.mof.gov.cn/gongzuotongzhi/202212/t20221212_3857395.htm",
        "date": "2022-12-13",
    },
    {
        "title": "第15号",
        "url": "https://kjs.mof.gov.cn/zhengcefabu/202112/t20211231_3779983.htm",
        "date": "2021-12-31",
    },
    {
        "title": "第14号",
        "url": "https://kjs.mof.gov.cn/zhengcefabu/202102/t20210202_3653110.htm",
        "date": "2021-02-02",
    },
    {
        "title": "第13号",
        "url": "https://kjs.mof.gov.cn/zhengcefabu/201912/t20191213_3441493.htm",
        "date": "2019-12-16",
    },
    {
        "title": "第12号",
        "url": "https://kjs.mof.gov.cn/zhengcefabu/201706/t20170621_2628439.htm",
        "date": "2017-06-21",
    },
    {
        "title": "第11号",
        "url": "https://kjs.mof.gov.cn/zhengcefabu/201706/t20170621_2628437.htm",
        "date": "2017-06-21",
    },
    {
        "title": "第10号",
        "url": "https://kjs.mof.gov.cn/zhengcefabu/201706/t20170621_2628435.htm",
        "date": "2017-06-21",
    },
    {
        "title": "第9号",
        "url": "https://kjs.mof.gov.cn/zhengcefabu/201706/t20170621_2628433.htm",
        "date": "2017-06-21",
    },
]


def get_attachment_url(url):
    """从页面提取附件下载链接"""
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=15) as response:
            html = response.read().decode("utf-8")

        # 查找附件链接 - 更宽松的模式，匹配任何docx/pdf/doc文件
        patterns = [
            r'href="([^"]+\.pdf)"',
            r'href="([^"]+\.docx)"',
            r'href="([^"]+\.doc)"',
            r"href='([^']+\.pdf)'",
            r"href='([^']+\.docx)'",
            r"href='([^']+\.doc)'",
        ]

        for pattern in patterns:
            matches = re.findall(pattern, html, re.IGNORECASE)
            for match in matches:
                if not match:
                    continue
                # 补全URL
                if match.startswith("http"):
                    return match
                elif match.startswith("./"):
                    # 处理相对路径: ./P020170621605521628417.docx
                    return "https://kjs.mof.gov.cn" + match[1:]
                elif match.startswith("/"):
                    return "https://kjs.mof.gov.cn" + match
                else:
                    return "https://kjs.mof.gov.cn/" + match
        return None
    except Exception as e:
        print(f"Error getting attachment URL: {e}")
        return None
    """从页面提取附件下载链接"""
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=15) as response:
            html = response.read().decode("utf-8")

        # 查找附件链接 (PDF, DOCX, DOC)
        patterns = [
            r'<a[^>]+href=["\']([^"\']+\.pdf)["\']',
            r'<a[^>]+href=["\']([^"\']+\.docx)["\']',
            r'<a[^>]+href=["\']([^"\']+\.doc)["\']',
        ]

        for pattern in patterns:
            matches = re.findall(pattern, html, re.IGNORECASE)
            for match in matches:
                if "解释" in match:
                    # 补全URL
                    if match.startswith("http"):
                        return match
                    else:
                        return "https://kjs.mof.gov.cn" + match
        return None
    except Exception as e:
        print(f"Error getting attachment URL: {e}")
        return None


def download_file(url, filename):
    """下载文件"""
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=30) as response:
            data = response.read()
            with open(filename, "wb") as f:
                f.write(data)
        print(f"Downloaded: {filename}")
        return True
    except Exception as e:
        print(f"Error downloading {url}: {e}")
        return False


def extract_text(filename):
    """提取文件文本"""
    try:
        # 使用textutil转换
        import subprocess

        txt_file = (
            filename.replace(".pdf", ".txt")
            .replace(".docx", ".txt")
            .replace(".doc", ".txt")
        )

        if filename.endswith(".pdf"):
            # 尝试用pdftotext
            result = subprocess.run(
                ["pdftotext", filename, "-"], capture_output=True, text=True
            )
            if result.returncode == 0:
                return result.stdout
        elif filename.endswith(".docx"):
            # 使用zipfile解压word/document.xml
            import zipfile

            with zipfile.ZipFile(filename, "r") as z:
                with z.open("word/document.xml") as f:
                    content = f.read().decode("utf-8")
                    # 移除XML标签
                    text = re.sub(r"<[^>]+>", " ", content)
                    text = re.sub(r"\s+", " ", text)
                    return text
        elif filename.endswith(".doc"):
            # 使用textutil转换
            txt_file = filename + ".txt"
            result = subprocess.run(
                ["textutil", "-convert", "txt", "-output", txt_file, filename],
                capture_output=True,
                text=True,
            )
            if os.path.exists(txt_file):
                with open(txt_file, "r", encoding="utf-8") as f:
                    return f.read()

        return None
    except Exception as e:
        print(f"Error extracting text from {filename}: {e}")
        return None


# 获取所有附件URL
print("=" * 50)
print("Step 1: 获取附件下载链接")
print("=" * 50)

attachment_urls = {}
for item in attachments_info:
    title = item["title"]
    url = item["url"]
    attach_url = get_attachment_url(url)
    if attach_url:
        attachment_urls[title] = attach_url
        print(f"{title}: {attach_url}")
    else:
        print(f"{title}: 未找到附件")

print(f"\n共找到 {len(attachment_urls)} 个附件")

# 下载附件并提取内容
print("\n" + "=" * 50)
print("Step 2: 下载附件")
print("=" * 50)

attachments_content = {}
for title, url in attachment_urls.items():
    # 确定文件扩展名
    if ".pdf" in url:
        ext = ".pdf"
    elif ".docx" in url:
        ext = ".docx"
    elif ".doc" in url:
        ext = ".doc"
    else:
        ext = ".bin"

    filename = f"解释{title}{ext}"

    if download_file(url, filename):
        # 提取文本内容
        text = extract_text(filename)
        if text:
            attachments_content[title] = text
            print(f"  -> 提取成功: {len(text)} 字符")
        else:
            print(f"  -> 提取失败")
    else:
        print(f"  -> 下载失败")

print(f"\n成功提取 {len(attachments_content)} 个附件内容")

# 保存结果
with open("attachments_content.json", "w", encoding="utf-8") as f:
    json.dump(attachments_content, f, ensure_ascii=False, indent=2)

print("\n附件内容已保存到 attachments_content.json")
