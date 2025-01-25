import pytest
from app.database import get_db_connection, get_table_metadata, execute_query
from app.exceptions import DatabaseError, QueryExecutionError, TableNotFoundError
from unittest.mock import MagicMock
from typing import Dict, Any

def test_get_db_connection_success(monkeypatch):
    """Test successful database connection."""
    mock_conn = MagicMock()
    monkeypatch.setattr("app.database.db_pool.connection", lambda: mock_conn)

    conn = get_db_connection()
    assert conn is not None

def test_get_db_connection_failure(monkeypatch):
    """Test database connection failure."""
    def mock_connection():
        raise Exception("Connection failed")

    monkeypatch.setattr("app.database.db_pool.connection", mock_connection)

    with pytest.raises(DatabaseError):
        get_db_connection()

def test_get_table_metadata_success(monkeypatch):
    """Test successful retrieval of table metadata."""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor

    # Mock the result of cursor.fetchall()
    mock_row = MagicMock()
    mock_row.column_name = "test_column"
    mock_row.type_name = "varchar"
    mock_row.nullable = 0
    mock_cursor.fetchall.return_value = [mock_row]

    monkeypatch.setattr("app.database.get_db_connection", lambda: mock_conn)

    metadata = get_table_metadata("test_table")
    assert metadata is not None
    assert metadata.table_name == "test_table"
    assert len(metadata.columns) == 1
    assert metadata.columns[0].name == "test_column"
    assert metadata.columns[0].type == "varchar"
    assert metadata.columns[0].nullable is False

def test_get_table_metadata_not_found(monkeypatch):
    """Test retrieval of metadata for a non-existent table."""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.fetchall.return_value = []  # Empty result indicates table not found

    monkeypatch.setattr("app.database.get_db_connection", lambda: mock_conn)

    with pytest.raises(DatabaseError):
        get_table_metadata("nonexistent_table")

def test_execute_query_success(monkeypatch):
    """Test successful query execution."""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.description = [("result",)]
    mock_cursor.fetchall.return_value = [("test_result",)]

    monkeypatch.setattr("app.database.get_db_connection", lambda: mock_conn)

    result = execute_query("SELECT 1")
    assert result is not None
    assert len(result) == 1
    assert result[0]["result"] == "test_result"

def test_execute_query_failure(monkeypatch):
    """Test query execution failure."""
    def mock_execute(*args, **kwargs):
        raise pyodbc.Error("Query failed")

    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.execute.side_effect = mock_execute

    monkeypatch.setattr("app.database.get_db_connection", lambda: mock_conn)

    with pytest.raises(QueryExecutionError):
        execute_query("INVALID QUERY")
