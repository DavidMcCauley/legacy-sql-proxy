# Legacy SQL Proxy Microservice

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code Style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

## Overview

This project implements a secure and efficient Python microservice designed to interact with a legacy Microsoft SQL Server 2005 database. The microservice acts as a proxy, providing a controlled and validated interface for executing SQL queries and retrieving table metadata. It is designed to be robust, maintainable, and production-ready, addressing the challenges of interacting with older database systems in a modern, secure way.

## Key Features

*   **Type Hinting:** Comprehensive type hints throughout the codebase for improved readability, maintainability, and early error detection.
*   **Pydantic Validation:** Uses Pydantic models to validate all incoming requests, ensuring data integrity and preventing invalid inputs from reaching the database.
*   **Database Connection Pooling:** Implements connection pooling using `dbutils` to efficiently manage database connections, reducing latency and improving performance.
*   **Metadata Caching:** Employs an LRU (Least Recently Used) cache to store table metadata, minimizing database calls and improving response times.
*   **Robust Error Handling:** Features custom exception classes and centralized error handling to gracefully manage errors, provide informative error messages, and log relevant information for debugging.
*   **Authentication:** Uses API key-based authentication to secure endpoints and prevent unauthorized access.
*   **SQL Injection Prevention:** Strictly uses parameterized queries and validates SQL syntax to mitigate SQL injection vulnerabilities.
*   **Logging:** Comprehensive logging with configurable levels, rotating file handler, and detailed log messages for monitoring and troubleshooting.
*   **Health Check Endpoint:** Includes a `/health` endpoint for monitoring the service's operational status.
*   **Production-Ready:** Designed for deployment with production-ready WSGI servers like Gunicorn and can be managed with process managers like systemd.
*   **Testing:**  Includes thorough unit tests with mocking to ensure code quality and reliability.
*   **Open Source (MIT License):**  Freely available to use, modify, and distribute.

## Table of Contents

*   [Overview](#overview)
*   [Key Features](#key-features)
*   [Table of Contents](#table-of-contents)
*   [Installation](#installation)
*   [Configuration](#configuration)
*   [Running the Application](#running-the-application)
    *   [Development](#development)
    *   [Production](#production)
*   [Testing](#testing)
*   [API Endpoints](#api-endpoints)
    *   [POST /query](#post-query)
    *   [GET /metadata/&lt;table&gt;](#get-metadatatable)
    *   [GET /health](#get-health)
*   [Security](#security)
*   [Error Handling and Logging](#error-handling-and-logging)
*   [Deployment](#deployment)
*   [Troubleshooting](#troubleshooting)
*   [Contributing](#contributing)
*   [License](#license)
*   [Future Improvements](#future-improvements)

## Installation

1. **Clone the repository:**

    ```bash
    git clone <your_repository_url>
    cd legacy-sql-proxy
    ```

2. **Create a virtual environment (recommended):**

    ```bash
    python3 -m venv .venv
    source .venv/bin/activate  # Linux/macOS
    .venv\Scripts\activate  # Windows
    ```

3. **Install dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

## Configuration

1. **Copy the example environment file:**

    ```bash
    cp .env.example .env
    ```

2. **Edit `.env` and set the following environment variables:**

    *   **`SQL_SERVER`:** The hostname or IP address of your SQL Server 2005 instance.
    *   **`SQL_DATABASE`:** The name of the database to connect to.
    *   **`SQL_USERNAME`:** The username for database authentication.
    *   **`SQL_PASSWORD`:** The password for database authentication.
    *   **`API_KEYS`:** A dictionary of API keys and their corresponding roles (currently only supporting a single role). **Important:** The value must be a valid Python dictionary after using `ast.literal_eval()`. Make sure that any single quotes used within the value are escaped if you are having problems.

        *   Example: `'{"your_api_key": "your_role"}'`

    *   **`LOG_LEVEL`:** The desired logging level (e.g., `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`).
    *   **`LOG_ROTATION_MAX_BYTES`:** The maximum size of each log file before rotation (default: 10MB).
    *   **`LOG_ROTATION_BACKUP_COUNT`:** The number of backup log files to keep.

**Security Note:**

*   **Never commit your `.env` file to version control.** It contains sensitive credentials.
*   For production environments, consider more secure ways to manage secrets (e.g., HashiCorp Vault, AWS Secrets Manager, or other platform-specific solutions).

## Running the Application

### Development

For development purposes, you can run the application directly using Flask's built-in development server:

```bash
flask --app app.main run --debug --host=0.0.0.0 --port=5000
```

*   **`--debug`:** Enables debug mode, which provides detailed error messages and automatically reloads the server when code changes. **Do not use this in production.**
*   **`--host=0.0.0.0`:** Makes the server accessible from other machines on your network.
*   **`--port=5000`:** Specifies the port to listen on (default is 5000).

### Production

For production deployments, use a production-ready WSGI server like Gunicorn:

```bash
gunicorn --workers 4 --bind 0.0.0.0:5000 app.main:app
```

*   **`--workers 4`:** Specifies the number of worker processes to use. Adjust this based on your server's resources.
*   **`--bind 0.0.0.0:5000`:** Specifies the address and port to bind to.

**Daemonization with systemd (Recommended for Production)**

To ensure the application runs as a background service and restarts automatically, you can use systemd (on Linux systems that support it):

1. **Create a systemd unit file:**

    Create a file named `legacy-sql-proxy.service` (or similar) in `/etc/systemd/system/`:

    ```ini
    [Unit]
    Description=Legacy SQL Proxy Microservice
    After=network.target

    [Service]
    User=your_user  # Replace with the user you want to run the service as (e.g., a dedicated service account)
    Group=your_group # Replace with the group (e.g., www-data, nobody)
    WorkingDirectory=/path/to/your/legacy-sql-proxy
    Environment="PATH=/path/to/your/legacy-sql-proxy/.venv/bin"
    ExecStart=/path/to/your/legacy-sql-proxy/.venv/bin/gunicorn --workers 4 --bind 0.0.0.0:5000 app.main:app

    [Install]
    WantedBy=multi-user.target
    ```

    *   **Replace placeholders:**
        *   `your_user` and `your_group` with the appropriate user and group.
        *   `/path/to/your/legacy-sql-proxy` with the actual path to your project directory.

2. **Reload systemd:**

    ```bash
    sudo systemctl daemon-reload
    ```

3. **Enable and start the service:**

    ```bash
    sudo systemctl enable legacy-sql-proxy.service
    sudo systemctl start legacy-sql-proxy.service
    ```

4. **Check service status:**

    ```bash
    sudo systemctl status legacy-sql-proxy.service
    ```

## Testing

1. **Install development dependencies:**

    ```bash
    pip install -r requirements-dev.txt
    ```

2. **Run tests with coverage:**

    ```bash
    pytest --cov=app --cov-report=term-missing tests/
    ```

    This will run all tests in the `tests/` directory and provide a coverage report showing which lines of code are not covered by tests.

## API Endpoints

The microservice exposes the following API endpoints:

### POST /query

Executes a SQL `SELECT` query against the configured database.

**Request:**

```json
{
    "sql": "SELECT * FROM your_table WHERE id = :id",
    "table": "your_table",
    "params": {"id": 1}
}
```

*   **`sql`:** The SQL `SELECT` query to execute. **Only `SELECT` queries are allowed.**
*   **`table`:** (Optional) The name of the table being queried. If provided, it is used to validate the parameters against the table's schema.
*   **`params`:** (Optional) A dictionary of parameters to be used in the query. Parameter names should be prefixed with a colon (`:`) in the SQL query string.

**Headers:**

*   **`X-API-Key`:** (Required) A valid API key for authentication.

**Response (200 OK):**

```json
[
    {"id": 1, "column1": "value1", "column2": "value2"},
    {"id": 2, "column1": "value3", "column2": "value4"}
]
```

**Error Responses:**

*   **400 Bad Request:**
    *   Invalid JSON payload.
    *   Validation errors in the `sql` or `params` fields (e.g., invalid SQL syntax, disallowed keywords, incorrect parameter types).
*   **401 Unauthorized:**
    *   Missing `X-API-Key` header.
    *   Invalid or unknown API key.
*   **500 Internal Server Error:**
    *   Database connection error.
    *   Error executing the query.
    *   Any other unexpected error.

### GET /metadata/&lt;table&gt;

Retrieves metadata for the specified table.

**Request:**

```
GET /metadata/your_table
```

*   **`table`:** The name of the table in the database.

**Headers:**

*   **`X-API-Key`:** (Required) A valid API key for authentication.

**Response (200 OK):**

```json
{
    "table_name": "your_table",
    "columns": [
        {"name": "id", "type": "int", "nullable": false},
        {"name": "column1", "type": "varchar", "nullable": true},
        {"name": "column2", "type": "datetime", "nullable": false}
    ]
}
```

**Error Responses:**

*   **401 Unauthorized:**
    *   Missing `X-API-Key` header.
    *   Invalid or unknown API key.
*   **404 Not Found:**
    *   The specified table does not exist.
*   **500 Internal Server Error:**
    *   Database connection error.
    *   Error retrieving metadata.
    *   Any other unexpected error.

### GET /health

Performs a health check on the application. This endpoint verifies that the application is running and can connect to the database.

**Request:**

```
GET /health
```

**Response (200 OK):**

```json
{"status": "OK"}
```

**Error Responses:**

*   **500 Internal Server Error:**
    *   The application is unhealthy (e.g., cannot connect to the database).

## Security

This microservice incorporates several security measures to protect the database and ensure secure operation:

*   **API Key Authentication:** All API requests require a valid API key to be passed in the `X-API-Key` header. This prevents unauthorized access to the endpoints.
*   **Parameterized Queries:** The application strictly uses parameterized queries when interacting with the database. This is the most effective way to prevent SQL injection vulnerabilities. Parameterized queries ensure that user-supplied data is treated as data, not as executable SQL code.
*   **Input Validation:**
    *   **SQL Query Validation:** The `sql` field in the `/query` endpoint is validated to ensure that:
        *   It starts with the `SELECT` keyword, enforcing that only read operations are allowed.
        *   It does not contain any disallowed keywords like `INSERT`, `UPDATE`, `DELETE`, `DROP`, `ALTER`, etc., preventing any data modification or database schema changes.
    *   **Parameter Validation:** If the `table` field is provided in the `/query` request, the `params` are validated against the actual table schema fetched from the database. This ensures that:
        *   The parameter names match the column names in the table.
        *   The parameter types are compatible with the corresponding column types.
*   **Principle of Least Privilege:** The database user configured in the `.env` file should be granted only the absolute minimum necessary permissions. In most cases, this will be `SELECT` access to specific tables. Avoid using database users with administrative privileges.
*   **Secrets Management:**
    *   Sensitive information like database credentials and API keys are stored in the `.env` file, which should **never** be committed to version control.
    *   **Recommendation for Production:** Use a dedicated secrets management solution like HashiCorp Vault, AWS Secrets Manager, Google Cloud Secret Manager, or Azure Key Vault to store and manage secrets more securely. These solutions provide encryption, access control, audit logging, and other security features.
*   **Role-Based Access Control (RBAC) Placeholder:** The `auth.py` file includes a placeholder for implementing role-based access control. In the future, you can extend this to assign different roles to API keys (e.g., `admin`, `read-only`) and restrict access to specific endpoints or operations based on these roles.

## Error Handling and Logging

*   **Custom Exceptions:** The application defines custom exception classes to represent different types of errors:
    *   **`DatabaseError`:**  Base class for any database-related errors.
    *   **`QueryExecutionError`:** Raised when there is an error executing a SQL query (e.g., syntax error, invalid parameter).
    *   **`TableNotFoundError`:**  Raised when a specified table is not found in the database.
    *   **`APIError`:** Base class for API-related errors (e.g., validation errors).
    *   **`InvalidRequestError`:** Raised when the request data is invalid (e.g., missing fields, incorrect types).
    *   **`AuthException`:** Raised when there is an authentication or authorization failure (e.g., missing or invalid API key).
*   **Centralized Error Handling:** The `main.py` file uses Flask's `@app.errorhandler` decorator to set up centralized error handlers for each custom exception type. These handlers perform the following:
    *   Log the error using the application's logger, including relevant details like the error message, client IP, API key (if available), SQL query, and parameters.
    *   Return a consistent JSON error response to the client with an appropriate HTTP status code (e.g., 400 for validation errors, 401 for authentication errors, 404 for table not found, 500 for server errors).
*   **Logging:**
    *   **Configuration:**
        *   The logging level (e.g., `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`) is configured in the `.env` file.
        *   The application uses a `RotatingFileHandler` to manage log file size. The `LOG_ROTATION_MAX_BYTES` and `LOG_ROTATION_BACKUP_COUNT` settings in `.env` control the maximum log file size and the number of backup files to keep.
    *   **Content:** Log messages include:
        *   **Timestamp:** When the event occurred.
        *   **Log Level:** The severity of the event (e.g., `INFO`, `ERROR`).
        *   **Logger Name:** The name of the logger that generated the message (usually the module name).
        *   **Message:** A description of the event, including relevant details.
        *   **Context:** For errors, the log message often includes additional context, such as the client's IP address, the API key used (if available), the SQL query, and any parameters passed.

**Example Log Messages:**

```
2023-10-27 10:30:00,000 [INFO] app.main: Query received from 127.0.0.1 - SQL: SELECT * FROM..., Params: {'id': 1}
2023-10-27 10:30:00,500 [ERROR] app.main: Database error: Error executing query: ...
2023-10-27 10:35:00,000 [WARNING] app.main: Invalid request: ...
2023-10-27 10:40:00,000 [ERROR] app.main: Authentication error: Unauthorized
```

## Deployment

**Deployment to a production environment typically involves the following steps:**

1. **Choose a Server:** Select a server or cloud instance to host your application (e.g., AWS EC2, Google Cloud Compute Engine, Azure Virtual Machines, or a physical server).

2. **Install Prerequisites:** On your server, ensure that the necessary prerequisites are installed:
    *   Python 3 (preferably the same version you used for development)
    *   pip
    *   systemd (if you're using systemd for process management)
    *   A reverse proxy server (e.g., Nginx, Apache) - strongly recommended

3. **Transfer Project Files:** Transfer your project files to the server using a method like `scp`, `rsync`, or Git.

4. **Set Up Virtual Environment:** Create and activate a virtual environment on the server:

    ```bash
    python3 -m venv .venv
    source .venv/bin/activate # Or equivalent for your OS
    ```

5. **Install Dependencies:** Install the project's dependencies into the virtual environment:

    ```bash
    pip install -r requirements.txt
    ```

6. **Configure Environment Variables:**
    *   Create a `.env` file on the server and set the environment variables as described in the [Configuration](#configuration) section.
    *   **Important:** For production, use a secure method to manage your secrets (e.g., a dedicated secrets management tool).

7. **Configure Gunicorn:** If you haven't already, create a Gunicorn configuration file (e.g., `gunicorn_config.py`) or specify the Gunicorn options directly in your systemd unit file (see step 8).

8. **Configure systemd (Recommended):**
    *   Create a systemd unit file (e.g., `/etc/systemd/system/legacy-sql-proxy.service`) as described in the [Production](#production) section under "Daemonization with systemd."
    *   Reload systemd: `sudo systemctl daemon-reload`
    *   Enable the service: `sudo systemctl enable legacy-sql-proxy.service`
    *   Start the service: `sudo systemctl start legacy-sql-proxy.service`

9. **Configure Reverse Proxy (Strongly Recommended):**
    *   Install and configure a reverse proxy server like Nginx or Apache.
    *   **Example Nginx Configuration:**

        ```nginx
        server {
            listen 80;
            server_name your_domain.com; # Or your server's IP address

            location / {
                proxy_pass http://127.0.0.1:5000; # Assuming Gunicorn is running on port 5000
                proxy_set_header Host $host;
                proxy_set_header X-Real-IP $remote_addr;
                proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
                proxy_set_header X-Forwarded-Proto $scheme;
            }
        }
        ```

    *   **SSL/TLS:** If you have a domain name, configure your reverse proxy to use SSL/TLS (HTTPS) to encrypt traffic. You can obtain free SSL certificates from Let's Encrypt.

10. **Test the Deployment:** Access your application through the reverse proxy (e.g., `http://your_domain.com` or `http://your_server_ip`) to ensure everything is working correctly.

## Troubleshooting

*   **Database Connection Errors:**
    *   **Check `.env`:** Double-check that `SQL_SERVER`, `SQL_DATABASE`, `SQL_USERNAME`, and `SQL_PASSWORD` are correct in your `.env` file.
    *   **Network Connectivity:** Ensure that your server can reach the SQL Server instance over the network. You might need to check firewall rules or network configuration.
    *   **SQL Server Configuration:** Verify that your SQL Server instance is configured to allow remote connections and that the specified user has the necessary permissions.
    *   **Logs:** Examine the application logs (`app.log`) for detailed error messages.

*   **Authentication Errors (401 Unauthorized):**
    *   **`X-API-Key` Header:** Make sure you are sending the `X-API-Key` header with a valid API key in all your requests.
    *   **`.env` API\_KEYS:** Verify that the `API_KEYS` setting in your `.env` file is a valid Python dictionary string and that the API key you are using is correctly defined.
    *   **Logs:** Look for authentication-related error messages in the application logs.

*   **Query Execution Errors (500 Internal Server Error):**
    *   **SQL Syntax:** Carefully review your SQL query for any syntax errors or invalid keywords.
    *   **Parameter Mismatch:** If you are using parameters, ensure that the parameter names in your query match the keys in the `params` dictionary and that the parameter types are compatible with the corresponding column types.
    *   **Database Permissions:** Verify that the database user has the necessary permissions to execute `SELECT` queries on the specified table.
    *   **Logs:** Examine the application logs for detailed error messages, including the SQL query that was executed and any error messages returned by the database.

*   **Metadata Errors (404 Not Found or 500 Internal Server Error):**
    *   **Table Name:** Double-check that you are using the correct table name in the URL (e.g., `/metadata/your_table`).
    *   **Database Connection:** Ensure that the application can successfully connect to the database.
    *   **Logs:** Look for error messages related to metadata retrieval in the application logs.

*   **General Application Errors:**
    *   **Logs:** The application logs are your primary source of information for debugging. Look for error messages, warnings, or any unusual activity.
    *   **systemd:** If you are using systemd, use `sudo systemctl status legacy-sql-proxy.service` to check the service status and `sudo journalctl -u legacy-sql-proxy.service` to view the systemd logs for the service.
    *   **Gunicorn Logs:** If you are using Gunicorn, check the Gunicorn error logs (if configured) for any issues related to the WSGI server.

## Contributing

Contributions to this project are welcome! If you find a bug, have a suggestion for improvement, or want to add a new feature, please follow these steps:

1. Fork the repository on GitHub.
2. Create a new branch for your changes: `git checkout -b your-feature-branch`
3. Make your changes, following the project's coding style and conventions.
4. Write tests to cover your changes.
5. Commit your changes with clear and descriptive commit messages.
6. Push your branch to your forked repository: `git push origin your-feature-branch`
7. Open a pull request on the main repository, explaining your changes and why they are valuable.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
