from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.core"
    label = "core"

    def ready(self):
        # Import local para não conectar ao Mongo em contextos que não precisam
        # (ex.: geração de migrations, shell de introspecção, etc.) além do runtime normal.
        from apps.core.db import ensure_indexes

        try:
            ensure_indexes()
        except Exception:
            # Não derruba o boot do Django se o Mongo ainda não estiver disponível
            # (ex.: primeiro `manage.py` antes do `docker compose up`).
            pass
