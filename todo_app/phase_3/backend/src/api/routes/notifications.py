"""
Notification API endpoints for Phase 3.
Adapted from Phase 2 with async/await patterns.
"""

from typing import Sequence
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from sqlmodel import select

from db import get_async_session
from models.notification import Notification

router = APIRouter(prefix="/api", tags=["notifications"])


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
    user_id: str,
    session: AsyncSession = Depends(get_async_session),
    unread_only: bool = False,
) -> Sequence[NotificationResponse]:
    """Get all notifications for a user."""
    query = select(Notification).where(Notification.user_id == user_id)
    if unread_only:
        query = query.where(Notification.is_read == False)
    query = query.order_by(Notification.sent_at.desc())

    result = await session.execute(query)
    notifications = list(result.scalars().all())

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
    user_id: str,
    session: AsyncSession = Depends(get_async_session),
) -> dict:
    """Get count of unread notifications."""
    query = select(Notification).where(
        Notification.user_id == user_id,
        Notification.is_read == False
    )
    result = await session.execute(query)
    notifications = list(result.scalars().all())

    return {"unread_count": len(notifications)}


@router.patch("/{user_id}/notifications/mark-read", status_code=status.HTTP_200_OK)
async def mark_notifications_read(
    user_id: str,
    request: MarkReadRequest,
    session: AsyncSession = Depends(get_async_session),
) -> dict:
    """Mark notifications as read."""
    for notification_id in request.notification_ids:
        # Query by ID - need to manually check ownership
        query = select(Notification).where(Notification.id == notification_id)
        result = await session.execute(query)
        notification = result.scalar_one_or_none()

        if notification and notification.user_id == user_id:
            notification.is_read = True
            session.add(notification)

    await session.commit()
    return {"message": "Notifications marked as read"}


@router.patch("/{user_id}/notifications/mark-all-read", status_code=status.HTTP_200_OK)
async def mark_all_read(
    user_id: str,
    session: AsyncSession = Depends(get_async_session),
) -> dict:
    """Mark all notifications as read."""
    query = select(Notification).where(
        Notification.user_id == user_id,
        Notification.is_read == False
    )
    result = await session.execute(query)
    notifications = list(result.scalars().all())

    for notification in notifications:
        notification.is_read = True
        session.add(notification)

    await session.commit()
    return {"message": f"Marked {len(notifications)} notifications as read"}


@router.delete("/{user_id}/notifications/{notification_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_notification(
    user_id: str,
    notification_id: int,
    session: AsyncSession = Depends(get_async_session),
) -> None:
    """Delete a notification."""
    query = select(Notification).where(Notification.id == notification_id)
    result = await session.execute(query)
    notification = result.scalar_one_or_none()

    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")

    if notification.user_id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized")

    await session.delete(notification)
    await session.commit()
    return None
