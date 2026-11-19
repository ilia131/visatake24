from rest_framework.permissions import BasePermission

from apps.consultants.models import Consultant


def can_review_payment(user):
    return user.is_authenticated and (
        user.is_staff
        or user.role == user.Role.MANAGER
        or user.has_perm("appointments.review_payment")
    )


class IsAppointmentOwner(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        return obj.user_id == request.user.pk


class IsAssignedConsultant(IsAppointmentOwner):
    def has_permission(self, request, view):
        return super().has_permission(request, view) and Consultant.objects.filter(user=request.user).exists()

    def has_object_permission(self, request, view, obj):
        return obj.availability.consultant.user_id == request.user.pk


class IsAdminPaymentReviewer(BasePermission):
    def has_permission(self, request, view):
        return can_review_payment(request.user)
