from rest_framework import serializers


class UserSerializer(serializers.Serializer):
    """Representação de saída de um usuário (funcionário)."""

    id = serializers.CharField(read_only=True)
    name = serializers.CharField()
    # Responsáveis (só retiram/devolvem notebooks) não têm e-mail nem login.
    email = serializers.EmailField(required=False, allow_null=True)
    department = serializers.CharField()
    active = serializers.BooleanField()


class UserCreateSerializer(serializers.Serializer):
    """Dois formatos aceitos:

    - usuário do sistema: name + department + email + password (pode logar);
    - responsável: só name + department (não loga; apenas retira/devolve
      notebooks).
    """

    name = serializers.CharField(max_length=150)
    email = serializers.EmailField(required=False)
    department = serializers.CharField(max_length=100)
    active = serializers.BooleanField(required=False, default=True)
    password = serializers.CharField(write_only=True, min_length=6, required=False)

    def validate_name(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError("Informe o nome.")
        return value

    def validate_department(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError("Informe o departamento.")
        return value

    def validate(self, attrs):
        has_email = bool(attrs.get("email"))
        has_password = bool(attrs.get("password"))
        if has_email != has_password:
            raise serializers.ValidationError(
                "Para criar um usuário com login, informe e-mail e senha juntos."
            )
        return attrs


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
