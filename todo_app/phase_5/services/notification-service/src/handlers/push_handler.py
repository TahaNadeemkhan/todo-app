"""
T131-T132: PushHandler - Send push notifications via Firebase Cloud Messaging (FCM)
"""

import logging
import json
from datetime import datetime
from typing import Optional

import firebase_admin
from firebase_admin import credentials, messaging

from config import get_settings

logger = logging.getLogger(__name__)


class PushHandler:
    """Handler for sending push notifications via Firebase Cloud Messaging."""

    def __init__(self):
        self.settings = get_settings()
        self._app = None
        self._initialized = False

        # Initialize Firebase if credentials are configured
        if self.settings.fcm_configured:
            try:
                self._initialize_firebase()
                self._initialized = True
            except Exception as e:
                logger.error(f"Failed to initialize Firebase: {e}")

    def _initialize_firebase(self):
        """Initialize Firebase Admin SDK."""
        if self.settings.fcm_credentials_json:
            # Parse JSON credentials from string
            cred_dict = json.loads(self.settings.fcm_credentials_json)
            cred = credentials.Certificate(cred_dict)

            # Initialize app if not already initialized
            if not firebase_admin._apps:
                self._app = firebase_admin.initialize_app(
                    cred,
                    options={"projectId": self.settings.fcm_project_id}
                )
            else:
                self._app = firebase_admin.get_app()

            logger.info("Firebase Admin SDK initialized successfully")

    async def send_reminder_push(
        self,
        user_id: str,
        task_title: str,
        task_description: Optional[str],
        due_at: datetime,
        remind_before: str,
        fcm_token: Optional[str] = None
    ) -> bool:
        """
        Send push notification for task reminder.

        Args:
            user_id: User UUID
            task_title: Title of the task
            task_description: Description of the task
            due_at: When the task is due
            remind_before: ISO 8601 duration string (PT1H, P1D, P1W)
            fcm_token: User's FCM device token (retrieved from user profile)

        Returns:
            True if push sent successfully, False otherwise
        """
        logger.info(f"send_reminder_push called for user: {user_id}")

        if not self._initialized:
            logger.warning("FCM not configured, skipping push notification")
            return False

        if not fcm_token:
            logger.warning(f"No FCM token found for user {user_id}, skipping push")
            return False

        try:
            # Parse remind_before for human-readable text
            remind_text = remind_before.replace("PT", "").replace("P", "")
            if "H" in remind_text:
                remind_text = remind_text.replace("H", " hour")
            elif "D" in remind_text:
                remind_text = remind_text.replace("D", " day")
            elif "W" in remind_text:
                remind_text = remind_text.replace("W", " week")

            due_date_str = due_at.strftime("%B %d, %Y at %I:%M %p")

            # Construct FCM message
            message = messaging.Message(
                notification=messaging.Notification(
                    title=f"⏰ Reminder: {task_title}",
                    body=f"Due {remind_text} from now ({due_date_str})",
                ),
                data={
                    "type": "task_reminder",
                    "task_title": task_title,
                    "task_description": task_description or "",
                    "due_at": due_at.isoformat(),
                    "click_action": "FLUTTER_NOTIFICATION_CLICK",  # For mobile apps
                },
                token=fcm_token,
                android=messaging.AndroidConfig(
                    priority="high",
                    notification=messaging.AndroidNotification(
                        icon="ic_notification",
                        color="#667eea",
                        sound="default",
                    ),
                ),
                apns=messaging.APNSConfig(
                    payload=messaging.APNSPayload(
                        aps=messaging.Aps(
                            sound="default",
                            badge=1,
                        )
                    )
                ),
            )

            # Send message
            response = messaging.send(message)
            logger.info(f"Push notification sent successfully: {response}")
            return True

        except messaging.UnregisteredError:
            logger.error(f"FCM token invalid or expired for user {user_id}")
            return False
        except Exception as e:
            logger.error(f"Failed to send push notification: {e}")
            return False

    async def send_test_notification(self, fcm_token: str) -> bool:
        """Send a test push notification to verify FCM setup."""
        if not self._initialized:
            logger.warning("FCM not configured")
            return False

        try:
            message = messaging.Message(
                notification=messaging.Notification(
                    title="iTasks Test Notification",
                    body="Your push notifications are working!",
                ),
                token=fcm_token,
            )

            response = messaging.send(message)
            logger.info(f"Test notification sent: {response}")
            return True

        except Exception as e:
            logger.error(f"Failed to send test notification: {e}")
            return False
