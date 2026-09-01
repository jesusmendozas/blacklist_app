"""Pruebas unitarias de database.

Autores: Jesús Mendoza, Rafael Beleño, Juan Díaz, Yeison Arrieta.
"""
import pytest
from flask import Flask
from src.db.database import init_db, create_tables


def test_init_db_without_url_raises(monkeypatch):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    app = Flask(__name__)
    with pytest.raises(ValueError):
        init_db(app)


def test_init_db_with_url_sets_config(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "sqlite:///:memory:")
    app = Flask(__name__)
    init_db(app)
    assert app.config["SQLALCHEMY_DATABASE_URI"] == "sqlite:///:memory:"
    assert app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] is False


def test_create_tables_runs_without_error(app):
    # Uses the real test app/db from conftest — just confirms it runs cleanly.
    create_tables(app)