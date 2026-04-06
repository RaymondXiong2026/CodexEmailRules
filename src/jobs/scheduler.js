const cron = require('node-cron');
const db = require('../db');
const config = require('../config');
const { runBatchPostReviewActions } = require('../services/reviewService');

function recordJobStart(jobName) {
  const startedAt = new Date().toISOString();
  const result = db
    .prepare('INSERT INTO job_runs (job_name, started_at, status) VALUES (?, ?, ?)')
    .run(jobName, startedAt, 'RUNNING');
  return result.lastInsertRowid;
}

function recordJobFinish(id, status, message) {
  const finishedAt = new Date().toISOString();
  db.prepare('UPDATE job_runs SET finished_at = ?, status = ?, message = ? WHERE id = ?').run(
    finishedAt,
    status,
    message || '',
    id
  );
}

function startScheduler() {
  cron.schedule(config.jobs.reviewScanCron, async () => {
    const runId = recordJobStart('review_sync_job');
    try {
      const result = await runBatchPostReviewActions();
      const message = `处理 ${result.total} 条，成功 ${result.successCount} 条，错误 ${result.errors.length} 条`;
      recordJobFinish(runId, 'SUCCESS', message);
      if (result.errors.length > 0) {
        console.error('[Scheduler] errors:', result.errors);
      }
    } catch (err) {
      recordJobFinish(runId, 'FAILED', err.message);
      console.error('[Scheduler] failed:', err);
    }
  });

  console.log(`[Scheduler] 已启动，表达式: ${config.jobs.reviewScanCron}`);
}

module.exports = {
  startScheduler
};
