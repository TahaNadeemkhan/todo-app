"""
T125: Unit tests for EmailHandler
"""

import pytest
from datetime import datetime
from unittest.mock import Mock, patch, AsyncMock
from handlers.email_handler import EmailHandler


@pytest.fixture
def email_handler():
    """Create EmailHandler instance for testing."""
    return EmailHandler()


@pytest.mark.asyncio
async def test_send_reminder_email_success_brevo(email_handler, monkeypatch):
    """Test successful email sending via Brevo."""
    # Mock settings to use Brevo
    monkeypatch.setattr(email_handler.settings, "email_configured", True)
    monkeypatch.setattr(email_handler.settings, "use_brevo", True)

    # Mock Brevo API
    mock_brevo_response = Mock()
    email_handler._brevo_api = Mock()
    email_handler._brevo_api.send_transac_email = Mock(return_value=mock_brevo_response)

    # Test data
    to_email = "user@example.com"
    task_title = "Buy groceries"
    task_description = "Milk, bread, eggs"
    due_at = datetime(2026, 1, 10, 18, 0, 0)
    remind_before = "PT1H"

    # Execute
    result = await email_handler.send_reminder_email(
        to_email, task_title, task_description, due_at, remind_before
    )

    # Assert
    assert result is True
    email_handler._brevo_api.send_transac_email.assert_called_once()


@pytest.mark.asyncio
async def test_send_reminder_email_success_smtp(email_handler, monkeypatch):
    """Test successful email sending via SMTP."""
    # Mock settings to use SMTP
    monkeypatch.setattr(email_handler.settings, "email_configured", True)
    monkeypatch.setattr(email_handler.settings, "use_brevo", False)
    monkeypatch.setattr(email_handler.settings, "smtp_host", "smtp.example.com")
    monkeypatch.setattr(email_handler.settings, "smtp_port", 587)
    monkeypatch.setattr(email_handler.settings, "smtp_username", "user")
    monkeypatch.setattr(email_handler.settings, "smtp_password", "pass")

    # Mock SMTP
    with patch("handlers.email_handler.smtplib.SMTP") as mock_smtp:
        mock_server = Mock()
        mock_smtp.return_value.__enter__.return_value = mock_server

        # Test data
        to_email = "user@example.com"
        task_title = "Buy groceries"
        due_at = datetime(2026, 1, 10, 18, 0, 0)

        # Execute
        result = await email_handler.send_reminder_email(
            to_email, task_title, None, due_at, "PT1H"
        )

        # Assert
        assert result is True
        mock_server.starttls.assert_called_once()
        mock_server.login.assert_called_once()
        mock_server.sendmail.assert_called_once()


@pytest.mark.asyncio
async def test_send_reminder_email_not_configured(email_handler, monkeypatch):
    """Test email sending when email is not configured."""
    monkeypatch.setattr(email_handler.settings, "email_configured", False)

    result = await email_handler.send_reminder_email(
        "user@example.com", "Test Task", None, datetime.now(), "PT1H"
    )

    assert result is False


@pytest.mark.asyncio
async def test_send_reminder_email_brevo_failure(email_handler, monkeypatch):
    """Test email sending when Brevo API fails."""
    monkeypatch.setattr(email_handler.settings, "email_configured", True)
    monkeypatch.setattr(email_handler.settings, "use_brevo", True)

    # Mock Brevo API to raise exception
    email_handler._brevo_api = Mock()
    email_handler._brevo_api.send_transac_email = Mock(
        side_effect=Exception("Brevo API error")
    )

    result = await email_handler.send_reminder_email(
        "user@example.com", "Test Task", None, datetime.now(), "PT1H"
    )

    assert result is False


def test_get_reminder_email_template(email_handler):
    """Test email template generation."""
    task_title = "Buy groceries"
    task_description = "Milk, bread, eggs"
    due_at = datetime(2026, 1, 10, 18, 0, 0)
    remind_before = "PT1H"

    subject, html_body = email_handler._get_reminder_email_template(
        task_title, task_description, due_at, remind_before
    )

    assert "⏰ Reminder" in subject
    assert task_title in subject
    assert task_title in html_body
    assert task_description in html_body
    assert "January 10, 2026" in html_body
