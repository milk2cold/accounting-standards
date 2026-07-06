const { chromium } = require('playwright');
const fs = require('fs');

// 批次4: 文章31-40
const articles = [
  { title: "企业会计准则第27号——石油天然气开采", url: "https://kjs.mof.gov.cn/zt/kjzzss/kuaijizhunzeshishi/200806/t20080618_46221.htm", date: "2006-03-09" },
  { title: "企业会计准则第28号——会计政策、会计估计变更和差错更正", url: "https://kjs.mof.gov.cn/zt/kjzzss/kuaijizhunzeshishi/200806/t20080618_46220.htm", date: "2006-03-09" },
  { title: "企业会计准则第29号——资产负债表日后事项", url: "https://kjs.mof.gov.cn/zt/kjzzss/kuaijizhunzeshishi/200806/t20080618_46219.htm", date: "2006-03-09" },
  { title: "企业会计准则第30号——财务报表列报", url: "https://kjs.mof.gov.cn/zt/kjzzss/kuaijizhunzeshishi/200806/t20080618_46218.htm", date: "2014-02-17" },
  { title: "企业会计准则第31号——现金流量表", url: "https://kjs.mof.gov.cn/zt/kjzzss/kuaijizhunzeshishi/200806/t20080618_46250.htm", date: "2006-03-09" },
  { title: "企业会计准则第32号——中期财务报告", url: "https://kjs.mof.gov.cn/zt/kjzzss/kuaijizhunzeshishi/200806/t20080618_46249.htm", date: "2006-03-09" },
  { title: "企业会计准则第33号——合并财务报表", url: "https://kjs.mof.gov.cn/zt/kjzzss/kuaijizhunzeshishi/200806/t20080618_46248.htm", date: "2014-03-03" },
  { title: "企业会计准则第34号——每股收益", url: "https://kjs.mof.gov.cn/zt/kjzzss/kuaijizhunzeshishi/200806/t20080618_46247.htm", date: "2006-03-09" },
  { title: "企业会计准则第35号——分部报告", url: "https://kjs.mof.gov.cn/zt/kjzzss/kuaijizhunzeshishi/200806/t20080618_46246.htm", date: "2006-03-09" },
  { title: "企业会计准则第36号——关联方披露", url: "https://kjs.mof.gov.cn/zt/kjzzss/kuaijizhunzeshishi/200806/t20080618_46245.htm", date: "2006-03-09" }
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
  fs.writeFileSync('batch4.json', JSON.stringify(results, null, 2), 'utf8');
  console.log('Batch 4 done!');
}

main();
