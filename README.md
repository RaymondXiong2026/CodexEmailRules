# 店铺邮件 AI 自动化处理系统

本项目提供一套可部署的、模块化的邮件自动处理流水线，涵盖：
- IMAP 多店铺邮件拉取
- 去重与线程归并
- 邮件清洗与 PII 脱敏
- 一级/二级分类与置信度评估
- 优先级与 SLA 生成
- 知识库 RAG（关键词 + 向量）
- 合规回复草稿生成
- 风险识别与人工审核判断
- 全量结构化 JSON 输出与 MySQL 落库

> 注意：由于当前仓库未包含《店铺邮件自动处理流程设计.md》原文，系统已按“可配置优先”实现。请将文档中的分类、阈值、字段映射到 `config/workflow_rules.yaml`，即可实现与文档一一对应。

## 1) 安装依赖

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
```

## 2) 配置环境变量

复制并编辑 `.env.example` 为 `.env`：

```bash
cp .env.example .env
```

## 3) 初始化 MySQL 表

```bash
mysql -u root -p < sql/schema.sql
```

## 4) 运行

```bash
python -m app.main
```

可选：
```bash
python -m app.main --once
```

## 5) 输出

每封邮件处理后会输出完整结构化 JSON，并写入 `processed_email_records`。

