"""View: só faz parsing de request/response. Toda regra de negócio vive em UserService."""
from rest_framework import exceptions
from rest_framework import status as http_status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.utils import serialize_doc
from apps.users.serializers import LoginSerializer, UserCreateSerializer, UserSerializer
from apps.users.services import UserService


class UserListCreateView(APIView):
    service = UserService()

    def get_permissions(self):
        # Cadastro fica aberto (bootstrap do sistema); listar exige login.
        if self.request.method == "POST":
            return [AllowAny()]
        return [IsAuthenticated()]

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
        # Cadastro aberto vale só para usuários com login (bootstrap).
        # Responsáveis (sem e-mail/senha) só podem ser criados por quem já
        # está logado, para não permitir criação anônima de registros.
        if not serializer.validated_data.get("password") and not request.user.is_authenticated:
            raise exceptions.NotAuthenticated()
        user = self.service.create_user(serializer.validated_data)
        return Response(UserSerializer(serialize_doc(user)).data, status=http_status.HTTP_201_CREATED)


class AuthLoginView(APIView):
    """POST /api/auth/login/ — qualquer usuário criado via /api/users/ já
    consegue logar aqui imediatamente, sem passo de ativação."""

    permission_classes = [AllowAny]
    service = UserService()

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user, token = self.service.login(**serializer.validated_data)
        return Response({"token": token, "user": UserSerializer(serialize_doc(user)).data})


class AuthLogoutView(APIView):
    service = UserService()

    def post(self, request):
        self.service.logout(request.user.id)
        return Response(status=http_status.HTTP_204_NO_CONTENT)


class AuthMeView(APIView):
    def get(self, request):
        user = request.user
        return Response(
            {
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "department": user.department,
                "active": user.active,
            }
        )
