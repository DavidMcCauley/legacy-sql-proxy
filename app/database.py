import pyodbc
from dbutils.pooled_db import PooledDB
from .config import settings
from .models import TableMetadata, ColumnSchema
from functools import lru_cache
from typing import Optional, List, Dict, Any, Union, Tuple
from .exceptions import DatabaseError, QueryExecutionError, TableNotFoundError

connection_string: str = (
    f'DRIVER={{jTDS}};'
    f'SERVER={settings.sql_server};'
    f'DATABASE={settings.sql_database};'
    f'UID={settings.sql_username};'
    f'PWD={settings.sql_password};'
    f'TDS_Version=8.0;'
)

db_pool: PooledDB = PooledDB(
    creator=pyodbc,
    mincached=2,
    maxcached=5,
    maxconnections=10,
    blocking=True,
    connection_string=connection_string
)

def get_db_connection() -> Optional[pyodbc.Connection]:
    """Gets a connection from the pool."""
    try:
        conn: pyodbc.Connection = db_pool.connection()
        return conn
    except Exception as ex:
        raise DatabaseError(f"Failed to get a database connection: {ex}")

@lru_cache(maxsize=32)
def get_table_metadata(table_name: str) -> Optional[TableMetadata]:
    """Fetches and caches table metadata."""
    conn: Optional[pyodbc.Connection] = get_db_connection()
    if conn is None:
        raise DatabaseError("Failed to get a database connection")

    try:
        cursor: pyodbc.Cursor = conn.cursor()
        cursor.columns(table=table_name)

        columns: List[ColumnSchema] = []
        for row in cursor.fetchall():
            columns.append(
                ColumnSchema(
                    name=row.column_name, type=row.type_name, nullable=row.nullable == 1
                )
            )
        return TableMetadata(table_name=table_name, columns=columns)
    except pyodbc.Error as ex:
        raise DatabaseError(f"Error fetching table metadata: {ex}")
    finally:
        cursor.close()
        conn.close()

def execute_query(
    sql: str, params: Optional[Tuple[Any, ...]] = None
) -> Union[List[Dict[str, Any]], Dict[str, str]]:
    """
    Executes a SQL query.

    Args:
        sql: The SQL query to execute.
        params: Optional parameters for the query.

    Returns:
        A list of dictionaries for SELECT queries, or a dictionary indicating success for other queries.

    Raises:
        QueryExecutionError: If the query fails to execute.
    """
    conn: Optional[pyodbc.Connection] = get_db_connection()
    if conn is None:
        raise DatabaseError("Failed to get a database connection")

    try:
        cursor: pyodbc.Cursor = conn.cursor()
        if params:
            cursor.execute(sql, params)
        else:
            cursor.execute(sql)

        if sql.strip().upper().startswith("SELECT"):
            columns: List[str] = [col[0] for col in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]

        conn.commit()
        return {"message": "Query executed successfully"}
    except pyodbc.Error as ex:
        raise QueryExecutionError(f"Error executing query: {ex}")
    finally:
        cursor.close()
        conn.close()
