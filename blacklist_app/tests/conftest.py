import os
import tempfile

import pytest

# Use a temporary file-based SQLite database for tests, configured
# BEFORE importing the app so init_db() picks it up.
_db_fd, _db_path = tempfile.mkstemp(suffix=".db")
os.environ["DATABASE_URL"] = f"sqlite:///{_db_path}"
os.environ["BEARER_TOKEN"] = "test-bearer-token"

from src.main import app as flask_app  # noqa: E402
from src.db.database import db as _db  # noqa: E402


@pytest.fixture(scope="session")
def app():
    flask_app.config.update({"TESTING": True})
    yield flask_app
    with flask_app.app_context():
        _db.session.remove()
        _db.engine.dispose()
    os.close(_db_fd)
    try:
        os.remove(_db_path)
    except PermissionError:
        pass


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture(autouse=True)
def clean_db(app):
    """Ensure a clean database before/after every test for isolation."""
    with app.app_context():
        yield
        for table in reversed(_db.metadata.sorted_tables):
            _db.session.execute(table.delete())
        _db.session.commit()


@pytest.fixture
def auth_headers():
    return {"Authorization": f"Bearer {os.environ['BEARER_TOKEN']}"}