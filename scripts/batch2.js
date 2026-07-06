const { chromium } = require('playwright');
const fs = require('fs');

// 批次2: 文章11-20
const articles = [
  { title: "企业会计准则第10号——企业年金基金", url: "https://kjs.mof.gov.cn/zt/kjzzss/kuaijizhunzeshishi/200806/t20080618_46238.htm", date: "2006-03-09" },
  { title: "企业会计准则第11号——股份支付", url: "https://kjs.mof.gov.cn/zt/kjzzss/kuaijizhunzeshishi/200806/t20080618_46237.htm", date: "2006-03-09" },
  { title: "企业会计准则第12号——债务重组", url: "https://kjs.mof.gov.cn/zt/kjzzss/kuaijizhunzeshishi/201910/t20191028_3410789.htm", date: "2019-10-28" },
  { title: "企业会计准则第13号——或有事项", url: "https://kjs.mof.gov.cn/zt/kjzzss/kuaijizhunzeshishi/200806/t20080618_46235.htm", date: "2006-03-09" },
  { title: "企业会计准则第14号——收入", url: "https://kjs.mof.gov.cn/zt/kjzzss/kuaijizhunzeshishi/201709/t20170907_2694006.htm", date: "2017-09-07" },
  { title: "企业会计准则第16号——政府补助", url: "https://kjs.mof.gov.cn/zt/kjzzss/kuaijizhunzeshishi/200806/t20080618_46232.htm", date: "2017-05-25" },
  { title: "企业会计准则第17号——借款费用", url: "https://kjs.mof.gov.cn/zt/kjzzss/kuaijizhunzeshishi/200806/t20080618_46231.htm", date: "2006-03-09" },
  { title: "企业会计准则第18号——所得税", url: "https://kjs.mof.gov.cn/zt/kjzzss/kuaijizhunzeshishi/200806/t20080618_46230.htm", date: "2006-03-09" },
  { title: "企业会计准则第19号——外币折算", url: "https://kjs.mof.gov.cn/zt/kjzzss/kuaijizhunzeshishi/200806/t20080618_46229.htm", date: "2006-03-09" },
  { title: "企业会计准则第20号——企业合并", url: "https://kjs.mof.gov.cn/zt/kjzzss/kuaijizhunzeshishi/200806/t20080618_46228.htm", date: "2006-03-09" }
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
  fs.writeFileSync('batch2.json', JSON.stringify(results, null, 2), 'utf8');
  console.log('Batch 2 done!');
}

main();
