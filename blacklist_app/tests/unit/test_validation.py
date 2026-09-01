"""Pruebas unitarias de validation.

Autores: Jesús Mendoza, Rafael Beleño, Juan Díaz, Yeison Arrieta.
"""
import pytest
from src.models.errors import BadRequestError
from src.utils.validation import validate_uuid, get_client_ip


def test_validate_uuid_valid():
    assert validate_uuid("123e4567-e89b-12d3-a456-426614174000") is True


def test_validate_uuid_invalid_raises():
    with pytest.raises(BadRequestError):
        validate_uuid("not-a-uuid")


class FakeRequest:
    def __init__(self, headers=None, remote_addr=None):
        self.headers = headers or {}
        self.remote_addr = remote_addr


def test_get_client_ip_with_forwarded_for_single():
    req = FakeRequest(headers={"X-Forwarded-For": "1.2.3.4"})
    assert get_client_ip(req) == "1.2.3.4"


def test_get_client_ip_with_forwarded_for_multiple():
    req = FakeRequest(headers={"X-Forwarded-For": "1.2.3.4, 5.6.7.8"})
    assert get_client_ip(req) == "1.2.3.4"


def test_get_client_ip_without_forwarded_for_uses_remote_addr():
    req = FakeRequest(headers={}, remote_addr="9.9.9.9")
    assert get_client_ip(req) == "9.9.9.9"


def test_get_client_ip_without_anything_returns_unknown():
    req = FakeRequest(headers={}, remote_addr=None)
    assert get_client_ip(req) == "unknown"