import pytest
from app.main import app
from flask.testing import FlaskClient
from typing import Generator
from unittest.mock import MagicMock
import pyodbc

@pytest.fixture(scope="session", autouse=True)
def configure_test_settings():
    """Configure settings for tests."""
    app.config["TESTING"] = True

@pytest.fixture
def client() -> Generator[FlaskClient, None, None]:
    """
    Creates a Flask test client.

    Yields:
        A Flask test client.
    """
    with app.test_client() as client:
        yield client

@pytest.fixture
def mock_db_connection(monkeypatch) -> None:
    """
    Mocks the database connection for testing.
    """
    conn: MagicMock = MagicMock(spec=pyodbc.Connection)
    cursor: MagicMock = MagicMock(spec=pyodbc.Cursor)
    conn.cursor.return_value = cursor
    cursor.execute.return_value = None
    cursor.fetchall.return_value = []
    cursor.description = []

    def mock_get_db_connection():
        return conn

    monkeypatch.setattr("app.database.get_db_connection", mock_get_db_connection)
