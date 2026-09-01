"""Pruebas unitarias de blacklist_repository.

Autores: Jesús Mendoza, Rafael Beleño, Juan Díaz, Yeison Arrieta.
"""
from unittest.mock import MagicMock
import pytest
from sqlalchemy.exc import IntegrityError
from src.repositories.blacklist_repository import BlacklistRepository
from src.models.errors import ConflictError


def test_create_success(mocker):
    repo = BlacklistRepository()
    mock_session = mocker.patch("src.repositories.blacklist_repository.db.session")

    result = repo.create({
        "id": "abc",
        "email": "user@example.com",
        "app_uuid": "123e4567-e89b-12d3-a456-426614174000",
        "blocked_reason": None,
        "ip_address": "127.0.0.1",
    })

    mock_session.add.assert_called_once()
    mock_session.commit.assert_called_once()
    assert result.email == "user@example.com"


def test_create_duplicate_email_raises_conflict(mocker):
    repo = BlacklistRepository()
    mock_session = mocker.patch("src.repositories.blacklist_repository.db.session")
    mock_session.commit.side_effect = IntegrityError(
        "statement", "params", Exception("duplicate key value violates unique constraint")
    )

    with pytest.raises(ConflictError):
        repo.create({
            "id": "abc",
            "email": "user@example.com",
            "app_uuid": "123e4567-e89b-12d3-a456-426614174000",
            "blocked_reason": None,
            "ip_address": "127.0.0.1",
        })

    mock_session.rollback.assert_called_once()


def test_create_other_integrity_error_reraised(mocker):
    repo = BlacklistRepository()
    mock_session = mocker.patch("src.repositories.blacklist_repository.db.session")
    mock_session.commit.side_effect = IntegrityError(
        "statement", "params", Exception("some other db error")
    )

    with pytest.raises(IntegrityError):
        repo.create({
            "id": "abc",
            "email": "user@example.com",
            "app_uuid": "123e4567-e89b-12d3-a456-426614174000",
            "blocked_reason": None,
            "ip_address": "127.0.0.1",
        })


def test_get_by_email_found(mocker):
    repo = BlacklistRepository()
    fake_result = MagicMock()
    mock_query = mocker.patch("src.repositories.blacklist_repository.db.session.query")
    mock_query.return_value.filter.return_value.first.return_value = fake_result

    result = repo.get_by_email("user@example.com")
    assert result is fake_result


def test_exists_by_email_true(mocker):
    repo = BlacklistRepository()
    mock_query = mocker.patch("src.repositories.blacklist_repository.db.session.query")
    mock_query.return_value.filter.return_value.first.return_value = MagicMock()

    assert repo.exists_by_email("user@example.com") is True


def test_exists_by_email_false(mocker):
    repo = BlacklistRepository()
    mock_query = mocker.patch("src.repositories.blacklist_repository.db.session.query")
    mock_query.return_value.filter.return_value.first.return_value = None

    assert repo.exists_by_email("user@example.com") is False