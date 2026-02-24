import redis
from django.conf import settings
from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model
from django.db import connection
from rest_framework.authentication import BasicAuthentication
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import AdminRegistrationSerializer, UserRegisterSerializer
from .services.admin_auth import AdminAuthService
from .services.user_auth import UserAuthService

User = get_user_model()


class HealthLiveView(APIView):
    permission_classes = []

    def get(self, request):
        return Response({'status': 'ok'}, status=status.HTTP_200_OK)


class HealthReadyView(APIView):
    permission_classes = []

    def get(self, request):
        queue_always_sync = getattr(settings, 'QUEUE_ALWAYS_SYNC', False)
        checks = {'database': False, 'redis': queue_always_sync}

        try:
            with connection.cursor() as cursor:
                cursor.execute('SELECT 1')
                cursor.fetchone()
            checks['database'] = True
        except Exception:
            checks['database'] = False

        if not queue_always_sync:
            try:
                redis_client = redis.Redis.from_url(settings.REDIS_URL)
                checks['redis'] = bool(redis_client.ping())
            except Exception:
                checks['redis'] = False

        overall = all(checks.values())
        return Response(
            {'status': 'ok' if overall else 'degraded', 'checks': checks},
            status=status.HTTP_200_OK if overall else status.HTTP_503_SERVICE_UNAVAILABLE
        )


class TokenAuthView(APIView):
    authentication_classes = [BasicAuthentication]
    permission_classes = [AllowAny]

    def post(self, request):
        email = (request.data.get('email') or request.data.get('username') or '').strip().lower()
        password = request.data.get('password') or ''
        user = authenticate(request=request, username=email, password=password)
        if user is None and '@' in email:
            existing = User.objects.filter(email__iexact=email).first()
            if existing:
                user = authenticate(request=request, username=existing.username, password=password)
        if user is None:
            return Response(
                {'error': {'code': 'AUTH_FAILED', 'message': 'Invalid credentials', 'details': {}}},
                status=status.HTTP_400_BAD_REQUEST
            )
        token, _ = Token.objects.get_or_create(user=user)
        return Response(
            {
                'token': token.key,
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'username': user.username,
                }
            },
            status=status.HTTP_200_OK
        )


class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserRegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        service = UserAuthService()
        try:
            user_data = service.register_user(
                email=data['email'],
                password=data['password'],
                confirm_password=data['confirm_password'],
            )
        except Exception as exc:
            if hasattr(exc, "to_dict"):
                return Response(exc.to_dict(), status=status.HTTP_400_BAD_REQUEST)
            return Response(
                {
                    "error": {
                        "code": "REGISTRATION_ERROR",
                        "message": str(exc),
                        "details": {},
                    }
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = service.model_class.objects.get(id=user_data["id"])
        token, _ = Token.objects.get_or_create(user=user)
        return Response(
            {
                'success': True,
                'token': token.key,
                'user': user_data,
            },
            status=status.HTTP_201_CREATED
        )


class AdminRegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = AdminRegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        service = AdminAuthService()
        try:
            user_data = service.register_admin(
                username=data["username"],
                password=data["password"],
                invite_code=data["invite_code"],
            )
        except Exception as exc:
            if hasattr(exc, "to_dict"):
                return Response(exc.to_dict(), status=status.HTTP_400_BAD_REQUEST)
            return Response(
                {
                    "error": {
                        "code": "ADMIN_REGISTRATION_ERROR",
                        "message": str(exc),
                        "details": {},
                    }
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = service.model_class.objects.get(id=user_data["id"])
        token, _ = Token.objects.get_or_create(user=user)
        return Response(
            {
                "success": True,
                "user": user_data,
                "token": token.key,
            },
            status=status.HTTP_201_CREATED,
        )
