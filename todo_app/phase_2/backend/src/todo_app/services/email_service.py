"""
Email notification service using Gmail SMTP.
"""

import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

from ..config import get_settings

logger = logging.getLogger(__name__)


class EmailService:
    """Service for sending email notifications."""

    def __init__(self):
        self.settings = get_settings()

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
            "task_updated": {
                "subject": f"Task Updated: {task_title}",
                "body": f"""
                <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
                    <div style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); padding: 30px; border-radius: 10px 10px 0 0;">
                        <h1 style="color: white; margin: 0; font-size: 24px;">Task Updated</h1>
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
            "task_completed": {
                "subject": f"Task Completed: {task_title}",
                "body": f"""
                <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
                    <div style="background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%); padding: 30px; border-radius: 10px 10px 0 0;">
                        <h1 style="color: white; margin: 0; font-size: 24px;">Task Completed!</h1>
                    </div>
                    <div style="background: #f8f9fa; padding: 30px; border-radius: 0 0 10px 10px;">
                        <h2 style="color: #333; margin-top: 0;">{task_title}</h2>
                        <p style="color: #666;">{task_description or 'No description provided'}</p>
                        <div style="background: #d4edda; padding: 15px; border-radius: 8px; margin-top: 20px; text-align: center;">
                            <p style="margin: 0; color: #155724; font-size: 18px;">Great job! You've completed this task.</p>
                        </div>
                        <p style="color: #888; font-size: 12px; margin-top: 30px;">This is an automated notification from iTasks.</p>
                    </div>
                </div>
                """
            },
            "task_deleted": {
                "subject": f"Task Deleted: {task_title}",
                "body": f"""
                <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
                    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; border-radius: 10px 10px 0 0;">
                        <h1 style="color: white; margin: 0; font-size: 24px;">Task Deleted</h1>
                    </div>
                    <div style="background: #f8f9fa; padding: 30px; border-radius: 0 0 10px 10px;">
                        <h2 style="color: #333; margin-top: 0;">{task_title}</h2>
                        <p style="color: #666;">This task has been removed from your list.</p>
                        <p style="color: #888; font-size: 12px; margin-top: 30px;">This is an automated notification from iTasks.</p>
                    </div>
                </div>
                """
            },
            "due_reminder": {
                "subject": f"Reminder: {task_title} is due soon!",
                "body": f"""
                <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
                    <div style="background: linear-gradient(135deg, #ff9a9e 0%, #fecfef 100%); padding: 30px; border-radius: 10px 10px 0 0;">
                        <h1 style="color: white; margin: 0; font-size: 24px;">Task Reminder</h1>
                    </div>
                    <div style="background: #f8f9fa; padding: 30px; border-radius: 0 0 10px 10px;">
                        <h2 style="color: #333; margin-top: 0;">{task_title}</h2>
                        <p style="color: #666;">{task_description or 'No description provided'}</p>
                        <div style="background: #fff3cd; padding: 15px; border-radius: 8px; margin-top: 20px;">
                            <p style="margin: 0; color: #856404;"><strong>Due:</strong> {due_date_str}</p>
                        </div>
                        <p style="color: #888; font-size: 12px; margin-top: 30px;">This is an automated notification from iTasks.</p>
                    </div>
                </div>
                """
            },
        }

        template = templates.get(notification_type, templates["task_updated"])
        return template["subject"], template["body"]

    async def send_notification(
        self,
        to_email: str,
        notification_type: str,
        task_title: str,
        task_description: str | None = None,
        due_date: datetime | None = None,
    ) -> bool:
        """Send email notification."""

        if not self.settings.email_configured:
            logger.warning("Email not configured, skipping notification")
            return False

        try:
            subject, html_body = self._get_email_template(
                notification_type, task_title, task_description, due_date
            )

            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = f"iTasks <{self.settings.email_address}>"
            msg["To"] = to_email

            # Plain text fallback
            plain_text = f"{notification_type.replace('_', ' ').title()}: {task_title}"
            msg.attach(MIMEText(plain_text, "plain"))
            msg.attach(MIMEText(html_body, "html"))

            # Send email
            with smtplib.SMTP(self.settings.smtp_host, self.settings.smtp_port) as server:
                server.starttls()
                server.login(self.settings.email_address, self.settings.email_app_password)
                server.sendmail(self.settings.email_address, to_email, msg.as_string())

            logger.info(f"Email sent successfully to {to_email}")
            return True

        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            return False


# Singleton instance
email_service = EmailService()
