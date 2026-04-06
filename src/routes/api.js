const express = require('express');
const {
  listTasks,
  createTask,
  getTaskById,
  reviewTask,
  postReviewActions
} = require('../services/reviewService');

const router = express.Router();

router.get('/health', (req, res) => {
  res.json({ ok: true, timestamp: new Date().toISOString() });
});

router.get('/tasks', (req, res) => {
  const tasks = listTasks(req.query.status);
  res.json({ data: tasks });
});

router.post('/tasks', (req, res) => {
  const required = ['customer_name', 'customer_email', 'order_no', 'issue_type', 'issue_description'];
  const missing = required.filter((f) => !req.body[f]);
  if (missing.length > 0) {
    return res.status(400).json({ message: `缺少字段: ${missing.join(', ')}` });
  }

  const task = createTask(req.body);
  return res.status(201).json({ data: task });
});

router.post('/tasks/:id/review', async (req, res) => {
  const id = Number(req.params.id);
  if (!Number.isInteger(id) || id <= 0) {
    return res.status(400).json({ message: '非法任务ID' });
  }

  const { status, reviewer, review_note } = req.body;
  if (!['APPROVED', 'REJECTED'].includes(status)) {
    return res.status(400).json({ message: 'status 必须为 APPROVED 或 REJECTED' });
  }
  if (!reviewer) {
    return res.status(400).json({ message: 'reviewer 不能为空' });
  }

  const updated = reviewTask(id, { status, reviewer, review_note });
  if (!updated) {
    return res.status(404).json({ message: '任务不存在' });
  }

  try {
    const synced = await postReviewActions(id);
    return res.json({ data: synced });
  } catch (err) {
    return res.status(500).json({
      message: '审核完成，但后续自动动作失败',
      error: err.message,
      data: getTaskById(id)
    });
  }
});

module.exports = router;
