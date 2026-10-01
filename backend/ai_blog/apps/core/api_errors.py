"""
Shared helpers for building consistent API error responses.

Centralizes the ServiceError-or-fallback pattern that several views repeated
inline, and keeps internal exception detail out of client responses (logged
instead, surfaced only under DEBUG).
"""
import logging

from django.conf import settings
from rest_framework import status
from rest_framework.response import Response

logger = logging.getLogger('ai_blog.core.api_errors')


def error_response(code: str, message: str, http_status: int, exc: Exception = None):
    """
    Build a consistent error body. Internal exception text is logged rather than
    returned, so stack/driver details do not leak to API clients in production.
    """
    if exc is not None:
        logger.exception('%s: %s', code, exc)
        if settings.DEBUG:
            message = f'{message} ({exc})'
    return Response(
        {'error': {'code': code, 'message': message, 'details': {}}},
        status=http_status,
    )


def service_error_response(exc: Exception, code: str, message: str, http_status: int):
    """
    Convert an exception raised by the service layer into a Response.

    A ServiceError (anything exposing ``to_dict()``) is a client-facing 400 with
    its own structured body. Anything else is unexpected: it is logged and
    returned under ``code``/``http_status`` with a non-leaking message.
    """
    if hasattr(exc, 'to_dict'):
        return Response(exc.to_dict(), status=status.HTTP_400_BAD_REQUEST)
    return error_response(code, message, http_status, exc=exc)
