
from rest_framework.generics import ListAPIView
from rest_framework.permissions import AllowAny

from apps.visas.api.serializers.country import CountrySerializer
from apps.visas.selectors.applications import get_active_countries


class CountryListAPIView(ListAPIView):

    serializer_class = CountrySerializer

    permission_classes = [AllowAny]
    authentication_classes = []

    def get_queryset(self):
        return get_active_countries()
