"""Pruebas unitarias de errors.

Autores: Jesús Mendoza, Rafael Beleño, Juan Díaz, Yeison Arrieta.
"""
from src.models.errors import (
    BadRequestError,
    NotFoundError,
    UnauthorizedError,
    ConflictError,
)


def test_bad_request_error_default_message():
    err = BadRequestError()
    assert err.message == "Bad request"
    assert err.errors is None
    assert str(err) == "Bad request"


def test_bad_request_error_custom_message_and_errors():
    err = BadRequestError("Custom message", errors={"field": "bad"})
    assert err.message == "Custom message"
    assert err.errors == {"field": "bad"}


def test_not_found_error_default_message():
    err = NotFoundError()
    assert err.message == "Resource not found"


def test_not_found_error_custom_message():
    err = NotFoundError("Email not found")
    assert err.message == "Email not found"


def test_unauthorized_error_default_message():
    err = UnauthorizedError()
    assert err.message == "Unauthorized"


def test_unauthorized_error_custom_message():
    err = UnauthorizedError("Invalid token")
    assert err.message == "Invalid token"


def test_conflict_error_default_message():
    err = ConflictError()
    assert err.message == "Resource already exists"


def test_conflict_error_custom_message():
    err = ConflictError("Email already blacklisted")
    assert err.message == "Email already blacklisted"