# 会计准则知识库

[![Deploy](https://github.com/milk2cold/accounting-standards/actions/workflows/deploy.yml/badge.svg)](https://github.com/milk2cold/accounting-standards/actions/workflows/deploy.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> 基于 Astro 与 Bun 构建的中国会计准则静态知识库。

**在线访问**: [https://milk2cold.github.io/accounting-standards/](https://milk2cold.github.io/accounting-standards/)

## 项目现状

- 已上线 GitHub Pages 自动部署
- 首页与文档页已重做为简约阅读型界面
- 已接入 Pagefind 全文搜索
- 站点构建前会自动从根目录 `docs/` 同步 Markdown
- 当前已覆盖：
  - 企业会计准则
  - 企业会计准则解释
  - 企业会计准则指南
  - 每月更新
  - 推荐资源

## 技术栈

- [Astro](https://astro.build/)
- [Bun](https://bun.sh/)
- [Tailwind CSS](https://tailwindcss.com/)
- [Pagefind](https://pagefind.app/)
- [GitHub Pages](https://pages.github.com/)

## 本地开发

```bash
cd site
bun install
bun run dev
```

默认开发地址通常为 [http://localhost:4321](http://localhost:4321)。

## 构建与部署

```bash
cd site
bun run build
```

构建流程会自动执行：

1. `bun run scripts/sync-docs.ts`
2. `astro build`
3. `pagefind --site dist`

推送到 GitHub `main` 后，GitHub Actions 会自动部署到 GitHub Pages。

## 内容同步机制

站点内容不直接在 `site/src/content/docs/` 手工维护，而是从项目根目录 `docs/` 同步生成。

当前同步目录：

- `docs/01-企业会计准则`
- `docs/02-企业会计准则解释`
- `docs/03-企业会计准则指南`
- `docs/08-每月更新`
- `docs/09-推荐资源`

同步脚本位置：

- [`scripts/sync-docs.ts`](./scripts/sync-docs.ts)

规则摘要：

- 自动忽略 `json`、`pdf`、`docx`、`archive` 等非站点文件
- 对缺失 frontmatter 的 Markdown 自动补最小 frontmatter
- 自动移除不兼容的 `layout:` 字段

## 目录结构

```text
site/
├── .github/workflows/       # GitHub Pages 部署
├── scripts/
│   └── sync-docs.ts         # docs -> site 内容同步
├── src/
│   ├── content/docs/        # 构建前自动生成的站点内容
│   ├── layouts/             # BaseLayout / DocLayout
│   └── pages/
│       ├── index.astro
│       └── docs/[...slug].astro
├── public/
├── dist/
└── package.json
```

## 内容来源

- 财政部会计司
- 中国会计准则委员会
- 德勤 CAS Plus

说明：本站为学习与检索用途的整理站，具体内容仍应以官方最新版本为准。

## 许可证

MIT
