from rest_framework import serializers

from apps.notebooks.constants import STATUS_CHOICES


class ResponsibleSerializer(serializers.Serializer):
    user_id = serializers.CharField()
    name = serializers.CharField()


class NotebookSerializer(serializers.Serializer):
    """Representação de saída de um notebook."""

    id = serializers.CharField(read_only=True)
    asset = serializers.CharField()
    brand = serializers.CharField()
    model = serializers.CharField()
    serial_number = serializers.CharField()
    status = serializers.ChoiceField(choices=STATUS_CHOICES)
    current_responsible = ResponsibleSerializer(allow_null=True)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)


class NotebookCreateSerializer(serializers.Serializer):
    asset = serializers.CharField(max_length=50)
    brand = serializers.CharField(max_length=100)
    model = serializers.CharField(max_length=100)
    serial_number = serializers.CharField(max_length=100)
    status = serializers.ChoiceField(choices=STATUS_CHOICES, required=False, default="EM_ESTOQUE")


class NotebookUpdateSerializer(serializers.Serializer):
    brand = serializers.CharField(max_length=100, required=False)
    model = serializers.CharField(max_length=100, required=False)
    serial_number = serializers.CharField(max_length=100, required=False)
    status = serializers.ChoiceField(choices=STATUS_CHOICES, required=False)
