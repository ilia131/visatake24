
from rest_framework import serializers

from apps.visas.models import Country


class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = [
            "id",
            "name",
            "name_en",
            "slug",
            "flag",
            "description",
        ]
