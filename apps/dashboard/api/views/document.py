from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from apps.dashboard.selectors.documents import get_user_documents
from apps.dashboard.api.serializers.document import (
    DashboardDocumentSerializer,
)


class DashboardDocumentListAPIView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = DashboardDocumentSerializer

    def get_queryset(self):
        return get_user_documents(self.request.user)