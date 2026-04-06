CREATE TABLE IF NOT EXISTS `email_records` (
  `id` BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '主键',
  `message_id` VARCHAR(255) NOT NULL COMMENT '邮件唯一ID',
  `sender` VARCHAR(255) NOT NULL COMMENT '发件人',
  `recipients` TEXT NOT NULL COMMENT '收件人列表',
  `subject` VARCHAR(500) NOT NULL COMMENT '邮件主题',
  `body_text` LONGTEXT NOT NULL COMMENT '邮件原文',
  `cleaned_text` LONGTEXT NULL COMMENT '清洗后文本',
  `ai_result` JSON NULL COMMENT 'AI分析结果',
  `structured_data` JSON NULL COMMENT '结构化数据',
  `draft_reply` LONGTEXT NULL COMMENT '草稿回复',
  `status` ENUM('PENDING','APPROVED','SENT','REGENERATED','HIGH_RISK','MANUAL') NOT NULL DEFAULT 'PENDING' COMMENT '审核状态',
  `risk_level` VARCHAR(20) NOT NULL DEFAULT 'LOW' COMMENT '风险等级',
  `erp_sync_status` VARCHAR(20) NOT NULL DEFAULT 'PENDING' COMMENT 'ERP同步状态',
  `last_error` TEXT NULL COMMENT '最近一次错误',
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  UNIQUE KEY `uk_message_id` (`message_id`),
  KEY `idx_status_created` (`status`, `created_at`),
  KEY `idx_sender` (`sender`),
  KEY `idx_risk_level` (`risk_level`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='邮件处理主表';

CREATE TABLE IF NOT EXISTS `review_actions` (
  `id` BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '主键',
  `email_id` BIGINT NOT NULL COMMENT '邮件ID',
  `action` VARCHAR(50) NOT NULL COMMENT '动作',
  `operator` VARCHAR(100) NOT NULL DEFAULT 'system' COMMENT '操作人',
  `remark` TEXT NULL COMMENT '备注',
  `payload` JSON NULL COMMENT '附加数据',
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  KEY `idx_email_action` (`email_id`, `action`),
  KEY `idx_created_at` (`created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='审核动作日志';
