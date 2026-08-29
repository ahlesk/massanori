STATUS_EM_ESTOQUE = "EM_ESTOQUE"
STATUS_EM_USO = "EM_USO"
STATUS_MANUTENCAO = "MANUTENCAO"
STATUS_INATIVO = "INATIVO"

STATUS_CHOICES = [STATUS_EM_ESTOQUE, STATUS_EM_USO, STATUS_MANUTENCAO, STATUS_INATIVO]

# Status que podem ser definidos manualmente via PUT. EM_USO só é atingido
# através do endpoint de checkout (Fase 2), para garantir que sempre exista
# um current_responsible e um registro RETIRADA associados.
STATUSES_ALLOWED_VIA_UPDATE = [STATUS_EM_ESTOQUE, STATUS_MANUTENCAO, STATUS_INATIVO]

TYPE_RETIRADA = "RETIRADA"
TYPE_DEVOLUCAO = "DEVOLUCAO"

# "etc." no enunciado: mantemos as duas condições que têm efeito na regra de
# negócio (AVARIA joga o notebook para MANUTENCAO); qualquer outro valor de
# condition é aceito e apenas registrado, mas tratado como "sem avaria".
CONDITION_BOM = "BOM"
CONDITION_AVARIA = "AVARIA"
CONDITION_CHOICES = [CONDITION_BOM, CONDITION_AVARIA]
