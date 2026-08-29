"""View: só faz parsing de request/response. Toda regra de negócio vive em NotebookService."""
from rest_framework import status as http_status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.utils import serialize_doc
from apps.movements.serializers import MovementSerializer
from apps.notebooks.serializers import (
    CheckoutSerializer,
    NotebookCreateSerializer,
    NotebookSerializer,
    NotebookUpdateSerializer,
    ReturnSerializer,
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


def _actor_from_request(request) -> dict:
    """Monta o objeto {user_id, name} do operador logado que está
    executando a ação (performed_by/received_by)."""
    return {"user_id": request.user.id, "name": request.user.name}


class NotebookCheckoutView(APIView):
    service = NotebookService()

    def post(self, request, asset):
        serializer = CheckoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        notebook = self.service.checkout(
            asset,
            user_id=serializer.validated_data["user_id"],
            performed_by=_actor_from_request(request),
            observation=serializer.validated_data.get("observation", ""),
        )
        return Response(NotebookSerializer(serialize_doc(notebook)).data)


class NotebookReturnView(APIView):
    service = NotebookService()

    def post(self, request, asset):
        serializer = ReturnSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        notebook = self.service.return_notebook(
            asset,
            received_by=_actor_from_request(request),
            condition=serializer.validated_data.get("condition"),
            observation=serializer.validated_data.get("observation", ""),
        )
        return Response(NotebookSerializer(serialize_doc(notebook)).data)


class NotebookHistoryView(APIView):
    service = NotebookService()

    def get(self, request, asset):
        movements = self.service.get_history(asset)
        data = MovementSerializer([serialize_doc(m) for m in movements], many=True).data
        return Response(data)
