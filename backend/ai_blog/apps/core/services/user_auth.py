from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password

from .base import BaseService, ServiceError


User = get_user_model()


class UserAuthService(BaseService):
    model_class = User
    logger_name = "user_auth"

    def execute(self, *args, **kwargs):
        return self.register_user(*args, **kwargs)

    def register_user(self, email: str, password: str, confirm_password: str):
        normalized_email = (email or "").strip().lower()
        if not normalized_email:
            raise ServiceError("Email is required.", code="INVALID_EMAIL")

        if password != confirm_password:
            raise ServiceError("Passwords do not match.", code="PASSWORD_MISMATCH")

        if User.objects.filter(email__iexact=normalized_email).exists():
            raise ServiceError("Email already registered.", code="EMAIL_EXISTS")

        try:
            validate_password(password)
        except Exception as exc:
            raise ServiceError(
                f"Password validation failed: {exc}",
                code="WEAK_PASSWORD",
            ) from exc

        user = User.objects.create_user(
            username=normalized_email,
            email=normalized_email,
            password=password,
            is_staff=False,
            is_superuser=False,
        )
        return {
            "id": user.id,
            "email": user.email,
            "username": user.username,
        }
