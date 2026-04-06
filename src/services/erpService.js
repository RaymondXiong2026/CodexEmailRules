const axios = require('axios');
const config = require('../config');

function canCallRealErp() {
  return Boolean(config.erp.baseUrl && config.erp.apiKey);
}

async function pushReviewToErp(task) {
  const payload = {
    orderNo: task.order_no,
    customerName: task.customer_name,
    customerEmail: task.customer_email,
    issueType: task.issue_type,
    issueDescription: task.issue_description,
    reviewStatus: task.status,
    reviewer: task.reviewer,
    reviewNote: task.review_note,
    reviewedAt: task.reviewed_at
  };

  if (!canCallRealErp()) {
    console.log('[MockERP] ERP 未完整配置，使用模拟写入:', payload);
    return { mocked: true };
  }

  await axios.post(`${config.erp.baseUrl}/api/reviews/sync`, payload, {
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${config.erp.apiKey}`
    },
    timeout: config.erp.timeoutMs
  });

  return { mocked: false };
}

module.exports = {
  pushReviewToErp
};
