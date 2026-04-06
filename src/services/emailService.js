const nodemailer = require('nodemailer');
const config = require('../config');

function canSendRealEmail() {
  return Boolean(config.smtp.host && config.smtp.user && config.smtp.pass);
}

function getTransporter() {
  return nodemailer.createTransport({
    host: config.smtp.host,
    port: config.smtp.port,
    secure: config.smtp.secure,
    auth: {
      user: config.smtp.user,
      pass: config.smtp.pass
    }
  });
}

async function sendReviewResultMail(task) {
  const subject = `订单 ${task.order_no} 审核结果通知`;
  const html = `
    <h3>您好，${task.customer_name}</h3>
    <p>您的订单 <strong>${task.order_no}</strong> 已审核完成。</p>
    <p>审核结果：<strong>${task.status}</strong></p>
    <p>审核备注：${task.review_note || '无'}</p>
    <p>时间：${new Date().toISOString()}</p>
  `;

  if (!canSendRealEmail()) {
    console.log('[MockEmail] SMTP 未完整配置，使用模拟发送:', {
      to: task.customer_email,
      subject
    });
    return { mocked: true };
  }

  const transporter = getTransporter();
  await transporter.sendMail({
    from: config.smtp.from,
    to: task.customer_email,
    subject,
    html
  });

  return { mocked: false };
}

module.exports = {
  sendReviewResultMail
};
