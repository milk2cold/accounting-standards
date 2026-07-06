import json
import urllib.request
import re

# 定义所有解释的URL
articles_data = [
    {
        "title": "关于印发《企业会计准则解释第19号》的通知",
        "url": "https://kjs.mof.gov.cn/zhengcefabu/202512/t20251218_3979556.htm",
        "date": "2025-12-19",
    },
    {
        "title": "关于印发《企业会计准则解释第18号》的通知",
        "url": "https://kjs.mof.gov.cn/zhengcefabu/202412/t20241223_3950344.htm",
        "date": "2024-12-31",
    },
    {
        "title": "关于印发《企业会计准则解释第17号》的通知",
        "url": "https://kjs.mof.gov.cn/zhengcefabu/202311/t20231109_3915491.htm",
        "date": "2023-11-09",
    },
    {
        "title": "关于印发《企业会计准则解释第16号》的通知",
        "url": "https://kjs.mof.gov.cn/gongzuotongzhi/202212/t20221212_3857395.htm",
        "date": "2022-12-13",
    },
    {
        "title": "关于印发《企业会计准则解释第15号》的通知",
        "url": "https://kjs.mof.gov.cn/zhengcefabu/202112/t20211231_3779983.htm",
        "date": "2021-12-31",
    },
    {
        "title": "关于印发《企业会计准则解释第14号》的通知",
        "url": "https://kjs.mof.gov.cn/zhengcefabu/202102/t20210202_3653110.htm",
        "date": "2021-02-02",
    },
    {
        "title": "关于印发《企业会计准则解释第13号》的通知",
        "url": "https://kjs.mof.gov.cn/zhengcefabu/201912/t20191213_3441493.htm",
        "date": "2019-12-16",
    },
    {
        "title": "关于印发《企业会计准则解释第12号——关于关键管理人员服务的提供方与接受方是否为关联方》的通知",
        "url": "https://kjs.mof.gov.cn/zhengcefabu/201706/t20170621_2628439.htm",
        "date": "2017-06-21",
    },
    {
        "title": "关于印发《企业会计准则解释第11号——关于以使用无形资产产生的收入为基础的摊销方法》的通知",
        "url": "https://kjs.mof.gov.cn/zhengcefabu/201706/t20170621_2628437.htm",
        "date": "2017-06-21",
    },
    {
        "title": "关于印发《企业会计准则解释第10号——关于以使用固定资产产生的收入为基础的折旧方法》的通知",
        "url": "https://kjs.mof.gov.cn/zhengcefabu/201706/t20170621_2628435.htm",
        "date": "2017-06-21",
    },
    {
        "title": "关于印发《企业会计准则解释第9号——关于权益法下投资净损失的会计处理》的通知",
        "url": "https://kjs.mof.gov.cn/zhengcefabu/201706/t20170621_2628433.htm",
        "date": "2017-06-21",
    },
    {
        "title": "关于印发《企业会计准则解释第8号》的通知",
        "url": "https://kjs.mof.gov.cn/zhengcefabu/201601/t20160104_1643346.htm",
        "date": "2016-01-04",
    },
    {
        "title": "关于印发《企业会计准则解释第7号》的通知",
        "url": "https://kjs.mof.gov.cn/zhengcefabu/201511/t20151113_1559056.htm",
        "date": "2015-11-13",
    },
    {
        "title": "关于印发《企业会计准则解释第6号》的通知",
        "url": "https://kjs.mof.gov.cn/zhengcefabu/201401/t20140123_1038629.htm",
        "date": "2014-01-24",
    },
    {
        "title": "关于印发企业会计准则解释第5号的通知",
        "url": "https://kjs.mof.gov.cn/zhengcefabu/201211/t20121122_701308.htm",
        "date": "2012-11-30",
    },
    {
        "title": "关于印发企业会计准则解释第4号的通知",
        "url": "https://kjs.mof.gov.cn/zhengcefabu/201008/t20100809_332092.htm",
        "date": "2010-08-09",
    },
    {
        "title": "关于印发企业会计准则解释第3号的通知",
        "url": "https://kjs.mof.gov.cn/zhengcefabu/200906/t20090625_172281.htm",
        "date": "2009-06-25",
    },
    {
        "title": "关于印发企业会计准则解释第2号的通知",
        "url": "https://kjs.mof.gov.cn/zhengcefabu/200809/t20080912_74645.htm",
        "date": "2008-09-17",
    },
    {
        "title": "关于印发《企业会计准则解释第1号》的通知",
        "url": "https://kjs.mof.gov.cn/zhengcefabu/200805/t20080522_33804.htm",
        "date": "2008-05-22",
    },
]


def fetch_content(url):
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=15) as response:
            html = response.read().decode("utf-8")

        paragraphs = re.findall(r"<p[^>]*>(.*?)</p>", html, re.DOTALL)
        content_parts = []
        for p in paragraphs:
            text = re.sub(r"<[^>]+>", "", p)
            text = text.strip()
            if text and len(text) > 5:
                if (
                    "版权所有" not in text
                    and "技术支持" not in text
                    and "网站标识码" not in text
                ):
                    content_parts.append(text)

        return "\n\n".join(content_parts)
    except Exception as e:
        return f"Error: {str(e)}"


articles = []
for i, art in enumerate(articles_data):
    print(f"[{i + 1}/{len(articles_data)}] Fetching: {art['title']}")
    content = fetch_content(art["url"])
    articles.append(
        {
            "title": art["title"],
            "url": art["url"],
            "date": art["date"],
            "content": content,
        }
    )

# 添加附件内容
with open("解释1号.txt", "r", encoding="utf-8") as f:
    attach1 = f.read()
with open("解释2号.txt", "r", encoding="utf-8") as f:
    attach2 = f.read()
with open("解释3号.txt", "r", encoding="utf-8") as f:
    attach3 = f.read()

# 更新1-3号的content，添加附件
for art in articles:
    if "第1号" in art["title"]:
        art["content"] = art["content"] + "\n\n===== 附件全文 =====\n\n" + attach1
        art["attachment_url"] = (
            "https://kjs.mof.gov.cn/zhengcefabu/200805/P020081118406702247293.doc"
        )
    elif "第2号" in art["title"]:
        art["content"] = art["content"] + "\n\n===== 附件全文 =====\n\n" + attach2
        art["attachment_url"] = (
            "https://kjs.mof.gov.cn/zhengcefabu/200809/P020080912540661805201.doc"
        )
    elif "第3号" in art["title"]:
        art["content"] = art["content"] + "\n\n===== 附件全文 =====\n\n" + attach3
        art["attachment_url"] = (
            "https://kjs.mof.gov.cn/zhengcefabu/200906/P020090625556829994230.doc"
        )
    elif "第4号" in art["title"]:
        art["attachment_url"] = (
            "https://kjs.mof.gov.cn/zhengcefabu/201008/P020100809542292789598.doc"
        )

data = {
    "source": "财政部会计司 - 企业会计准则解释",
    "url": "https://kjs.mof.gov.cn/zt/kjzzss/qykjzzjs/",
    "total_count": len(articles),
    "articles": articles,
}

with open("企业会计准则解释_全文.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"\n完成！共 {len(articles)} 篇文章")
