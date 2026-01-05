"""
Email notification service using Brevo API (production) or Gmail SMTP (local).
"""

import smtplib
import logging
import asyncio
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException

from config.settings import get_settings

logger = logging.getLogger(__name__)

# Thread pool for running sync operations in async context
_executor = ThreadPoolExecutor(max_workers=3)


class EmailService:
    """Service for sending email notifications."""

    def __init__(self):
        self.settings = get_settings()
        self._brevo_api = None

        # Configure Brevo if API key is available
        if self.settings.brevo_api_key:
            configuration = sib_api_v3_sdk.Configuration()
            configuration.api_key['api-key'] = self.settings.brevo_api_key
            self._brevo_api = sib_api_v3_sdk.TransactionalEmailsApi(
                sib_api_v3_sdk.ApiClient(configuration)
            )

    def _get_email_template(self, notification_type: str, task_title: str, task_description: str | None, due_date: datetime | None) -> tuple[str, str]:
        """Generate email subject and HTML body based on notification type."""

        due_date_str = due_date.strftime("%B %d, %Y at %I:%M %p") if due_date else "Not set"

        templates = {
            "task_created": {
                "subject": f"Task Created: {task_title}",
                "body": f"""
                <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
                    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; border-radius: 10px 10px 0 0;">
                        <h1 style="color: white; margin: 0; font-size: 24px;">New Task Created</h1>
                    </div>
                    <div style="background: #f8f9fa; padding: 30px; border-radius: 0 0 10px 10px;">
                        <h2 style="color: #333; margin-top: 0;">{task_title}</h2>
                        <p style="color: #666;">{task_description or 'No description provided'}</p>
                        <div style="background: white; padding: 15px; border-radius: 8px; margin-top: 20px;">
                            <p style="margin: 0; color: #888;"><strong>Due Date:</strong> {due_date_str}</p>
                        </div>
                        <p style="color: #888; font-size: 12px; margin-top: 30px;">This is an automated notification from iTasks.</p>
                    </div>
                </div>
                """
            },
            # Add other templates as needed
        }

        template = templates.get(notification_type, templates.get("task_created")) # Default to created if not found or update logic
        return template["subject"], template["body"]

    def _send_via_brevo(self, to_email: str, subject: str, html_body: str) -> bool:
        """Send email via Brevo API."""
        try:
            print(f"[EmailService] Sending via Brevo to: {to_email}")

            send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
                to=[{"email": to_email}],
                sender={"name": "iTasks", "email": self.settings.email_address or "noreply@itasks.app"},
                subject=subject,
                html_content=html_body,
            )

            response = self._brevo_api.send_transac_email(send_smtp_email)
            print(f"[EmailService] Brevo response: {response}")
            return True

        except ApiException as e:
            print(f"[EmailService] Brevo API Error: {e}")
            logger.error(f"Brevo failed: {e}")
            return False
        except Exception as e:
            print(f"[EmailService] Brevo Error: {e}")
            logger.error(f"Brevo failed: {e}")
            return False

    def _send_via_smtp(self, to_email: str, subject: str, html_body: str, plain_text: str) -> bool:
        """Send email via SMTP (for local development)."""
        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = f"iTasks <{self.settings.email_address}>"
            msg["To"] = to_email

            msg.attach(MIMEText(plain_text, "plain"))
            msg.attach(MIMEText(html_body, "html"))

            smtp_port = self.settings.smtp_port
            print(f"[EmailService] Connecting to SMTP: {self.settings.smtp_host}:{smtp_port}")

            if smtp_port == 465:
                with smtplib.SMTP_SSL(self.settings.smtp_host, smtp_port, timeout=30) as server:
                    server.login(self.settings.email_address, self.settings.email_app_password)
                    server.sendmail(self.settings.email_address, to_email, msg.as_string())
            else:
                with smtplib.SMTP(self.settings.smtp_host, smtp_port, timeout=30) as server:
                    server.starttls()
                    server.login(self.settings.email_address, self.settings.email_app_password)
                    server.sendmail(self.settings.email_address, to_email, msg.as_string())

            print(f"[EmailService] SMTP email sent successfully")
            return True

        except Exception as e:
            print(f"[EmailService] SMTP Error: {e}")
            logger.error(f"SMTP failed: {e}")
            return False

    async def send_notification(
        self,
        to_email: str,
        notification_type: str,
        task_title: str,
        task_description: str | None = None,
        due_date: datetime | None = None,
    ) -> bool:
        """Send email notification asynchronously."""
        print(f"[EmailService] send_notification called")
        
        if not self.settings.email_configured:
            print("[EmailService] Email not configured, skipping")
            return False

        try:
            subject, html_body = self._get_email_template(
                notification_type, task_title, task_description, due_date
            )
            plain_text = f"{notification_type.replace('_', ' ').title()}: {task_title}"

            loop = asyncio.get_event_loop()

            if self.settings.use_brevo:
                # Use Brevo API
                result = await loop.run_in_executor(
                    _executor,
                    self._send_via_brevo,
                    to_email,
                    subject,
                    html_body,
                )
            else:
                # Use SMTP
                result = await loop.run_in_executor(
                    _executor,
                    self._send_via_smtp,
                    to_email,
                    subject,
                    html_body,
                    plain_text,
                )

            print(f"[EmailService] Result: {result}")
            return result

        except Exception as e:
            print(f"[EmailService] Error: {e}")
            logger.error(f"Failed to send email: {e}")
            return False


# Singleton instance
email_service = EmailService()
