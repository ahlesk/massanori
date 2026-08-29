"""View: só faz parsing de request/response. Toda regra de negócio vive em UserService."""
from rest_framework import status as http_status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.utils import serialize_doc
from apps.users.serializers import UserCreateSerializer, UserSerializer
from apps.users.services import UserService


class UserListCreateView(APIView):
    service = UserService()

    def get(self, request):
        active_param = request.query_params.get("active")
        active = None
        if active_param is not None:
            active = active_param.lower() in ("1", "true", "yes")

        users = self.service.list_users(active=active)
        data = UserSerializer([serialize_doc(u) for u in users], many=True).data
        return Response(data)

    def post(self, request):
        serializer = UserCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = self.service.create_user(serializer.validated_data)
        return Response(UserSerializer(serialize_doc(user)).data, status=http_status.HTTP_201_CREATED)
