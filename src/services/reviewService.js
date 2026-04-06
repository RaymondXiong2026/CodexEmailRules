const db = require('../db');
const { sendReviewResultMail } = require('./emailService');
const { pushReviewToErp } = require('./erpService');

function listTasks(status) {
  if (status) {
    return db
      .prepare('SELECT * FROM review_tasks WHERE status = ? ORDER BY id DESC')
      .all(status);
  }
  return db.prepare('SELECT * FROM review_tasks ORDER BY id DESC').all();
}

function createTask(input) {
  const stmt = db.prepare(`
    INSERT INTO review_tasks (
      customer_name, customer_email, order_no, issue_type, issue_description, status, created_at
    ) VALUES (?, ?, ?, ?, ?, 'PENDING', ?)
  `);

  const now = new Date().toISOString();
  const result = stmt.run(
    input.customer_name,
    input.customer_email,
    input.order_no,
    input.issue_type,
    input.issue_description,
    now
  );

  return getTaskById(result.lastInsertRowid);
}

function getTaskById(id) {
  return db.prepare('SELECT * FROM review_tasks WHERE id = ?').get(id);
}

function reviewTask(id, payload) {
  const existing = getTaskById(id);
  if (!existing) {
    return null;
  }

  const now = new Date().toISOString();
  db.prepare(`
    UPDATE review_tasks
    SET status = ?, reviewer = ?, review_note = ?, reviewed_at = ?
    WHERE id = ?
  `).run(payload.status, payload.reviewer, payload.review_note || '', now, id);

  return getTaskById(id);
}

async function postReviewActions(id) {
  const task = getTaskById(id);
  if (!task || task.status === 'PENDING') {
    return null;
  }

  if (!task.email_sent) {
    await sendReviewResultMail(task);
    db.prepare('UPDATE review_tasks SET email_sent = 1 WHERE id = ?').run(id);
  }

  if (!task.erp_written) {
    await pushReviewToErp(task);
    db.prepare('UPDATE review_tasks SET erp_written = 1 WHERE id = ?').run(id);
  }

  return getTaskById(id);
}

async function runBatchPostReviewActions() {
  const pendingSync = db
    .prepare(`
      SELECT * FROM review_tasks
      WHERE status IN ('APPROVED', 'REJECTED')
        AND (email_sent = 0 OR erp_written = 0)
      ORDER BY id ASC
    `)
    .all();

  let successCount = 0;
  const errors = [];

  for (const task of pendingSync) {
    try {
      await postReviewActions(task.id);
      successCount += 1;
    } catch (err) {
      errors.push({ id: task.id, message: err.message });
    }
  }

  return {
    total: pendingSync.length,
    successCount,
    errors
  };
}

module.exports = {
  listTasks,
  createTask,
  getTaskById,
  reviewTask,
  postReviewActions,
  runBatchPostReviewActions
};
