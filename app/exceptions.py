from werkzeug.exceptions import HTTPException

class DatabaseError(Exception):
    """Base database error"""
    pass

class QueryExecutionError(DatabaseError):
    """Invalid query parameters"""
    pass

class TableNotFoundError(DatabaseError):
    """Table not found"""
    pass

class APIError(Exception):
    """Base API error"""
    pass

class InvalidRequestError(APIError):
    """Invalid request data"""
    pass

class AuthException(HTTPException):
    """Authentication or authorization failure"""
    def __init__(self, message: str, status_code: int = 401):
        super().__init__(description=message)
        self.code = status_code
