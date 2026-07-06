const { chromium } = require('playwright');
const fs = require('fs');

// 批次3: 文章21-30
const articles = [
  { title: "企业会计准则第21号——租赁", url: "https://kjs.mof.gov.cn/zt/kjzzss/kuaijizhunzeshishi/201910/t20191028_3411190.htm", date: "2019-10-28" },
  { title: "企业会计准则第22号——金融工具确认和计量（财会〔2017〕7号）", url: "https://kjs.mof.gov.cn/zt/kjzzss/kuaijizhunzeshishi/201709/t20170908_2694655.htm", date: "2017-09-08" },
  { title: "企业会计准则第22号——金融工具确认和计量（财会〔2006〕3号）", url: "https://kjs.mof.gov.cn/zt/kjzzss/kuaijizhunzeshishi/200806/t20080618_46226.htm", date: "2006-03-09" },
  { title: "企业会计准则第23号——金融资产转移（财会〔2017〕8号）", url: "https://kjs.mof.gov.cn/zt/kjzzss/kuaijizhunzeshishi/201709/t20170908_2694626.htm", date: "2017-09-08" },
  { title: "企业会计准则第23号——金融资产转移（财会〔2006〕3号）", url: "https://kjs.mof.gov.cn/zt/kjzzss/kuaijizhunzeshishi/200806/t20080618_46225.htm", date: "2006-03-09" },
  { title: "企业会计准则第24号——套期会计（财会〔2017〕9号）", url: "https://kjs.mof.gov.cn/zt/kjzzss/kuaijizhunzeshishi/201709/t20170908_2694624.htm", date: "2017-09-08" },
  { title: "企业会计准则第24号——套期保值（财会〔2006〕3号）", url: "https://kjs.mof.gov.cn/zt/kjzzss/kuaijizhunzeshishi/200806/t20080618_46224.htm", date: "2006-03-09" },
  { title: "企业会计准则第25号——保险合同（财会〔2020〕20号）", url: "https://kjs.mof.gov.cn/zt/kjzzss/kuaijizhunzeshishi/202202/t20220224_3790240.htm", date: "2022-02-24" },
  { title: "企业会计准则第25号——原保险合同（财会〔2006〕3号）", url: "https://kjs.mof.gov.cn/zt/kjzzss/kuaijizhunzeshishi/200806/t20080618_46223.htm", date: "2006-03-09" },
  { title: "企业会计准则第26号——再保险合同（财会〔2006〕3号）", url: "https://kjs.mof.gov.cn/zt/kjzzss/kuaijizhunzeshishi/200806/t20080618_46222.htm", date: "2006-03-09" }
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
  fs.writeFileSync('batch3.json', JSON.stringify(results, null, 2), 'utf8');
  console.log('Batch 3 done!');
}

main();
