import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from app.core.config import settings


def render_base_email(
    title: str,
    body_lines: list[str],
    highlight: str | None = None,
    footer_note: str | None = None,
) -> str:
    """
    A single reusable HTML template for all transactional emails.
    `body_lines` are rendered as separate paragraphs.
    `highlight` renders as a large emphasized block (e.g. the OTP code).
    """
    paragraphs = "".join(f"<p style='margin:0 0 16px;color:#374151;font-size:15px;line-height:1.6;'>{line}</p>" for line in body_lines)

    highlight_html = ""
    if highlight:
        highlight_html = f"""
        <div style="margin:24px 0;text-align:center;">
            <span style="display:inline-block;padding:14px 28px;background:#f3f4f6;
                         border-radius:8px;font-size:28px;font-weight:700;letter-spacing:6px;
                         color:#111827;">{highlight}</span>
        </div>
        """

    footer_html = ""
    if footer_note:
        footer_html = f"<p style='margin-top:24px;color:#9ca3af;font-size:13px;'>{footer_note}</p>"

    return f"""\
<html>
  <body style="margin:0;padding:0;background:#f9fafb;font-family:Arial,Helvetica,sans-serif;">
    <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="padding:32px 0;">
      <tr>
        <td align="center">
          <table role="presentation" width="480" cellpadding="0" cellspacing="0"
                 style="background:#ffffff;border-radius:12px;padding:32px;box-shadow:0 1px 3px rgba(0,0,0,0.08);">
            <tr>
              <td>
                <h2 style="margin:0 0 20px;color:#111827;font-size:20px;">{title}</h2>
                {paragraphs}
                {highlight_html}
                {footer_html}
              </td>
            </tr>
          </table>
          <p style="margin-top:16px;color:#d1d5db;font-size:12px;">
            {settings.MAIL_FROM_NAME}
          </p>
        </td>
      </tr>
    </table>
  </body>
</html>
"""


def send_email(to_email: str, subject: str, html_content: str) -> None:
    message = MIMEMultipart("alternative")
    message["Subject"] = subject
    message["From"] = f"{settings.MAIL_FROM_NAME} <{settings.MAIL_FROM_ADDRESS}>"
    message["To"] = to_email

    message.attach(MIMEText(html_content, "html"))

    if settings.MAIL_SSL_TLS:
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(settings.MAIL_HOST, settings.MAIL_PORT, context=context) as server:
            server.login(settings.MAIL_USERNAME, settings.MAIL_PASSWORD)
            server.sendmail(settings.MAIL_FROM_ADDRESS, to_email, message.as_string())
    else:
        with smtplib.SMTP(settings.MAIL_HOST, settings.MAIL_PORT) as server:
            if settings.MAIL_STARTTLS:
                context = ssl.create_default_context()
                server.starttls(context=context)
            server.login(settings.MAIL_USERNAME, settings.MAIL_PASSWORD)
            server.sendmail(settings.MAIL_FROM_ADDRESS, to_email, message.as_string())


def send_otp_email(to_email: str, otp: str, ttl_minutes: int) -> None:
    html = render_base_email(
        title="Reset your password",
        body_lines=[
            "We received a request to reset your password.",
            "Use the one-time code below to continue. This code is valid for "
            f"{ttl_minutes} minutes.",
        ],
        highlight=otp,
        footer_note="If you didn't request this, you can safely ignore this email.",
    )
    send_email(to_email, subject="Your password reset code", html_content=html)