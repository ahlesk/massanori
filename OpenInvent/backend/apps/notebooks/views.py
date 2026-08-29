"""View: só faz parsing de request/response. Toda regra de negócio vive em NotebookService."""
from rest_framework import status as http_status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.utils import serialize_doc
from apps.notebooks.serializers import (
    NotebookCreateSerializer,
    NotebookSerializer,
    NotebookUpdateSerializer,
)
from apps.notebooks.services import NotebookService


class NotebookListCreateView(APIView):
    service = NotebookService()

    def get(self, request):
        notebooks = self.service.list_notebooks(
            status=request.query_params.get("status"),
            search=request.query_params.get("asset"),
        )
        data = NotebookSerializer([serialize_doc(n) for n in notebooks], many=True).data
        return Response(data)

    def post(self, request):
        serializer = NotebookCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        notebook = self.service.create_notebook(serializer.validated_data)
        return Response(
            NotebookSerializer(serialize_doc(notebook)).data, status=http_status.HTTP_201_CREATED
        )


class NotebookDetailView(APIView):
    service = NotebookService()

    def get(self, request, asset):
        notebook = self.service.get_notebook(asset)
        return Response(NotebookSerializer(serialize_doc(notebook)).data)

    def put(self, request, asset):
        serializer = NotebookUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        notebook = self.service.update_notebook(asset, serializer.validated_data)
        return Response(NotebookSerializer(serialize_doc(notebook)).data)

    def delete(self, request, asset):
        """Soft delete: nunca remove o documento, apenas move o status para INATIVO."""
        self.service.soft_delete_notebook(asset)
        return Response(status=http_status.HTTP_204_NO_CONTENT)
