"""
Base service class for all business logic.
Implements the Service Layer pattern from SYSTEM_DESIGN.md
"""
import logging
from typing import TypeVar, Generic, Type, Optional, Any, Dict
from django.db import models
from django.core.exceptions import ValidationError
from abc import ABC, abstractmethod

T = TypeVar('T', bound=models.Model)

logger = logging.getLogger('ai_blog')


class ServiceError(Exception):
    """Base exception for service layer errors"""

    def __init__(self, message: str, code: str = "SERVICE_ERROR", details: Dict = None):
        self.message = message
        self.code = code
        self.details = details or {}
        super().__init__(self.message)

    def to_dict(self):
        """Convert to API response format"""
        return {
            'error': {
                'code': self.code,
                'message': self.message,
                'details': self.details
            }
        }


class BaseService(ABC, Generic[T]):
    """
    Abstract base service providing common functionality.
    Enforces separation: Services handle business logic, Models handle persistence.
    """

    model_class: Type[T]
    logger_name: str = None

    def __init__(self):
        self._logger = logger.getChild(self.logger_name or self.__class__.__name__)

    def log_execution(self, method_name: str, **kwargs):
        """Log service method execution with context"""
        self._logger.info(
            f"{self.__class__.__name__}.{method_name} called",
            extra={'context': kwargs}
        )

    def handle_exception(self, exc: Exception, context: Dict = None) -> ServiceError:
        """Convert exceptions to ServiceError with proper context"""
        context = context or {}
        self._logger.error(
            f"Exception in {self.__class__.__name__}: {str(exc)}",
            extra={'context': context},
            exc_info=True
        )
        return ServiceError(str(exc), details=context)

    def validate_input(self, data: Dict, validators: Dict = None) -> None:
        """
        Validate input data before processing.
        validators: {field_name: callable}
        """
        for field, validator in (validators or {}).items():
            if field in data:
                try:
                    validator(data[field])
                except (ValueError, ValidationError) as e:
                    raise ServiceError(
                        f"Validation failed for {field}: {str(e)}",
                        code="VALIDATION_ERROR"
                    )

    @abstractmethod
    def execute(self, *args, **kwargs) -> Any:
        """Main execution method - must be implemented by subclasses"""
        raise NotImplementedError
