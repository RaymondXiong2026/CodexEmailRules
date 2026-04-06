import { env } from '../config/env.js';
import { SMTPClientPool } from '../modules/mailer/smtpClient.js';
import { EmailSendService } from '../modules/mailer/sendService.js';
import { ERPFailureQueue } from '../modules/erp/retryQueue.js';
import { ERPClient } from '../modules/erp/erpClient.js';
import { ReviewSyncService } from '../modules/workflow/reviewSyncService.js';

async function main() {
  const smtpPool = new SMTPClientPool(env.smtp.accounts, env.smtp.defaultAccount);
  const emailSender = new EmailSendService({
    smtpClientPool: smtpPool,
    signature: env.smtp.signature,
    maxRetry: env.smtp.maxRetry,
    retryBaseMs: env.smtp.retryBaseMs,
    alertWebhook: env.smtp.alertWebhook,
    logLevel: env.logLevel
  });

  const failureQueue = new ERPFailureQueue(env.erp.failureCacheFile);
  const erpClient = new ERPClient({
    provider: env.erp.provider,
    baseUrl: env.erp.baseUrl,
    apiKey: env.erp.apiKey,
    timeoutMs: env.erp.timeoutMs,
    maxRetry: env.erp.maxRetry,
    retryBaseMs: env.erp.retryBaseMs,
    fieldMapping: env.erp.fieldMapping,
    failureQueue,
    logLevel: env.logLevel
  });

  const reviewSyncService = new ReviewSyncService({ emailSender, erpClient });

  const result = await reviewSyncService.processReviewAction({
    mail: {
      id: 'mail-1001',
      subject: 'Where is my package?',
      customerEmail: 'customer@example.com',
      senderAccount: env.smtp.defaultAccount,
      parsedData: {
        orderNo: 'SO-2026-1001',
        customerName: 'Alice',
        customerEmail: 'customer@example.com',
        amount: 199.99,
        productName: 'Winter Jacket',
        address: 'No.88 Market St',
        phone: '+1-888-000-9999'
      }
    },
    action: 'SEND_AFTER_EDIT',
    draftReply: '<p>Hi Alice, your order has been shipped and is expected tomorrow.</p>',
    editor: 'agent.tina'
  });

  console.log('review action result:', result);

  // Retry failed ERP writes from local cache
  await erpClient.retryFailed();
}

main().catch((error) => {
  console.error('integration example failed:', error.message);
  process.exitCode = 1;
});
