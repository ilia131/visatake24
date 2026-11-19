
from rest_framework import serializers

from apps.visas.models import VisaApplicationHistory


class VisaApplicationHistorySerializer(serializers.ModelSerializer):

    changed_by_name = serializers.SerializerMethodField()

    class Meta:
        model = VisaApplicationHistory
        fields = [
            "id",
            "old_status",
            "new_status",
            "description",
            "changed_by_name",
            "created_at",
        ]

    def get_changed_by_name(self, obj):
        if not obj.changed_by:
            return None

        return str(obj.changed_by)
