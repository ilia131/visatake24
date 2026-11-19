
from rest_framework import generics
from rest_framework.permissions import IsAdminUser

from apps.consultants.api.serializers.consultant_admin import (
    ConsultantAdminSerializer,
)
from apps.consultants.selectors.consultants import (
    get_all_consultants,
)
from apps.consultants.services.consultants import (
    create_consultant,
    update_consultant,
)


class ConsultantAdminListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = ConsultantAdminSerializer
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        return get_all_consultants()

    def perform_create(self, serializer):
        consultant = create_consultant(
            validated_data=serializer.validated_data
        )
        serializer.instance = consultant


class ConsultantAdminDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ConsultantAdminSerializer
    permission_classes = [IsAdminUser]
    lookup_field = "pk"

    def get_queryset(self):
        return get_all_consultants()

    def perform_update(self, serializer):
        consultant = update_consultant(
            consultant=serializer.instance,
            validated_data=serializer.validated_data,
        )
        serializer.instance = consultant
