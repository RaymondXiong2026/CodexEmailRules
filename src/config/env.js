import dotenv from 'dotenv';

dotenv.config();

const requiredKeys = ['API_BASE_URL'];

for (const key of requiredKeys) {
  if (!process.env[key]) {
    throw new Error(`Missing required env key: ${key}`);
  }
}

const parseJson = (value, fallback) => {
  if (!value) return fallback;
  try {
    return JSON.parse(value);
  } catch (error) {
    throw new Error(`Invalid JSON env value: ${value}`);
  }
};

export const env = {
  appName: process.env.APP_NAME || 'codex-email-rules-extension',
  nodeEnv: process.env.NODE_ENV || 'development',
  logLevel: process.env.LOG_LEVEL || 'info',
  apiBaseUrl: process.env.API_BASE_URL,
  smtp: {
    accounts: parseJson(process.env.SMTP_ACCOUNTS, []),
    defaultAccount: process.env.SMTP_DEFAULT_ACCOUNT,
    signature: process.env.SMTP_SIGNATURE || '',
    maxRetry: Number(process.env.SMTP_MAX_RETRY || 4),
    retryBaseMs: Number(process.env.SMTP_RETRY_BASE_MS || 500),
    alertWebhook: process.env.SMTP_ALERT_WEBHOOK || ''
  },
  erp: {
    provider: process.env.ERP_PROVIDER || 'generic',
    baseUrl: process.env.ERP_BASE_URL || '',
    apiKey: process.env.ERP_API_KEY || '',
    timeoutMs: Number(process.env.ERP_TIMEOUT_MS || 8000),
    maxRetry: Number(process.env.ERP_MAX_RETRY || 3),
    retryBaseMs: Number(process.env.ERP_RETRY_BASE_MS || 700),
    failureCacheFile: process.env.ERP_FAILURE_CACHE_FILE || './data/cache/erp-failures.json',
    fieldMapping: parseJson(process.env.ERP_FIELD_MAPPING, {})
  }
};
