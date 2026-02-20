import redis
from django.conf import settings
from django.db import connection
from rest_framework.authentication import BasicAuthentication
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.serializers import AuthTokenSerializer
from rest_framework.permissions import AllowAny
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView


class HealthLiveView(APIView):
    permission_classes = []

    def get(self, request):
        return Response({'status': 'ok'}, status=status.HTTP_200_OK)


class HealthReadyView(APIView):
    permission_classes = []

    def get(self, request):
        checks = {'database': False, 'redis': False}

        try:
            with connection.cursor() as cursor:
                cursor.execute('SELECT 1')
                cursor.fetchone()
            checks['database'] = True
        except Exception:
            checks['database'] = False

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
        serializer = AuthTokenSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, _ = Token.objects.get_or_create(user=user)
        return Response({'token': token.key}, status=status.HTTP_200_OK)
