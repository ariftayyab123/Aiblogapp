import secrets

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password

from .base import BaseService, ServiceError


User = get_user_model()


class AdminAuthService(BaseService):
    model_class = User
    logger_name = "admin_auth"

    def execute(self, *args, **kwargs):
        return self.register_admin(*args, **kwargs)

    def register_admin(self, username: str, password: str, invite_code: str):
        expected_code = getattr(settings, 'ADMIN_INVITE_CODE', '')
        if not expected_code:
            raise ServiceError(
                "Admin registration is not configured.",
                code="ADMIN_REGISTRATION_DISABLED",
            )

        if not secrets.compare_digest(invite_code, expected_code):
            raise ServiceError(
                "Invalid invite code.",
                code="INVALID_INVITE_CODE",
            )

        if User.objects.filter(username=username).exists():
            raise ServiceError(
                "Username already exists.",
                code="USERNAME_EXISTS",
            )

        try:
            validate_password(password)
        except Exception as exc:
            raise ServiceError(
                f"Password validation failed: {exc}",
                code="WEAK_PASSWORD",
            ) from exc

        user = User.objects.create_user(
            username=username,
            password=password,
            is_staff=True,
            is_superuser=True,
        )

        return {
            "id": user.id,
            "username": user.username,
            "is_staff": user.is_staff,
        }
