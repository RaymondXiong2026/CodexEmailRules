import fs from 'node:fs/promises';
import path from 'node:path';

export class ERPFailureQueue {
  constructor(cacheFile) {
    this.cacheFile = path.resolve(cacheFile);
  }

  async push(payload) {
    const data = await this.readAll();
    data.push({ ...payload, failedAt: new Date().toISOString() });
    await this.writeAll(data);
  }

  async flush(handler) {
    const data = await this.readAll();
    if (!data.length) return;

    const remain = [];
    for (const item of data) {
      try {
        await handler(item);
      } catch (error) {
        remain.push(item);
      }
    }

    await this.writeAll(remain);
  }

  async readAll() {
    try {
      const raw = await fs.readFile(this.cacheFile, 'utf-8');
      return JSON.parse(raw);
    } catch {
      return [];
    }
  }

  async writeAll(items) {
    await fs.mkdir(path.dirname(this.cacheFile), { recursive: true });
    await fs.writeFile(this.cacheFile, JSON.stringify(items, null, 2), 'utf-8');
  }
}
