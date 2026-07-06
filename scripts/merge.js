const fs = require('fs');

// 读取已有文件
const existing = JSON.parse(fs.readFileSync('企业会计准则_全文.json', 'utf8'));

// 读取各批次
const batch2 = JSON.parse(fs.readFileSync('batch2.json', 'utf8'));
const batch3 = JSON.parse(fs.readFileSync('batch3.json', 'utf8'));
const batch4 = JSON.parse(fs.readFileSync('batch4.json', 'utf8'));
const batch5 = JSON.parse(fs.readFileSync('batch5.json', 'utf8'));

// 合并所有文章
const allArticles = [
  ...existing.articles,
  ...batch2,
  ...batch3,
  ...batch4,
  ...batch5
];

// 写入最终文件
const final = {
  source: "财政部会计司 - 企业会计准则",
  url: "https://kjs.mof.gov.cn/zt/kjzzss/kuaijizhunzeshishi/",
  total_count: allArticles.length,
  articles: allArticles
};

fs.writeFileSync('企业会计准则_全文.json', JSON.stringify(final, null, 2), 'utf8');
console.log(`合并完成！共 ${allArticles.length} 篇文章`);
