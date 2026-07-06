const { chromium } = require('playwright');
const fs = require('fs');

// 批次1: 文章1-10 (第19号-第10号)
const articles1 = [
  { title: "关于印发《企业会计准则解释第19号》的通知", url: "https://kjs.mof.gov.cn/zhengcefabu/202512/t20251218_3979556.htm", date: "2025-12-19" },
  { title: "关于印发《企业会计准则解释第18号》的通知", url: "https://kjs.mof.gov.cn/zhengcefabu/202412/t20241223_3950344.htm", date: "2024-12-31" },
  { title: "关于印发《企业会计准则解释第17号》的通知", url: "https://kjs.mof.gov.cn/zhengcefabu/202311/t20231109_3915491.htm", date: "2023-11-09" },
  { title: "关于印发《企业会计准则解释第16号》的通知", url: "https://kjs.mof.gov.cn/gongzuotongzhi/202212/t20221212_3857395.htm", date: "2022-12-13" },
  { title: "关于印发《企业会计准则解释第15号》的通知", url: "https://kjs.mof.gov.cn/zhengcefabu/202112/t20211231_3779983.htm", date: "2021-12-31" },
  { title: "关于印发《企业会计准则解释第14号》的通知", url: "https://kjs.mof.gov.cn/zhengcefabu/202102/t20210202_3653110.htm", date: "2021-02-02" },
  { title: "关于印发《企业会计准则解释第13号》的通知", url: "https://kjs.mof.gov.cn/zhengcefabu/201912/t20191213_3441493.htm", date: "2019-12-16" },
  { title: "关于印发《企业会计准则解释第12号——关于关键管理人员服务的提供方与接受方是否为关联方》的通知", url: "https://kjs.mof.gov.cn/zhengcefabu/201706/t20170621_2628439.htm", date: "2017-06-21" },
  { title: "关于印发《企业会计准则解释第11号——关于以使用无形资产产生的收入为基础的摊销方法》的通知", url: "https://kjs.mof.gov.cn/zhengcefabu/201706/t20170621_2628437.htm", date: "2017-06-21" },
  { title: "关于印发《企业会计准则解释第10号——关于以使用固定资产产生的收入为基础的折旧方法》的通知", url: "https://kjs.mof.gov.cn/zhengcefabu/201706/t20170621_2628435.htm", date: "2017-06-21" }
];

// 批次2: 文章11-19 (第9号-第1号)
const articles2 = [
  { title: "关于印发《企业会计准则解释第9号——关于权益法下投资净损失的会计处理》的通知", url: "https://kjs.mof.gov.cn/zhengcefabu/201706/t20170621_2628433.htm", date: "2017-06-21" },
  { title: "关于印发《企业会计准则解释第8号》的通知", url: "https://kjs.mof.gov.cn/zhengcefabu/201601/t20160104_1643346.htm", date: "2016-01-04" },
  { title: "关于印发《企业会计准则解释第7号》的通知", url: "https://kjs.mof.gov.cn/zhengcefabu/201511/t20151113_1559056.htm", date: "2015-11-13" },
  { title: "关于印发《企业会计准则解释第6号》的通知", url: "https://kjs.mof.gov.cn/zhengcefabu/201401/t20140123_1038629.htm", date: "2014-01-24" },
  { title: "关于印发企业会计准则解释第5号的通知", url: "https://kjs.mof.gov.cn/zhengcefabu/201211/t20121122_701308.htm", date: "2012-11-30" },
  { title: "关于印发企业会计准则解释第4号的通知", url: "https://kjs.mof.gov.cn/zhengcefabu/201008/t20100809_332092.htm", date: "2010-08-09" },
  { title: "关于印发企业会计准则解释第3号的通知", url: "https://kjs.mof.gov.cn/zhengcefabu/200906/t20090625_172281.htm", date: "2009-06-25" },
  { title: "关于印发企业会计准则解释第2号的通知", url: "https://kjs.mof.gov.cn/zhengcefabu/200809/t20080912_74645.htm", date: "2008-09-17" },
  { title: "关于印发《企业会计准则解释第1号》的通知", url: "https://kjs.mof.gov.cn/zhengcefabu/200805/t20080522_33804.htm", date: "2008-05-22" }
];

async function fetchArticleContent(url) {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage();
  try {
    await page.goto(url, { timeout: 10000, waitUntil: 'domcontentloaded' });
    const content = await page.evaluate(() => {
      const paragraphs = document.querySelectorAll('p');
      const texts = [];
      paragraphs.forEach(p => {
        const text = p.innerText?.trim();
        if (text && text.length > 5 && !text.includes('版权所有') && !text.includes('技术支持')) {
          texts.push(text);
        }
      });
      return texts.join('\n\n');
    });
    await browser.close();
    return content;
  } catch (e) {
    await browser.close();
    return `Error: ${e.message}`;
  }
}

async function main() {
  const results1 = [];
  console.log(`Fetching batch 1: ${articles1.length} articles...`);
  for (let i = 0; i < articles1.length; i++) {
    const article = articles1[i];
    console.log(`[${i+1}/${articles1.length}] ${article.title}`);
    try {
      const content = await fetchArticleContent(article.url);
      results1.push({ ...article, content });
    } catch (e) {
      results1.push({ ...article, content: `Error: ${e.message}` });
    }
  }
  fs.writeFileSync('js_batch1.json', JSON.stringify(results1, null, 2), 'utf8');
  console.log('Batch 1 done!');

  const results2 = [];
  console.log(`Fetching batch 2: ${articles2.length} articles...`);
  for (let i = 0; i < articles2.length; i++) {
    const article = articles2[i];
    console.log(`[${i+1}/${articles2.length}] ${article.title}`);
    try {
      const content = await fetchArticleContent(article.url);
      results2.push({ ...article, content });
    } catch (e) {
      results2.push({ ...article, content: `Error: ${e.message}` });
    }
  }
  fs.writeFileSync('js_batch2.json', JSON.stringify(results2, null, 2), 'utf8');
  console.log('Batch 2 done!');

  // 合并
  const allArticles = [...results1, ...results2];
  const final = {
    source: "财政部会计司 - 企业会计准则解释",
    url: "https://kjs.mof.gov.cn/zt/kjzzss/qykjzzjs/",
    total_count: allArticles.length,
    articles: allArticles
  };
  fs.writeFileSync('企业会计准则解释_全文.json', JSON.stringify(final, null, 2), 'utf8');
  console.log(`合并完成！共 ${allArticles.length} 篇文章`);
}

main();
