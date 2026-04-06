# CodexEmailRules（可部署完整版）

## 1. 项目结构

```text
CodexEmailRules/
├── app/
│   ├── api/routes/review.py           # 审核相关 API
│   ├── core/                          # 配置、日志、异常
│   ├── db/                            # SQLAlchemy 会话、模型、CRUD
│   ├── services/                      # AI、邮件收发、ERP、业务工作流
│   └── tasks/email_poller.py          # 定时拉取邮件任务
├── sql/schema.sql                     # MySQL 建表脚本
├── .env.example                       # 全量环境变量模板
├── requirements.txt
└── main.py                            # 统一启动入口
```

## 2. 功能说明（与前端工作台对接）

### API 列表
- `GET /api/reviews/pending`：获取待审核列表
- `GET /api/reviews/{email_id}`：获取单条详情（原文、AI、结构化、草稿）
- `POST /api/reviews/{email_id}/approve`：审核通过并执行发送+ERP写入
- `POST /api/reviews/{email_id}/send-edited`：编辑后发送并写入ERP
- `POST /api/reviews/{email_id}/regenerate`：退回重生成
- `POST /api/reviews/{email_id}/flag-risk`：标记高风险/人工处理

### 统一返回
```json
{
  "code": 0,
  "message": "success",
  "data": {}
}
```

## 3. 部署步骤

1. 准备 Python 3.11+ 与 MySQL 8+
2. 安装依赖：
   ```bash
   pip install -r requirements.txt
   ```
3. 复制配置：
   ```bash
   cp .env.example .env
   ```
4. 修改 `.env` 中数据库、IMAP、SMTP、ERP 等参数。
5. 建表：
   ```bash
   mysql -uroot -p < sql/schema.sql
   ```
6. 启动服务：
   ```bash
   python main.py
   ```

## 4. 生产建议
- 用 `systemd/supervisor` 托管 `python main.py`。
- 将日志接入 ELK / Loki。
- AI 服务替换 `app/services/ai_processor.py` 中 `analyze` 方法。
- ERP 接口路径可在 `app/services/erp_client.py` 按实际系统调整。

## 5. 运行结果
- 前端审核工作台可直接调用 API。
- 系统后台按间隔自动拉取邮箱并入库。
- 审核通过可自动发送回复并推送 ERP。
