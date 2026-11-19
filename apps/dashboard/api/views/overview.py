from drf_spectacular.utils import extend_schema
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.dashboard.selectors.overview import (
    get_user_dashboard_overview,
)
from apps.dashboard.api.serializers.overview import (
    DashboardOverviewSerializer,
)


class DashboardOverviewAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(responses=DashboardOverviewSerializer)
    def get(self, request):
        data = get_user_dashboard_overview(request.user)
        serializer = DashboardOverviewSerializer(data)
        return Response(serializer.data)