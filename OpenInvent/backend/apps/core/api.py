from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import exception_handler as drf_exception_handler

from apps.core.exceptions import (
    AuthenticationError,
    ConflictError,
    DomainError,
    InvalidStateError,
    NotFoundError,
)

_STATUS_BY_EXCEPTION = (
    (NotFoundError, status.HTTP_404_NOT_FOUND),
    (ConflictError, status.HTTP_409_CONFLICT),
    (InvalidStateError, status.HTTP_422_UNPROCESSABLE_ENTITY),
    (AuthenticationError, status.HTTP_401_UNAUTHORIZED),
    (DomainError, status.HTTP_400_BAD_REQUEST),
)


def custom_exception_handler(exc, context):
    """Traduz exceções de domínio (services) em respostas HTTP padronizadas."""
    for exc_class, http_status in _STATUS_BY_EXCEPTION:
        if isinstance(exc, exc_class):
            return Response({"detail": exc.message}, status=http_status)

    return drf_exception_handler(exc, context)
