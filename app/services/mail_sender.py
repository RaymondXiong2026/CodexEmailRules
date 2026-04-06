import smtplib
from email.mime.text import MIMEText

from app.core.config import get_settings

settings = get_settings()


class MailSender:
    async def send(self, to_address: str, subject: str, body: str) -> None:
        msg = MIMEText(body, _charset="utf-8")
        msg["Subject"] = f"Re: {subject}"
        msg["From"] = settings.smtp_user
        msg["To"] = to_address

        if settings.smtp_use_ssl:
            with smtplib.SMTP_SSL(settings.smtp_host, settings.smtp_port, timeout=20) as server:
                server.login(settings.smtp_user, settings.smtp_password)
                server.sendmail(settings.smtp_user, [to_address], msg.as_string())
        else:
            with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=20) as server:
                server.starttls()
                server.login(settings.smtp_user, settings.smtp_password)
                server.sendmail(settings.smtp_user, [to_address], msg.as_string())
