const { chromium } = require('playwright');
const fs = require('fs');

// 批次5: 文章41-47
const articles = [
  { title: "企业会计准则第37号——金融工具列报（财会〔2017〕14号）", url: "https://kjs.mof.gov.cn/zt/kjzzss/kuaijizhunzeshishi/201709/t20170907_2694118.htm", date: "2017-09-07" },
  { title: "企业会计准则第37号——金融工具列报（财会〔2014〕23号）", url: "https://kjs.mof.gov.cn/zt/kjzzss/kuaijizhunzeshishi/200806/t20080618_46244.htm", date: "2014-07-11" },
  { title: "企业会计准则第38号——首次执行企业会计准则", url: "https://kjs.mof.gov.cn/zt/kjzzss/kuaijizhunzeshishi/200806/t20080618_46243.htm", date: "2006-03-09" },
  { title: "企业会计准则第39号——公允价值计量", url: "https://kjs.mof.gov.cn/zt/kjzzss/kuaijizhunzeshishi/201512/t20151208_1602631.htm", date: "2015-12-08" },
  { title: "企业会计准则第40号——合营安排", url: "https://kjs.mof.gov.cn/zt/kjzzss/kuaijizhunzeshishi/201512/t20151208_1602633.htm", date: "2015-12-08" },
  { title: "企业会计准则第41号——在其他主体中权益的披露", url: "https://kjs.mof.gov.cn/zt/kjzzss/kuaijizhunzeshishi/201512/t20151208_1602637.htm", date: "2015-12-08" },
  { title: "企业会计准则第42号——持有待售的非流动资产、处置组和终止经营", url: "https://kjs.mof.gov.cn/zt/kjzzss/kuaijizhunzeshishi/201709/t20170907_2694145.htm", date: "2017-09-07" }
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
  const results = [];
  console.log(`Fetching ${articles.length} articles...`);
  for (let i = 0; i < articles.length; i++) {
    const article = articles[i];
    console.log(`[${i+1}/${articles.length}] ${article.title}`);
    try {
      const content = await fetchArticleContent(article.url);
      results.push({ ...article, content });
    } catch (e) {
      results.push({ ...article, content: `Error: ${e.message}` });
    }
  }
  fs.writeFileSync('batch5.json', JSON.stringify(results, null, 2), 'utf8');
  console.log('Batch 5 done!');
}

main();
