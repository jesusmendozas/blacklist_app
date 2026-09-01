"""Pruebas unitarias de auth_middleware.

Autores: Jesús Mendoza, Rafael Beleño, Juan Díaz, Yeison Arrieta.
"""
import json
import os
from flask import Flask, jsonify
from src.middleware.auth_middleware import require_bearer_token


def make_test_app():
    """A minimal Flask app to exercise the decorator in isolation."""
    test_app = Flask(__name__)

    @test_app.route("/protected")
    @require_bearer_token
    def protected():
        return jsonify({"message": "ok"}), 200

    return test_app


def test_missing_authorization_header():
    app = make_test_app()
    client = app.test_client()
    resp = client.get("/protected")
    assert resp.status_code == 401
    assert resp.get_json()["message"] == "Authorization header is missing"


def test_malformed_authorization_header_no_bearer_prefix():
    app = make_test_app()
    client = app.test_client()
    resp = client.get("/protected", headers={"Authorization": "sometoken"})
    assert resp.status_code == 401


def test_malformed_authorization_header_wrong_scheme():
    app = make_test_app()
    client = app.test_client()
    resp = client.get("/protected", headers={"Authorization": "Basic sometoken"})
    assert resp.status_code == 401


def test_missing_bearer_token_env_var(monkeypatch):
    monkeypatch.delenv("BEARER_TOKEN", raising=False)
    app = make_test_app()
    client = app.test_client()
    resp = client.get("/protected", headers={"Authorization": "Bearer anytoken"})
    assert resp.status_code == 500


def test_invalid_bearer_token(monkeypatch):
    monkeypatch.setenv("BEARER_TOKEN", "correct-token")
    app = make_test_app()
    client = app.test_client()
    resp = client.get("/protected", headers={"Authorization": "Bearer wrong-token"})
    assert resp.status_code == 401
    assert resp.get_json()["message"] == "Invalid bearer token"


def test_valid_bearer_token(monkeypatch):
    monkeypatch.setenv("BEARER_TOKEN", "correct-token")
    app = make_test_app()
    client = app.test_client()
    resp = client.get("/protected", headers={"Authorization": "Bearer correct-token"})
    assert resp.status_code == 200
    assert resp.get_json()["message"] == "ok"