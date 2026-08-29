from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.utils import serialize_doc
from apps.movements.serializers import MovementSerializer
from apps.movements.services import MovementService


class MovementListView(APIView):
    service = MovementService()

    def get(self, request):
        movements = self.service.list_movements(asset=request.query_params.get("asset"))
        data = MovementSerializer([serialize_doc(m) for m in movements], many=True).data
        return Response(data)
