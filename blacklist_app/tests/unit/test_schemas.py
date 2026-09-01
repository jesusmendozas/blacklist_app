"""Pruebas unitarias de schemas.

Autores: Jesús Mendoza, Rafael Beleño, Juan Díaz, Yeison Arrieta.
"""
import pytest
from datetime import datetime
from marshmallow import ValidationError
from src.models.blacklist import (
    BlacklistCreateSchema,
    BlacklistResponseSchema,
    BlacklistCheckResponseSchema,
)

VALID_UUID = "123e4567-e89b-12d3-a456-426614174000"


def test_create_schema_valid_data():
    schema = BlacklistCreateSchema()
    data = schema.load({
        "email": "user@example.com",
        "app_uuid": VALID_UUID,
        "blocked_reason": "Spam",
    })
    assert data["email"] == "user@example.com"
    assert data["app_uuid"] == VALID_UUID
    assert data["blocked_reason"] == "Spam"


def test_create_schema_without_optional_reason():
    schema = BlacklistCreateSchema()
    data = schema.load({"email": "user@example.com", "app_uuid": VALID_UUID})
    assert "blocked_reason" not in data or data.get("blocked_reason") is None


def test_create_schema_missing_email_raises():
    schema = BlacklistCreateSchema()
    with pytest.raises(ValidationError) as exc:
        schema.load({"app_uuid": VALID_UUID})
    assert "email" in exc.value.messages


def test_create_schema_invalid_email_raises():
    schema = BlacklistCreateSchema()
    with pytest.raises(ValidationError) as exc:
        schema.load({"email": "not-an-email", "app_uuid": VALID_UUID})
    assert "email" in exc.value.messages


def test_create_schema_missing_app_uuid_raises():
    schema = BlacklistCreateSchema()
    with pytest.raises(ValidationError) as exc:
        schema.load({"email": "user@example.com"})
    assert "app_uuid" in exc.value.messages


def test_create_schema_invalid_app_uuid_raises():
    schema = BlacklistCreateSchema()
    with pytest.raises(ValidationError) as exc:
        schema.load({"email": "user@example.com", "app_uuid": "not-a-uuid"})
    assert "app_uuid" in exc.value.messages


def test_create_schema_blocked_reason_too_long_raises():
    schema = BlacklistCreateSchema()
    with pytest.raises(ValidationError) as exc:
        schema.load({
            "email": "user@example.com",
            "app_uuid": VALID_UUID,
            "blocked_reason": "x" * 256,
        })
    assert "blocked_reason" in exc.value.messages


def test_response_schema_dump():
    schema = BlacklistResponseSchema()
    result = schema.dump({
        "id": "abc-123",
        "email": "user@example.com",
        "app_uuid": VALID_UUID,
        "blocked_reason": "Spam",
        "ip_address": "127.0.0.1",
        "created_at": datetime(2026, 1, 1, 0, 0, 0),
    })
    assert result["email"] == "user@example.com"
    assert result["ip_address"] == "127.0.0.1"
    assert result["created_at"] == "2026-01-01T00:00:00"


def test_check_response_schema_dump():
    schema = BlacklistCheckResponseSchema()
    result = schema.dump({
        "is_blacklisted": True,
        "email": "user@example.com",
        "blocked_reason": "Spam",
    })
    assert result["is_blacklisted"] is True
    assert result["email"] == "user@example.com"