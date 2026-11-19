
from rest_framework import generics, filters
from rest_framework.permissions import AllowAny
from django_filters.rest_framework import DjangoFilterBackend

from apps.consultants.api.serializers.consultant import (
    ConsultantSerializer,
)
from apps.consultants.selectors.consultants import (
    get_public_consultants,
)


class ConsultantListAPIView(generics.ListAPIView):
    serializer_class = ConsultantSerializer
    permission_classes = [AllowAny]

    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]

    filterset_fields = ["specialties__slug"]
    search_fields = ["full_name", "title", "bio"]
    ordering_fields = ["experience_years", "created_at"]
    ordering = ["display_order", "-created_at"]

    def get_queryset(self):
        return get_public_consultants()


class ConsultantDetailAPIView(generics.RetrieveAPIView):
    serializer_class = ConsultantSerializer
    permission_classes = [AllowAny]
    lookup_field = "slug"

    def get_queryset(self):
        return get_public_consultants()
