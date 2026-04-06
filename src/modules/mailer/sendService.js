import fs from 'node:fs/promises';
import path from 'node:path';
import pino from 'pino';

const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

export class EmailSendService {
  constructor({ smtpClientPool, signature, maxRetry = 3, retryBaseMs = 500, alertWebhook = '', logLevel = 'info' }) {
    this.smtpClientPool = smtpClientPool;
    this.signature = signature;
    this.maxRetry = maxRetry;
    this.retryBaseMs = retryBaseMs;
    this.alertWebhook = alertWebhook;
    this.logger = pino({ name: 'email-send-service', level: logLevel });
    this.logFile = path.resolve('data', 'send-log.jsonl');
  }

  appendSignature(content, isHtml) {
    if (!this.signature) return content;
    if (isHtml) return `${content}${this.signature}`;
    return `${content}\n\n${this.signature.replace(/<br\/?\s*>/gi, '\n').replace(/<[^>]*>/g, '')}`;
  }

  async notifyAlert(payload) {
    if (!this.alertWebhook) return;
    try {
      await fetch(this.alertWebhook, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
    } catch (error) {
      this.logger.warn({ error: error.message }, 'Failed to notify alert webhook');
    }
  }

  async writeLog(record) {
    await fs.mkdir(path.dirname(this.logFile), { recursive: true });
    await fs.appendFile(this.logFile, `${JSON.stringify({ ...record, loggedAt: new Date().toISOString() })}\n`);
  }

  async sendReply({ senderName, to, cc = [], bcc = [], subject, text = '', html = '', traceId }) {
    let attempt = 0;
    const isHtml = Boolean(html);

    while (attempt <= this.maxRetry) {
      try {
        const { transporter, fromEmail, fromName } = this.smtpClientPool.getClient(senderName);
        const finalHtml = isHtml ? this.appendSignature(html, true) : undefined;
        const finalText = this.appendSignature(text, false);

        const info = await transporter.sendMail({
          from: `${fromName} <${fromEmail}>`,
          to,
          cc,
          bcc,
          subject,
          text: finalText,
          html: finalHtml,
          headers: { 'X-Trace-Id': traceId || `trace-${Date.now()}` }
        });

        const successRecord = {
          traceId,
          to,
          subject,
          attempt,
          status: 'SUCCESS',
          providerMessageId: info.messageId,
          response: info.response
        };

        await this.writeLog(successRecord);
        this.logger.info(successRecord, 'Email sent');
        return successRecord;
      } catch (error) {
        const errorRecord = {
          traceId,
          to,
          subject,
          attempt,
          status: 'FAILED',
          errorMessage: error.message
        };

        await this.writeLog(errorRecord);
        this.logger.error(errorRecord, 'Email send failed');

        if (attempt === this.maxRetry) {
          await this.notifyAlert({
            type: 'SMTP_SEND_FAILED',
            traceId,
            to,
            subject,
            error: error.message
          });
          return errorRecord;
        }

        const backoff = this.retryBaseMs * 2 ** attempt;
        await sleep(backoff);
      }
      attempt += 1;
    }

    return {
      traceId,
      to,
      subject,
      status: 'FAILED',
      errorMessage: 'Unexpected retry exit'
    };
  }
}
