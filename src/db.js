const fs = require('fs');
const path = require('path');
const Database = require('better-sqlite3');
const config = require('./config');

const dir = path.dirname(config.dbPath);
if (!fs.existsSync(dir)) {
  fs.mkdirSync(dir, { recursive: true });
}

const db = new Database(config.dbPath);

db.pragma('journal_mode = WAL');

function initDb() {
  const schemaPath = path.resolve(__dirname, 'models', 'schema.sql');
  const schema = fs.readFileSync(schemaPath, 'utf8');
  db.exec(schema);
}

initDb();

if (require.main === module) {
  console.log(`数据库初始化完成: ${config.dbPath}`);
}

module.exports = db;
