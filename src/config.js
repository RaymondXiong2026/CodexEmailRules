const path = require('path');
const dotenv = require('dotenv');

dotenv.config();

function toBoolean(value, fallback = false) {
  if (value === undefined || value === null) return fallback;
  return String(value).toLowerCase() === 'true';
}

const config = {
  port: Number(process.env.PORT || 3000),
  dbPath: path.resolve(process.env.DB_PATH || './data/app.db'),
  smtp: {
    host: process.env.SMTP_HOST || '',
    port: Number(process.env.SMTP_PORT || 465),
    user: process.env.SMTP_USER || '',
    pass: process.env.SMTP_PASS || '',
    secure: toBoolean(process.env.SMTP_SECURE, true),
    from: process.env.MAIL_FROM || 'no-reply@example.com'
  },
  erp: {
    baseUrl: process.env.ERP_BASE_URL || '',
    apiKey: process.env.ERP_API_KEY || '',
    timeoutMs: Number(process.env.ERP_TIMEOUT_MS || 10000)
  },
  jobs: {
    reviewScanCron: process.env.CRON_REVIEW_SCAN || '*/5 * * * *'
  }
};

module.exports = config;
