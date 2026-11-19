
from rest_framework import status
from rest_framework.generics import ListCreateAPIView, RetrieveAPIView ,UpdateAPIView
from rest_framework.permissions import IsAuthenticated , IsAdminUser
from rest_framework.response import Response

from drf_spectacular.utils import extend_schema

from apps.visas.models import VisaApplication
from apps.visas.api.pagination import VisaApplicationPagination
from apps.visas.api.serializers.application import (
    VisaApplicationCreateSerializer,
    VisaApplicationSerializer,
)

from apps.visas.selectors.applications import (
    get_user_applications,
)

from apps.visas.services.applications import (
    create_visa_application,
)


from apps.visas.api.serializers.application import (
    VisaApplicationStatusUpdateSerializer,
    VisaApplicationSerializer,
)
from apps.visas.services.applications import update_application_status
class VisaApplicationListCreateAPIView(ListCreateAPIView):

    permission_classes = [IsAuthenticated]
    pagination_class = VisaApplicationPagination

    def get_queryset(self):

        # جلوگیری از خطا هنگام تولید Swagger
        if getattr(self, "swagger_fake_view", False):
            return VisaApplication.objects.none()

        return get_user_applications(self.request.user)

    def get_serializer_class(self):

        if self.request.method == "POST":
            return VisaApplicationCreateSerializer

        return VisaApplicationSerializer

    @extend_schema(
        request=VisaApplicationCreateSerializer,
        responses={201: VisaApplicationSerializer},
    )
    def create(self, request, *args, **kwargs):

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        application = create_visa_application(
            user=request.user,
            **serializer.validated_data,
        )

        response_serializer = VisaApplicationSerializer(application)

        return Response(
            response_serializer.data,
            status=status.HTTP_201_CREATED,
        )


class VisaApplicationDetailAPIView(RetrieveAPIView):

    serializer_class = VisaApplicationSerializer
    permission_classes = [IsAuthenticated]

    lookup_field = "tracking_code"

    def get_queryset(self):

        # جلوگیری از خطا هنگام تولید Swagger
        if getattr(self, "swagger_fake_view", False):
            return VisaApplication.objects.none()

        return get_user_applications(self.request.user)



class VisaApplicationStatusUpdateAPIView(UpdateAPIView):
    serializer_class = VisaApplicationStatusUpdateSerializer
    permission_classes = [IsAdminUser]
    lookup_field = "tracking_code"

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return VisaApplication.objects.none()

        return VisaApplication.objects.select_related(
            "user",
            "country"
        )

    def perform_update(self, serializer):
        application = update_application_status(
            application=serializer.instance,
            changed_by=self.request.user,
            **serializer.validated_data
        )

        serializer.instance = application
