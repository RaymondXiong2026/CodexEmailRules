import nodemailer from 'nodemailer';

export class SMTPClientPool {
  constructor(accounts = [], defaultAccount = '') {
    if (!accounts.length) {
      throw new Error('SMTP account list is empty. Set SMTP_ACCOUNTS in .env');
    }

    this.defaultAccount = defaultAccount || accounts[0].name;
    this.pool = new Map(
      accounts.map((account) => [
        account.name,
        {
          fromName: account.fromName || account.name,
          fromEmail: account.fromEmail || account.user,
          transporter: nodemailer.createTransport({
            host: account.host,
            port: account.port,
            secure: account.secure,
            auth: {
              user: account.user,
              pass: account.pass
            }
          })
        }
      ])
    );
  }

  getClient(senderName) {
    const key = senderName || this.defaultAccount;
    const client = this.pool.get(key);
    if (!client) {
      throw new Error(`SMTP sender not found: ${key}`);
    }
    return client;
  }
}
