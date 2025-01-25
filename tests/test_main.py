from app.main import app
from app.config import settings
import json
from typing import Dict, Any
from unittest.mock import MagicMock
import pytest

def test_health_check(client):
    """Test the health check endpoint."""
    response = client.get('/health')
    assert response.status_code == 200
    assert b"OK" in response.data

def test_unauthorized_access(client):
    """Test that unauthorized access is denied."""
    response = client.post('/query', json={"sql": "SELECT 1"})
    assert response.status_code == 401

def test_valid_query(client, mock_db_connection, monkeypatch):
    """Test a valid query."""
    # Mock the execute_query function to return a specific result
    def mock_execute_query(*args, **kwargs):
        return [{"result": 1}]

    monkeypatch.setattr("app.database.execute_query", mock_execute_query)

    response = client.post(
        '/query',
        json={"sql": "SELECT 1", "params": {}},
        headers={"X-API-Key": list(settings.api_keys.keys())[0]}
    )
    assert response.status_code == 200
    assert b"result" in response.data

def test_invalid_query(client, mock_db_connection, monkeypatch):
    """Test an invalid query."""
    # Mock the execute_query function to raise an exception
    def mock_execute_query(*args, **kwargs):
        raise Exception("Invalid query")

    monkeypatch.setattr("app.database.execute_query", mock_execute_query)

    response = client.post(
        '/query',
        json={"sql": "INVALID QUERY", "params": {}},
        headers={"X-API-Key": list(settings.api_keys.keys())[0]}
    )
    assert response.status_code == 500  # Assuming your error handler returns 500 for exceptions

def test_get_metadata_success(client, mock_db_connection, monkeypatch):
    """Test successful retrieval of metadata."""
    # Mock the get_table_metadata function to return a specific result
    def mock_get_table_metadata(*args, **kwargs):
        return {"table_name": "test_table", "columns": []}

    monkeypatch.setattr("app.database.get_table_metadata", mock_get_table_metadata)

    response = client.get(
        '/metadata/test_table',
        headers={"X-API-Key": list(settings.api_keys.keys())[0]}
    )
    assert response.status_code == 200
    assert b"test_table" in response.data

def test_get_metadata_not_found(client, mock_db_connection, monkeypatch):
    """Test retrieval of metadata for a non-existent table."""
    # Mock the get_table_metadata function to return None
    def mock_get_table_metadata(*args, **kwargs):
        return None

    monkeypatch.setattr("app.database.get_table_metadata", mock_get_table_metadata)

    response = client.get(
        '/metadata/nonexistent_table',
        headers={"X-API-Key": list(settings.api_keys.keys())[0]}
    )
    assert response.status_code == 404
