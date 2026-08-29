from rest_framework import serializers


class ActorSerializer(serializers.Serializer):
    """Pessoa embutida em um movimento (responsible/returned_by/performed_by/received_by)."""

    user_id = serializers.CharField(required=False, allow_null=True)
    name = serializers.CharField()


class MovementSerializer(serializers.Serializer):
    """Representação de saída de um registro de movimentação (imutável)."""

    id = serializers.CharField(read_only=True)
    notebook_id = serializers.CharField()
    asset = serializers.CharField()
    type = serializers.ChoiceField(choices=["RETIRADA", "DEVOLUCAO"])
    responsible = ActorSerializer(required=False, allow_null=True)
    returned_by = ActorSerializer(required=False, allow_null=True)
    performed_by = ActorSerializer(required=False, allow_null=True)
    received_by = ActorSerializer(required=False, allow_null=True)
    date = serializers.DateTimeField()
    observation = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    condition = serializers.CharField(required=False, allow_null=True)
