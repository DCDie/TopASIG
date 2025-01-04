from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from requests import HTTPError
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from apps.payment.models import QrCode
from apps.payment.qr import QrCodeService
from apps.payment.serializers import (
    CreatePayeeQrResponseSerializer,
    GetQrStatusResponseSerializer,
    SizeSerializer,
    VbPayeeQrDtoSerializer,
)


class QrCodeViewSet(GenericViewSet):
    serializer_class = VbPayeeQrDtoSerializer
    queryset = QrCode.objects.all()
    lookup_field = "uuid"
    permission_classes = []
    authentication_classes = []

    @extend_schema(
        request=VbPayeeQrDtoSerializer,
        responses=CreatePayeeQrResponseSerializer,
        parameters=[
            OpenApiParameter(
                name="width",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                required=False,
                description="Width of the QR code in pixels. Defaults to 300.",
            ),
            OpenApiParameter(
                name="height",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                required=False,
                description="Height of the QR code in pixels. Defaults to 300.",
            ),
        ],
    )
    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data

        # Validate query parameters
        query_serializer = SizeSerializer(data=request.query_params)
        query_serializer.is_valid(raise_exception=True)

        qrcode_service = QrCodeService()
        try:
            response_data = qrcode_service.create_qr_code(validated_data, **query_serializer.validated_data)
            response_serializer = CreatePayeeQrResponseSerializer(data=response_data)
            if response_serializer.is_valid():
                return Response(response_serializer.data, status=status.HTTP_200_OK)
            else:
                return Response(
                    {"error": "Invalid response data from API."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        except HTTPError as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @extend_schema(responses=GetQrStatusResponseSerializer)
    @action(detail=True, methods=["get"], url_path="status")
    def get_status(self, request, pk=None):
        qr_code = self.get_object()
        # Request the API to get the status of the QR code
        qrcode_service = QrCodeService()
        try:
            response_data = qrcode_service.get_qr_status(qr_code.uuid)
            # Update the status of the QR code in the database
            qr_code.status = response_data.get("status")
            qr_code.save()
            return Response(response_data, status=status.HTTP_200_OK)
        except HTTPError as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
