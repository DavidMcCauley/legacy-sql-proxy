import ast
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Dict, Any

class Settings(BaseSettings):
    sql_server: str
    sql_database: str
    sql_username: str
    sql_password: str
    api_keys: Dict[str, str] = {"default_key": "read-only"}
    log_level: str = "INFO"
    log_rotation_max_bytes: int = 10485760  # 10 MB
    log_rotation_backup_count: int = 5

    @field_validator('api_keys', mode='before')
    def parse_api_keys(cls, v: str) -> Dict[str, Any]:
        if isinstance(v, str):
            try:
                return ast.literal_eval(v)
            except (ValueError, SyntaxError):
                raise ValueError("Invalid format for API_KEYS. Must be a valid dictionary.")
        return v

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="SQL_",
        frozen=True,
        extra="ignore"
    )

settings = Settings()
