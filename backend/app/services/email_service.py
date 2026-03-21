"""Email service: sends 6-digit OTP via SMTP using aiosmtplib."""

import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from loguru import logger

from app.core.config import get_settings

settings = get_settings()

OTP_HTML_TEMPLATE = """\
<!DOCTYPE html>
<html>
<body style="font-family: Arial, sans-serif; background: #f4f4f4; padding: 40px;">
  <div style="max-width: 480px; margin: auto; background: #fff; border-radius: 12px;
              padding: 32px; box-shadow: 0 2px 12px rgba(0,0,0,0.08);">
    <h2 style="color: #1a1a2e; margin-bottom: 8px;">🔐 Your Login Code</h2>
    <p style="color: #555; margin-bottom: 24px;">
      Use the following one-time password to sign in to the Enterprise RAG Chatbot.
      It will expire in <strong>{expire_minutes} minutes</strong>.
    </p>
    <div style="font-size: 36px; font-weight: bold; letter-spacing: 12px;
                color: #0f3460; background: #e8f0fe; border-radius: 8px;
                padding: 16px 24px; text-align: center;">
      {otp}
    </div>
    <p style="color: #999; font-size: 12px; margin-top: 24px;">
      If you did not request this code, please ignore this email.
    </p>
  </div>
</body>
</html>
"""


async def send_otp_email(to_email: str, otp: str) -> None:
    """Send the OTP to the given email asynchronously."""
    if not settings.smtp_user or not settings.smtp_password:
        # Dev mode: just log the OTP
        logger.warning(f"[DEV MODE] OTP for {to_email}: {otp}")
        return

    message = MIMEMultipart("alternative")
    message["Subject"] = "Your Enterprise RAG Chatbot OTP"
    message["From"] = settings.smtp_user
    message["To"] = to_email

    html_content = OTP_HTML_TEMPLATE.format(
        otp=otp,
        expire_minutes=settings.otp_expire_minutes,
    )
    message.attach(MIMEText(html_content, "html"))

    try:
        await aiosmtplib.send(
            message,
            hostname=settings.smtp_host,
            port=settings.smtp_port,
            start_tls=True,
            username=settings.smtp_user,
            password=settings.smtp_password,
        )
        logger.info(f"OTP email sent successfully to {to_email}")
    except Exception as exc:
        # Fallback to console logging if email fails
        logger.error(f"Failed to send OTP email: {exc}")
        logger.warning(f"--- [EMERGENCY FALLBACK] ---")
        logger.warning(f"OTP FOR {to_email}: {otp}")
        logger.warning(f"----------------------------")
        # Do not raise error to allow dev to continue
        return
