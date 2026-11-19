from drf_spectacular.utils import extend_schema
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.dashboard.api.serializers.profile import (
    DashboardProfileSerializer,
)


class DashboardProfileAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(responses=DashboardProfileSerializer)
    def get(self, request):
        serializer = DashboardProfileSerializer(request.user)
        return Response(serializer.data)

    @extend_schema(request=DashboardProfileSerializer, responses=DashboardProfileSerializer)
    def patch(self, request):
        serializer = DashboardProfileSerializer(
            request.user,
            data=request.data,
            partial=True,
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data)