"""
Custom exception handler for DRF.
Converts service errors to consistent API responses.
"""
import logging
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
from django.http import Http404
from django.core.exceptions import PermissionDenied

logger = logging.getLogger('ai_blog')


def custom_exception_handler(exc, context):
    """
    Custom exception handler that converts ServiceErrors
    and other exceptions into consistent API responses.
    """
    # Call REST framework's default exception handler first
    response = exception_handler(exc, context)

    if response is not None:
        # Standard DRF exception
        return response

    # Handle ServiceError
    if hasattr(exc, 'to_dict'):
        return Response(exc.to_dict(), status=status.HTTP_400_BAD_REQUEST)

    # Handle other exceptions
    logger.error(f"Unhandled exception: {exc}", exc_info=True)

    return Response(
        {
            'error': {
                'code': 'INTERNAL_ERROR',
                'message': 'An unexpected error occurred',
                'details': {}
            }
        },
        status=status.HTTP_500_INTERNAL_SERVER_ERROR
    )
