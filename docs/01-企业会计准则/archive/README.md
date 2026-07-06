# Python 脚本归档目录

此目录包含会计准则知识库维护过程中使用的所有 Python 脚本。

## 核心脚本（已复制到 Skill 目录）

以下脚本已复制到 `~/.config/opencode/skills/cas-accounting-workflow/scripts/`，建议从 Skill 目录使用：

| 脚本 | 功能 | 优先级 |
|------|------|--------|
| `audit_and_fix.py` | 检查并修复 origin_url | ⭐⭐⭐ |
| `check_content_consistency.py` | 检查 md 与 JSON 内容一致性 | ⭐⭐⭐ |
| `update_md_from_json.py` | 用 JSON 完整内容更新 md | ⭐⭐⭐ |
| `refetch.py` | 重新抓取官方内容到 JSON | ⭐⭐⭐ |

## 辅助脚本（仅在需要时使用）

| 脚本 | 功能 | 使用场景 |
|------|------|----------|
| `analyze.py` | 分析 JSON 数据结构 | 了解数据分布 |
| `check_frontmatter.py` | 检查 Frontmatter 完整性 | 新增文件检查 |
| `clean_json.py` | 清理 JSON 文件 | 数据清洗 |
| `compare_detailed.py` | 详细比较工具 | 深度分析差异 |
| `deep_clean_json.py` | 深度清理 JSON | 复杂数据清洗 |
| `generate_final_report.py` | 生成验证报告 | 生成报告 |
| `list_warning_files.py` | 列出警告文件 | 快速查看问题文件 |
| `refetch_31.py` | 单独抓取第31号 | 单个准则更新 |
| `refetch_all.py` | 批量重新抓取 | 批量更新 |
| `verify_frontmatter.py` | 验证 Frontmatter | 质量检查 |

## 使用建议

1. **日常使用**：优先使用 Skill 目录中的核心脚本
2. **特殊需求**：如需使用辅助脚本，从 archive 目录复制到工作目录
3. **运行环境**：所有脚本需要 Python 3.9+ 和 `requests`、`beautifulsoup4` 库

## 安装依赖

```bash
pip install requests beautifulsoup4
```

## 运行方式

```bash
# 从 archive 运行辅助脚本
python3 archive/analyze.py

# 或复制到当前目录后运行
cp archive/analyze.py .
python3 analyze.py
```

---

*归档日期：2026-03-06*
