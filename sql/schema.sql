CREATE DATABASE IF NOT EXISTS shop_mail_ai DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE shop_mail_ai;

CREATE TABLE IF NOT EXISTS raw_emails (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  store_id VARCHAR(64) NOT NULL,
  message_id VARCHAR(255) NOT NULL,
  thread_id VARCHAR(255) NOT NULL,
  subject VARCHAR(512) NULL,
  sender VARCHAR(512) NULL,
  recipient VARCHAR(512) NULL,
  sent_at DATETIME NULL,
  raw_body MEDIUMTEXT NULL,
  html_body MEDIUMTEXT NULL,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  UNIQUE KEY uk_store_msg (store_id, message_id),
  KEY idx_store_thread (store_id, thread_id),
  KEY idx_store_sent (store_id, sent_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS processed_email_records (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  store_id VARCHAR(64) NOT NULL,
  message_id VARCHAR(255) NOT NULL,
  thread_id VARCHAR(255) NOT NULL,
  payload_json JSON NOT NULL,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  UNIQUE KEY uk_store_processed_msg (store_id, message_id),
  KEY idx_store_thread (store_id, thread_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
