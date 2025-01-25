from functools import wraps
from flask import request, jsonify, Response
from .config import settings
from .exceptions import AuthException
from typing import Callable

def require_api_key(view_func: Callable) -> Callable:
    @wraps(view_func)
    def decorated_function(*args, **kwargs) -> Response:
        api_key: Optional[str] = request.headers.get('X-API-Key')
        if not api_key or api_key not in settings.api_keys:
            raise AuthException('Unauthorized', status_code=401)
        return view_func(*args, **kwargs)

    return decorated_function
