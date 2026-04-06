# Codex Email Rules 企业级扩展模块

该仓库提供可直接落地的扩展能力：

1. **客服审核工作台（HTML + Tailwind + 原生 JS）**
2. **SMTP 自动发送邮件模块（多账号、重试、日志、告警）**
3. **ERP 自动写入模块（字段映射、重试、一致性校验、失败缓存重放）**

## 目录结构

```text
.
├── public/
│   └── review-workbench.html              # 客服审核工作台
├── src/
│   ├── config/
│   │   └── env.js                         # .env 加载和配置解析
│   ├── modules/
│   │   ├── mailer/
│   │   │   ├── smtpClient.js              # SMTP 多发件箱连接池
│   │   │   └── sendService.js             # 邮件发送服务（重试/告警/日志）
│   │   ├── erp/
│   │   │   ├── erpClient.js               # ERP 通用调用客户端
│   │   │   ├── mappers.js                 # 字段映射与一致性校验
│   │   │   └── retryQueue.js              # 失败缓存队列
│   │   └── workflow/
│   │       └── reviewSyncService.js       # 审核动作与状态同步
│   └── examples/
│       └── integrationExample.js          # 与主流程对接示例
├── data/cache/
│   └── erp-failures.json                  # ERP 写入失败缓存（运行时生成）
├── .env.example
└── package.json
```

## 依赖清单

- Node.js 18+
- axios
- dotenv
- nodemailer
- pino

安装：

```bash
npm install
```

## 配置说明（.env）

复制模板并修改：

```bash
cp .env.example .env
```

关键配置：

- `SMTP_ACCOUNTS`：多发件邮箱 JSON 数组
- `SMTP_DEFAULT_ACCOUNT`：默认发件身份
- `SMTP_SIGNATURE`：自动追加签名
- `SMTP_MAX_RETRY` / `SMTP_RETRY_BASE_MS`：指数退避参数
- `SMTP_ALERT_WEBHOOK`：发送失败告警 Webhook
- `ERP_BASE_URL` / `ERP_API_KEY`：ERP 接口鉴权
- `ERP_FIELD_MAPPING`：邮件字段到 ERP 字段映射
- `ERP_FAILURE_CACHE_FILE`：本地失败重试缓存文件

## 前端工作台对接说明

`public/review-workbench.html` 默认请求以下 API（可通过 `window.API_BASE_URL` 覆盖）：

- `GET /review-mails?filter=pending&sort=priority`
- `POST /review-mails/:mailId/actions`

建议后端返回数据结构：

```json
[
  {
    "id": "mail-001",
    "subject": "订单地址需要修改",
    "sender": "customer@example.com",
    "category": "地址修改",
    "priority": "P1",
    "slaDeadline": "2026-04-06T18:00:00Z",
    "originalHtml": "<p>...</p>",
    "structured": {
      "orderNo": "SO-1001",
      "amount": "128.99"
    },
    "aiDraft": "您好...",
    "riskLevel": "LOW"
  }
]
```

## 自动发送邮件模块设计

- `SMTPClientPool` 负责维护多个 SMTP 连接配置
- `EmailSendService.sendReply()` 负责：
  - 按客户邮件地址回复
  - 支持 CC/BCC
  - 文本/HTML 自动追加签名
  - 发送失败指数退避重试
  - 失败告警（Webhook）
  - 发送日志写入 `data/send-log.jsonl`

## ERP 写入模块设计

- `ERPClient.write()` 根据解析结果写入 ERP
- 支持 provider 适配（`generic` / `shopify`）
- `mapFields()` 支持字段映射定制
- `validateConsistency()` 执行写入一致性检查
- 失败记录落盘到 `ERPFailureQueue`
- `ERPClient.retryFailed()` 支持后台定时重试

## 与主流程兼容建议

在原有邮件处理主流程中，推荐调用顺序：

1. NLP / LLM 完成邮件分类与结构化抽取
2. 生成 AI 草稿并进入审核工作台
3. 客服触发动作后，调用 `ReviewSyncService.processReviewAction()`
4. 发送成功后自动触发 ERP 写入
5. 对失败 ERP 任务启动后台轮询重试

## 启动示例

```bash
npm run start
```

语法检查：

```bash
npm run check
```

## 生产部署建议

- 使用 PM2/Systemd 托管 Node 进程
- 日志接入 ELK / Loki / Datadog
- 对 `data/cache` 和日志目录做持久化挂载
- 将 SMTP/ERP 密钥配置到 CI/CD Secret，不入库
- 前端页面可由 Nginx 直接托管到 `/ops/review-workbench`

