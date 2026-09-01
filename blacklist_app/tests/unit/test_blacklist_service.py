"""Pruebas unitarias de blacklist_service.

Autores: Jesús Mendoza, Rafael Beleño, Juan Díaz, Yeison Arrieta.
"""
from datetime import datetime
from unittest.mock import MagicMock
from src.services.blacklist_service import BlacklistService


def test_add_to_blacklist_success(mocker):
    service = BlacklistService()
    fake_blacklist = MagicMock()
    fake_blacklist.id = "some-id"
    fake_blacklist.email = "user@example.com"
    fake_blacklist.created_at = datetime(2026, 1, 1, 12, 0, 0)

    mocker.patch.object(service.repository, "create", return_value=fake_blacklist)

    result = service.add_to_blacklist(
        email="user@example.com",
        app_uuid="123e4567-e89b-12d3-a456-426614174000",
        blocked_reason="Spam",
        ip_address="127.0.0.1",
    )

    assert result["email"] == "user@example.com"
    assert result["id"] == "some-id"
    assert "added to blacklist successfully" in result["message"]
    assert result["created_at"] == "2026-01-01T12:00:00"


def test_check_blacklist_found(mocker):
    service = BlacklistService()
    fake_blacklist = MagicMock()
    fake_blacklist.blocked_reason = "Spam"

    mocker.patch.object(service.repository, "get_by_email", return_value=fake_blacklist)

    result = service.check_blacklist("user@example.com")

    assert result["is_blacklisted"] is True
    assert result["email"] == "user@example.com"
    assert result["blocked_reason"] == "Spam"


def test_check_blacklist_not_found(mocker):
    service = BlacklistService()
    mocker.patch.object(service.repository, "get_by_email", return_value=None)

    result = service.check_blacklist("nobody@example.com")

    assert result["is_blacklisted"] is False
    assert result["email"] == "nobody@example.com"
    assert result["blocked_reason"] is None