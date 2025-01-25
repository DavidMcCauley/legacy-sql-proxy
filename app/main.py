import logging
from logging.handlers import RotatingFileHandler
from flask import Flask, request, jsonify, Response
import json
from .database import execute_query, get_table_metadata
from .models import QueryRequest, TableMetadata
from .auth import require_api_key
from .config import settings
from .exceptions import (
    DatabaseError,
    QueryExecutionError,
    TableNotFoundError,
    InvalidRequestError,
    AuthException,
)
from pydantic import ValidationError
from typing import Any, Tuple

app: Flask = Flask(__name__)
app.config["ERROR_INCLUDE_MESSAGE"] = False

# Configure logging
handler: RotatingFileHandler = RotatingFileHandler(
    "app.log",
    maxBytes=settings.log_rotation_max_bytes,
    backupCount=settings.log_rotation_backup_count,
)
formatter: logging.Formatter = logging.Formatter(
    "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
handler.setFormatter(formatter)
app.logger.addHandler(handler)
app.logger.setLevel(settings.log_level)

# Centralized error handling
@app.errorhandler(AuthException)
def handle_auth_error(e: AuthException) -> Tuple[Response, int]:
    app.logger.error(f"Authentication error: {e}")
    return jsonify({"error": e.description}), e.code

@app.errorhandler(InvalidRequestError)
def handle_invalid_request_error(e: InvalidRequestError) -> Tuple[Response, int]:
    app.logger.error(f"Invalid request error: {e}")
    return jsonify({"error": str(e)}), 400

@app.errorhandler(DatabaseError)
def handle_database_error(e: DatabaseError) -> Tuple[Response, int]:
    app.logger.error(f"Database error: {e}")
    return jsonify({"error": str(e)}), 500

@app.errorhandler(TableNotFoundError)
def handle_table_not_found_error(e: TableNotFoundError) -> Tuple[Response, int]:
    app.logger.error(f"Table not found error: {e}")
    return jsonify({"error": str(e)}), 404

@app.errorhandler(QueryExecutionError)
def handle_query_execution_error(e: QueryExecutionError) -> Tuple[Response, int]:
    app.logger.error(f"Query execution error: {e}")
    return jsonify({"error": str(e)}), 500

@app.errorhandler(Exception)
def handle_unexpected_error(e: Exception) -> Tuple[Response, int]:
    app.logger.error(f"Unexpected error: {e}", exc_info=True)
    return jsonify({"error": "An unexpected error occurred"}), 500

# Routes
@app.route("/health")
def health_check() -> Tuple[Response, int]:
    """
    Checks the health of the application.

    Returns:
        A tuple containing the response and the status code.
    """
    app.logger.info("Health check successful")
    return jsonify({"status": "OK"}), 200

@app.route("/query", methods=["POST"])
@require_api_key
def handle_query() -> Tuple[Response, int]:
    """
    Handles incoming SQL query requests.

    Returns:
        A tuple containing the response and the status code.
    """
    try:
        query: QueryRequest = QueryRequest(**request.get_json())

        app.logger.info(
            f"Query received from {request.remote_addr} - SQL: {query.sql[:50]}..., Params: {query.params}"
        )

        result: Union[List[Dict[str, Any]], Dict[str, str]] = execute_query(
            query.sql, tuple(query.params.values()) if query.params else None
        )

        app.logger.info("Query executed successfully")
        return jsonify(result), 200

    except ValidationError as e:
        raise InvalidRequestError(str(e))

@app.route("/metadata/<table>", methods=["GET"])
@require_api_key
def get_metadata(table: str) -> Tuple[Response, int]:
    """
    Retrieves metadata for a given table.

    Args:
        table: The name of the table.

    Returns:
        A tuple containing the response and the status code.
    """
    try:
        metadata: Optional[TableMetadata] = get_table_metadata(table)
        if not metadata:
            raise TableNotFoundError(f"Metadata for table '{table}' not found")

        app.logger.info(f"Metadata retrieved for table: {table}")
        return jsonify(metadata.model_dump()), 200

    except DatabaseError as e:
        raise DatabaseError(f"Error retrieving metadata: {e}")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
