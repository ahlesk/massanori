STATUS_EM_ESTOQUE = "EM_ESTOQUE"
STATUS_EM_USO = "EM_USO"
STATUS_MANUTENCAO = "MANUTENCAO"
STATUS_INATIVO = "INATIVO"

STATUS_CHOICES = [STATUS_EM_ESTOQUE, STATUS_EM_USO, STATUS_MANUTENCAO, STATUS_INATIVO]

# Status que podem ser definidos manualmente via PUT. EM_USO só é atingido
# através do endpoint de checkout (Fase 2), para garantir que sempre exista
# um current_responsible e um registro RETIRADA associados.
STATUSES_ALLOWED_VIA_UPDATE = [STATUS_EM_ESTOQUE, STATUS_MANUTENCAO, STATUS_INATIVO]
