from rest_framework import serializers


class DashboardOverviewSerializer(serializers.Serializer):
    total_applications = serializers.IntegerField()
    active_applications = serializers.IntegerField()
    status_counts = serializers.DictField()
    total_appointments = serializers.IntegerField()
    upcoming_appointments = serializers.IntegerField()