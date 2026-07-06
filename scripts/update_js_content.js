const fs = require('fs');

// 读取现有JSON
const data = JSON.parse(fs.readFileSync('企业会计准则解释_全文.json', 'utf8'));

// 读取附件内容
const content1 = fs.readFileSync('解释1号.txt', 'utf8');
const content2 = fs.readFileSync('解释2号.txt', 'utf8');
const content3 = fs.readFileSync('解释3号.txt', 'utf8');

// 更新对应文章的内容
data.articles.forEach(article => {
  if (article.title.includes('第1号')) {
    // 保留原有通知内容，附加附件全文
    article.content = article.content + '\n\n===== 附件全文 =====\n\n' + content1;
  } else if (article.title.includes('第2号')) {
    article.content = article.content + '\n\n===== 附件全文 =====\n\n' + content2;
  } else if (article.title.includes('第3号')) {
    article.content = article.content + '\n\n===== 附件全文 =====\n\n' + content3;
  } else if (article.title.includes('第4号')) {
    // 第4号附件已失效，添加说明
    article.content = article.content + '\n\n===== 附件说明 =====\n\n附件链接已失效(404)，无法获取附件内容。';
  }
});

// 写回文件
fs.writeFileSync('企业会计准则解释_全文.json', JSON.stringify(data, null, 2), 'utf8');
console.log('已更新JSON文件，添加附件内容');
