"""
T129-T130: EmailHandler - Send email notifications via Brevo API or SMTP
Adapted from Phase 3 EmailService for event-driven notification service.
"""

import smtplib
import logging
import asyncio
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from typing import Optional

import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException

from config import get_settings

logger = logging.getLogger(__name__)

# Thread pool for running sync operations in async context
_executor = ThreadPoolExecutor(max_workers=3)


class EmailHandler:
    """Handler for sending email notifications for reminders."""

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

    def _get_reminder_email_template(
        self,
        task_title: str,
        task_description: Optional[str],
        due_at: datetime,
        remind_before: str
    ) -> tuple[str, str]:
        """
        Generate reminder email subject and HTML body.

        Args:
            task_title: Title of the task
            task_description: Description of the task
            due_at: When the task is due
            remind_before: Human-readable reminder timing (e.g., "1 hour", "1 day")

        Returns:
            Tuple of (subject, html_body)
        """
        due_date_str = due_at.strftime("%B %d, %Y at %I:%M %p")

        # Parse remind_before for human-readable text
        remind_text = remind_before.replace("PT", "").replace("P", "")
        if "H" in remind_text:
            remind_text = remind_text.replace("H", " hour")
        elif "D" in remind_text:
            remind_text = remind_text.replace("D", " day")
        elif "W" in remind_text:
            remind_text = remind_text.replace("W", " week")

        subject = f"⏰ Reminder: {task_title}"

        html_body = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; border-radius: 10px 10px 0 0;">
                <h1 style="color: white; margin: 0; font-size: 24px;">⏰ Task Reminder</h1>
            </div>
            <div style="background: #f8f9fa; padding: 30px; border-radius: 0 0 10px 10px;">
                <p style="color: #666; font-size: 16px; margin-top: 0;">
                    This is a friendly reminder about your upcoming task:
                </p>
                <div style="background: white; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #667eea;">
                    <h2 style="color: #333; margin-top: 0;">{task_title}</h2>
                    <p style="color: #666;">{task_description or 'No description provided'}</p>
                </div>
                <div style="background: white; padding: 15px; border-radius: 8px; margin-top: 20px;">
                    <p style="margin: 5px 0; color: #666;"><strong>Due:</strong> {due_date_str}</p>
                    <p style="margin: 5px 0; color: #888;"><strong>Reminder:</strong> {remind_text} before due date</p>
                </div>
                <div style="text-align: center; margin-top: 30px;">
                    <p style="color: #667eea; font-weight: bold;">Don't forget to complete your task! 🎯</p>
                </div>
                <p style="color: #888; font-size: 12px; margin-top: 30px; text-align: center;">
                    This is an automated reminder from iTasks
                </p>
            </div>
        </div>
        """

        return subject, html_body

    def _send_via_brevo(self, to_email: str, subject: str, html_body: str) -> bool:
        """Send email via Brevo API."""
        try:
            logger.info(f"Sending via Brevo to: {to_email}")

            send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
                to=[{"email": to_email}],
                sender={
                    "name": self.settings.smtp_from_name,
                    "email": self.settings.smtp_from_email
                },
                subject=subject,
                html_content=html_body,
            )

            response = self._brevo_api.send_transac_email(send_smtp_email)
            logger.info(f"Brevo response: {response}")
            return True

        except ApiException as e:
            logger.error(f"Brevo API Error: {e}")
            return False
        except Exception as e:
            logger.error(f"Brevo Error: {e}")
            return False

    def _send_via_smtp(
        self,
        to_email: str,
        subject: str,
        html_body: str,
        plain_text: str
    ) -> bool:
        """Send email via SMTP (for local development)."""
        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = f"{self.settings.smtp_from_name} <{self.settings.smtp_from_email}>"
            msg["To"] = to_email

            msg.attach(MIMEText(plain_text, "plain"))
            msg.attach(MIMEText(html_body, "html"))

            smtp_port = self.settings.smtp_port
            logger.info(f"Connecting to SMTP: {self.settings.smtp_host}:{smtp_port}")

            if smtp_port == 465:
                with smtplib.SMTP_SSL(
                    self.settings.smtp_host, smtp_port, timeout=30
                ) as server:
                    server.login(
                        self.settings.smtp_username, self.settings.smtp_password
                    )
                    server.sendmail(
                        self.settings.smtp_from_email, to_email, msg.as_string()
                    )
            else:
                with smtplib.SMTP(
                    self.settings.smtp_host, smtp_port, timeout=30
                ) as server:
                    server.starttls()
                    server.login(
                        self.settings.smtp_username, self.settings.smtp_password
                    )
                    server.sendmail(
                        self.settings.smtp_from_email, to_email, msg.as_string()
                    )

            logger.info("SMTP email sent successfully")
            return True

        except Exception as e:
            logger.error(f"SMTP Error: {e}")
            return False

    async def send_reminder_email(
        self,
        to_email: str,
        task_title: str,
        task_description: Optional[str],
        due_at: datetime,
        remind_before: str,
    ) -> bool:
        """
        Send reminder email notification asynchronously.

        Args:
            to_email: Recipient email address
            task_title: Title of the task
            task_description: Description of the task
            due_at: When the task is due
            remind_before: ISO 8601 duration string (PT1H, P1D, P1W)

        Returns:
            True if email sent successfully, False otherwise
        """
        logger.info(f"send_reminder_email called for: {to_email}")

        if not self.settings.email_configured:
            logger.warning("Email not configured, skipping")
            return False

        try:
            subject, html_body = self._get_reminder_email_template(
                task_title, task_description, due_at, remind_before
            )
            plain_text = f"Reminder: {task_title} is due on {due_at.strftime('%B %d, %Y at %I:%M %p')}"

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

            logger.info(f"Email send result: {result}")
            return result

        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            return False
