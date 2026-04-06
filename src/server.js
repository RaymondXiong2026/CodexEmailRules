const express = require('express');
const cors = require('cors');
const path = require('path');
const config = require('./config');
const apiRouter = require('./routes/api');
const { startScheduler } = require('./jobs/scheduler');

require('./db');

const app = express();

app.use(cors());
app.use(express.json());
app.use(express.static(path.resolve(__dirname, 'public')));

app.use('/api', apiRouter);

app.get('*', (req, res) => {
  res.sendFile(path.resolve(__dirname, 'public', 'index.html'));
});

app.listen(config.port, () => {
  console.log(`服务启动成功: http://localhost:${config.port}`);
  startScheduler();
});
