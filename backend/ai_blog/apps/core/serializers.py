from rest_framework import serializers


class AdminRegistrationSerializer(serializers.Serializer):
    username = serializers.CharField(min_length=3, max_length=150)
    password = serializers.CharField(min_length=8, write_only=True)
    invite_code = serializers.CharField(write_only=True)


class UserRegisterSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(min_length=8, write_only=True)
    confirm_password = serializers.CharField(min_length=8, write_only=True)
