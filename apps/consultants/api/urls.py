
from django.urls import path

from apps.consultants.api.views.consultant import (
    ConsultantListAPIView,
    ConsultantDetailAPIView,
)

from apps.consultants.api.views.consultant_admin import (
    ConsultantAdminListCreateAPIView,
    ConsultantAdminDetailAPIView,
)
from apps.consultants.api.views.assignment import (
    AssignmentAdminListAPIView,
    AssignmentCreateAPIView,
    MyAssignmentsAPIView,
    AssignmentStatusUpdateAPIView,
)
urlpatterns = [
    # Public API
    path("", ConsultantListAPIView.as_view(), name="consultant-list"),

    # Admin API
    path("manage/", ConsultantAdminListCreateAPIView.as_view(), name="consultant-admin-list"),
    path("manage/<int:pk>/", ConsultantAdminDetailAPIView.as_view(), name="consultant-admin-detail"),
      path(
        "assignments/manage/",
        AssignmentAdminListAPIView.as_view(),
        name="assignment-admin-list",
    ),
    path(
        "assignments/assign/",
        AssignmentCreateAPIView.as_view(),
        name="assignment-create",
    ),

    # پنل مشاور
    path(
        "my-assignments/",
        MyAssignmentsAPIView.as_view(),
        name="my-assignments",
    ),
    path(
        "my-assignments/<int:pk>/status/",
        AssignmentStatusUpdateAPIView.as_view(),
        name="assignment-status-update",
    ),
    path("<slug:slug>/", ConsultantDetailAPIView.as_view(), name="consultant-detail"),
]
