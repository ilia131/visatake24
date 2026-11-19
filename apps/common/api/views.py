from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework import status

from drf_spectacular.utils import extend_schema
@extend_schema(
    responses={
        200: {
            "type": "object",
            "properties": {
                "success": {"type": "boolean"},
                "service": {"type": "string"},
                "status": {"type": "string"},
            },
        }
    }
)
class HealthCheckAPIView(APIView):

    permission_classes = [AllowAny]
    authentication_classes = []

    def get(self, request):

        return Response(
            {
                "success": True,
                "service": "VoyaVisa API",
                "status": "healthy",
            },
            status=status.HTTP_200_OK
        )