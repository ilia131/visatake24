from drf_spectacular.utils import extend_schema
from rest_framework import generics, status
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.exceptions import PermissionDenied

from apps.consultants.models import ConsultantAssignment
from apps.consultants.api.serializers.assignment import (
    AssignmentSerializer,
    AssignmentCreateSerializer,
    AssignmentStatusSerializer,
)
from apps.consultants.services.assignments import (
    assign_application,
    update_assignment_status,
)


class AssignmentAdminListAPIView(generics.ListAPIView):
    serializer_class = AssignmentSerializer
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        queryset = (
            ConsultantAssignment.objects
            .select_related("application", "consultant", "assigned_by")
            .order_by("-assigned_at")
        )

        status_value = self.request.query_params.get("status")
        if status_value:
            queryset = queryset.filter(status=status_value)

        return queryset


class AssignmentCreateAPIView(APIView):
    permission_classes = [IsAdminUser]

    @extend_schema(request=AssignmentCreateSerializer, responses={201: AssignmentSerializer})
    def post(self, request):
        serializer = AssignmentCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        assignment = assign_application(
            application_id=serializer.validated_data["application_id"],
            consultant_id=serializer.validated_data["consultant_id"],
            admin=request.user,
        )

        return Response(
            AssignmentSerializer(assignment).data,
            status=status.HTTP_201_CREATED,
        )


class MyAssignmentsAPIView(generics.ListAPIView):
    queryset = ConsultantAssignment.objects.none()
    serializer_class = AssignmentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        consultant = getattr(
            self.request.user,
            "consultant_profile",
            None,
        )

        if consultant is None:
            raise PermissionDenied("حساب شما پروفایل مشاور ندارد.")

        return (
            ConsultantAssignment.objects
            .filter(consultant=consultant, is_active=True)
            .select_related("application", "consultant")
            .order_by("-assigned_at")
        )


class AssignmentStatusUpdateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(request=AssignmentStatusSerializer, responses={200: AssignmentSerializer})
    def patch(self, request, pk):
        consultant = getattr(
            request.user,
            "consultant_profile",
            None,
        )

        if consultant is None:
            raise PermissionDenied("شما دسترسی مشاور ندارید.")

        serializer = AssignmentStatusSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        assignment = update_assignment_status(
            assignment_id=pk,
            consultant=consultant,
            status=serializer.validated_data["status"],
            consultant_note=serializer.validated_data.get(
                "consultant_note", ""
            ),
        )

        return Response(AssignmentSerializer(assignment).data)
