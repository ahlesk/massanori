from rest_framework import serializers


class UserSerializer(serializers.Serializer):
    """Representação de saída de um usuário (funcionário)."""

    id = serializers.CharField(read_only=True)
    name = serializers.CharField()
    email = serializers.EmailField()
    department = serializers.CharField()
    active = serializers.BooleanField()


class UserCreateSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    department = serializers.CharField(max_length=100)
    active = serializers.BooleanField(required=False, default=True)
    password = serializers.CharField(write_only=True, min_length=6)


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
