"""Exceções de domínio, lançadas pelas services e traduzidas em respostas HTTP
pelo exception handler do DRF (ver apps.core.api.custom_exception_handler)."""


class DomainError(Exception):
    """Erro de negócio genérico."""

    default_message = "Erro de negócio."

    def __init__(self, message: str | None = None):
        super().__init__(message or self.default_message)
        self.message = message or self.default_message


class NotFoundError(DomainError):
    default_message = "Recurso não encontrado."


class ConflictError(DomainError):
    """Ex.: asset ou email duplicado."""

    default_message = "Recurso já existe."


class InvalidStateError(DomainError):
    """Ex.: tentar retirar um notebook que não está EM_ESTOQUE."""

    default_message = "Operação não permitida para o estado atual do recurso."


class AuthenticationError(DomainError):
    """Credenciais inválidas no login (email/senha)."""

    default_message = "E-mail ou senha inválidos."
