# 客服审核工作台系统（全套示例）

本项目包含你要求的完整模块：

1. 客服审核工作台（前端页面）
2. 自动发送邮件模块
3. 自动写入 ERP 接口模块
4. 后端 API 接口
5. 数据库结构（SQLite）
6. 定时任务（node-cron）
7. 完整启动入口与配置文件

---

## 一、项目结构

```bash
CodexEmailRules/
├─ .env.example
├─ .gitignore
├─ package.json
├─ README.md
└─ src/
   ├─ config.js
   ├─ db.js
   ├─ server.js
   ├─ jobs/
   │  └─ scheduler.js
   ├─ models/
   │  └─ schema.sql
   ├─ routes/
   │  └─ api.js
   ├─ services/
   │  ├─ emailService.js
   │  ├─ erpService.js
   │  └─ reviewService.js
   └─ public/
      ├─ index.html
      ├─ styles.css
      └─ app.js
```

---

## 二、快速启动

### 1) 安装依赖

```bash
npm install
```

### 2) 初始化环境变量

```bash
cp .env.example .env
```

按需修改 `.env`：
- SMTP 配置：用于真实发邮件
- ERP_BASE_URL / ERP_API_KEY：用于真实 ERP 写入

### 3) 启动服务

```bash
npm run start
```

默认访问：
- 前端工作台：`http://localhost:3000`
- 健康检查：`GET /api/health`

---

## 三、API 说明

### 1) 创建任务

`POST /api/tasks`

请求示例：

```json
{
  "customer_name": "张三",
  "customer_email": "zhangsan@example.com",
  "order_no": "SO20260406001",
  "issue_type": "退款申请",
  "issue_description": "客户反馈商品破损"
}
```

### 2) 查询任务

`GET /api/tasks`

可选：`GET /api/tasks?status=PENDING`

### 3) 审核任务（自动触发邮件 + ERP）

`POST /api/tasks/:id/review`

请求示例：

```json
{
  "reviewer": "客服A",
  "status": "APPROVED",
  "review_note": "符合退款规则"
}
```

---

## 四、数据库设计

主表：`review_tasks`
- 客户信息、订单信息、问题信息
- 审核状态（PENDING/APPROVED/REJECTED）
- 审核人、审核备注、审核时间
- 后续动作标记：`email_sent`、`erp_written`

任务日志表：`job_runs`
- 记录定时任务执行情况

SQL 见：`src/models/schema.sql`

---

## 五、定时任务说明

- 启动后根据 `CRON_REVIEW_SCAN` 扫描任务（默认每 5 分钟）
- 对 `APPROVED/REJECTED` 且未完成邮件或 ERP 写入的记录自动补偿处理
- 执行结果写入 `job_runs`

---

## 六、真实环境接入建议

1. SMTP 建议使用企业邮箱 SMTP（SSL/TLS）
2. ERP 接口建议增加签名机制与重试策略
3. 生产建议替换 SQLite 为 MySQL/PostgreSQL
4. 建议增加鉴权（JWT/OAuth2）与操作审计

