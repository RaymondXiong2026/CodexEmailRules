import axios from 'axios';
import pino from 'pino';
import { mapFields, validateConsistency } from './mappers.js';

const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

export class ERPClient {
  constructor({ baseUrl, apiKey, timeoutMs = 8000, maxRetry = 3, retryBaseMs = 700, fieldMapping = {}, provider = 'generic', failureQueue, logLevel = 'info' }) {
    this.provider = provider;
    this.maxRetry = maxRetry;
    this.retryBaseMs = retryBaseMs;
    this.failureQueue = failureQueue;
    this.fieldMapping = fieldMapping;
    this.logger = pino({ name: 'erp-client', level: logLevel });
    this.http = axios.create({
      baseURL: baseUrl,
      timeout: timeoutMs,
      headers: {
        Authorization: `Bearer ${apiKey}`,
        'Content-Type': 'application/json'
      }
    });
  }

  endpoint(resourceType) {
    if (this.provider === 'shopify') {
      return resourceType === 'order' ? '/admin/api/2024-04/orders.json' : '/admin/api/2024-04/customers.json';
    }
    return resourceType === 'order' ? '/orders' : '/customers';
  }

  async write({ resourceType, parsedMailData, consistencyKeys = [] }) {
    const payload = mapFields(parsedMailData, this.fieldMapping);
    let attempt = 0;

    while (attempt <= this.maxRetry) {
      try {
        const endpoint = this.endpoint(resourceType);
        const response = await this.http.post(endpoint, payload);
        const data = response.data?.data || response.data || {};
        const consistent = validateConsistency(payload, data, consistencyKeys);

        const result = {
          status: consistent ? 'SUCCESS' : 'INCONSISTENT',
          provider: this.provider,
          endpoint,
          attempt,
          request: payload,
          response: data
        };

        this.logger.info(result, 'ERP write finished');

        if (!consistent) {
          throw new Error('ERP consistency validation failed');
        }

        return result;
      } catch (error) {
        this.logger.error(
          {
            resourceType,
            payload,
            attempt,
            message: error.message,
            responseData: error.response?.data
          },
          'ERP write failed'
        );

        if (attempt === this.maxRetry) {
          await this.failureQueue.push({ resourceType, parsedMailData, errorMessage: error.message });
          return {
            status: 'FAILED',
            attempt,
            errorMessage: error.message
          };
        }

        const backoff = this.retryBaseMs * 2 ** attempt;
        await sleep(backoff);
      }
      attempt += 1;
    }

    return { status: 'FAILED', errorMessage: 'Unexpected retry exit' };
  }

  async retryFailed() {
    await this.failureQueue.flush(async (item) => {
      const result = await this.write({
        resourceType: item.resourceType,
        parsedMailData: item.parsedMailData
      });
      if (result.status !== 'SUCCESS') {
        throw new Error(result.errorMessage || 'Retry failed');
      }
    });
  }
}
