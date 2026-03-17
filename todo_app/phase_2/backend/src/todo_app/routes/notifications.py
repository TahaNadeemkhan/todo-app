"""
Notification API routes.
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from pydantic import BaseModel

from ..db import get_session
from ..deps import ValidatedUserId
from ..models import Notification

router = APIRouter(prefix="/api", tags=["notifications"])
SessionDep = Annotated[Session, Depends(get_session)]


class NotificationResponse(BaseModel):
    """Notification response model."""
    id: int
    user_id: str
    task_id: int | None
    type: str
    title: str
    message: str
    email_sent_to: str
    is_read: bool
    sent_at: str


class MarkReadRequest(BaseModel):
    """Request to mark notifications as read."""
    notification_ids: list[int]


@router.get("/{user_id}/notifications", response_model=list[NotificationResponse])
async def get_notifications(
    user_id: ValidatedUserId,
    session: SessionDep,
    unread_only: bool = False,
):
    """Get all notifications for a user."""
    query = select(Notification).where(Notification.user_id == user_id)
    if unread_only:
        query = query.where(Notification.is_read == False)
    query = query.order_by(Notification.sent_at.desc())

    notifications = session.exec(query).all()

    return [
        NotificationResponse(
            id=n.id,
            user_id=n.user_id,
            task_id=n.task_id,
            type=n.type,
            title=n.title,
            message=n.message,
            email_sent_to=n.email_sent_to,
            is_read=n.is_read,
            sent_at=n.sent_at.isoformat(),
        )
        for n in notifications
    ]


@router.get("/{user_id}/notifications/unread-count")
async def get_unread_count(
    user_id: ValidatedUserId,
    session: SessionDep,
):
    """Get count of unread notifications."""
    query = select(Notification).where(
        Notification.user_id == user_id,
        Notification.is_read == False
    )
    notifications = session.exec(query).all()

    return {"unread_count": len(notifications)}


@router.patch("/{user_id}/notifications/mark-read")
async def mark_notifications_read(
    user_id: ValidatedUserId,
    request: MarkReadRequest,
    session: SessionDep,
):
    """Mark notifications as read."""
    for notification_id in request.notification_ids:
        notification = session.get(Notification, notification_id)
        if notification and notification.user_id == user_id:
            notification.is_read = True
            session.add(notification)

    session.commit()
    return {"message": "Notifications marked as read"}


@router.patch("/{user_id}/notifications/mark-all-read")
async def mark_all_read(
    user_id: ValidatedUserId,
    session: SessionDep,
):
    """Mark all notifications as read."""
    query = select(Notification).where(
        Notification.user_id == user_id,
        Notification.is_read == False
    )
    notifications = session.exec(query).all()

    for notification in notifications:
        notification.is_read = True
        session.add(notification)

    session.commit()
    return {"message": f"Marked {len(notifications)} notifications as read"}


@router.delete("/{user_id}/notifications/{notification_id}")
async def delete_notification(
    user_id: ValidatedUserId,
    notification_id: int,
    session: SessionDep,
):
    """Delete a notification."""
    notification = session.get(Notification, notification_id)
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")

    if notification.user_id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized")

    session.delete(notification)
    session.commit()
    return {"message": "Notification deleted"}
