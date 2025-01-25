from pydantic import BaseModel, field_validator, ValidationInfo
from typing import List, Dict, Optional, Any, Type
import re
from .database import get_table_metadata

class ColumnSchema(BaseModel):
    name: str
    type: str
    nullable: bool

class TableMetadata(BaseModel):
    table_name: str
    columns: List[ColumnSchema]

class QueryRequest(BaseModel):
    sql: str
    table: Optional[str] = None
    params: Optional[Dict[str, Any]] = None

    @field_validator('sql')
    @classmethod
    def validate_sql(cls, v: str) -> str:
        cleaned: str = re.sub(r'\s+', ' ', v).upper().strip()

        if not cleaned.startswith("SELECT"):
            raise ValueError("Only SELECT queries allowed")

        forbidden: set[str] = {"INSERT", "UPDATE", "DELETE", "DROP", "ALTER"}
        if any(cmd in cleaned for cmd in forbidden):
            raise ValueError("Modification commands prohibited")

        return v

    @field_validator('params')
    @classmethod
    def validate_params(cls, v: Optional[Dict[str, Any]], info: ValidationInfo) -> Optional[Dict[str, Any]]:
        if not v or not info.data.get('table'):
            return v

        table_name: Optional[str] = info.data.get('table')
        metadata: Optional[TableMetadata] = get_table_metadata(table_name)
        if not metadata:
            raise ValueError("Table metadata not found")

        for param, value in v.items():
            col: Optional[ColumnSchema] = next((c for c in metadata.columns if c.name == param), None)
            if not col:
                raise ValueError(f"Invalid parameter: {param}")

            expected_type: Type = sql_type_to_python_type(col.type)
            if not isinstance(value, expected_type):
                raise ValueError(f"{param} must be {expected_type.__name__}")

        return v

def sql_type_to_python_type(sql_type: str) -> Type:
    """
    Maps SQL Server data types to Python types.

    Args:
        sql_type: The SQL Server data type.

    Returns:
        The corresponding Python type.
    """
    type_mapping: Dict[str, Type] = {
        "int": int,
        "smallint": int,
        "tinyint": int,
        "bigint": int,
        "varchar": str,
        "nvarchar": str,
        "char": str,
        "nchar": str,
        "text": str,
        "ntext": str,
        "date": str,
        "datetime": str,
        "smalldatetime": str,
        "datetime2": str,
        "time": str,
        "float": float,
        "real": float,
        "decimal": float,
        "numeric": float,
        "money": float,
        "smallmoney": float,
        "bit": bool,
        "binary": bytes,
        "varbinary": bytes,
        "image": bytes,
    }

    for key, value in type_mapping.items():
        if key in sql_type.lower():
            return value

    return Any  # Default fallback for unknown types
