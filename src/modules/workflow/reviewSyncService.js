export class ReviewSyncService {
  constructor({ emailSender, erpClient }) {
    this.emailSender = emailSender;
    this.erpClient = erpClient;
  }

  async processReviewAction({ mail, action, draftReply, editor }) {
    const now = new Date().toISOString();

    if (action === 'SEND_NOW' || action === 'SEND_AFTER_EDIT') {
      const sendResult = await this.emailSender.sendReply({
        senderName: mail.senderAccount,
        to: mail.customerEmail,
        cc: mail.cc || [],
        bcc: mail.bcc || [],
        subject: `Re: ${mail.subject}`,
        html: draftReply,
        traceId: mail.id
      });

      if (sendResult.status !== 'SUCCESS') {
        return {
          mailId: mail.id,
          status: 'SEND_FAILED',
          sendResult,
          updatedAt: now,
          updatedBy: editor
        };
      }

      const erpResult = await this.erpClient.write({
        resourceType: 'order',
        parsedMailData: mail.parsedData,
        consistencyKeys: ['order_id', 'email']
      });

      return {
        mailId: mail.id,
        status: erpResult.status === 'SUCCESS' ? 'SENT' : 'SENT_ERP_PENDING',
        sendResult,
        erpResult,
        updatedAt: now,
        updatedBy: editor
      };
    }

    if (action === 'REGENERATE') {
      return {
        mailId: mail.id,
        status: 'REJECTED',
        reason: '人工退回重生成',
        updatedAt: now,
        updatedBy: editor
      };
    }

    if (action === 'MARK_RISK') {
      return {
        mailId: mail.id,
        status: 'HIGH_RISK',
        reason: '客服标记高风险',
        updatedAt: now,
        updatedBy: editor
      };
    }

    return {
      mailId: mail.id,
      status: 'PENDING',
      updatedAt: now,
      updatedBy: editor
    };
  }
}
