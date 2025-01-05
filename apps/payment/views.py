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
    """
    A Django ViewSet for creating and managing QR codes.

    This class provides functionality for creating QR codes and retrieving their
    status. It integrates with serializers to validate incoming data and sends
    requests to external services for QR code generation and status updates.

    :ivar serializer_class: The serializer class used to validate and process
        incoming requests.
    :type serializer_class: type
    :ivar queryset: The queryset to retrieve QR code objects from the database.
    :type queryset: type
    :ivar lookup_field: Field used to look up objects in the queryset.
    :type lookup_field: str
    :ivar permission_classes: List of permission classes that determine access
        control to the viewset.
    :type permission_classes: list
    :ivar authentication_classes: List of authentication classes used for
        verifying requests.
    :type authentication_classes: list
    """
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
        """
        Handles the creation of QR codes for payees based on the provided request data
        and optional query parameters (width and height). Validates the input data
        using serializers, invokes the QR code service, and returns the generated QR
        code or an appropriate error response.

        :param request: HTTP request object containing necessary data in the body for
            QR code creation. Accepts optional query parameters ``width`` and
            ``height`` to specify QR code dimensions.
        :type request: HttpRequest

        :return: HTTP response object with serialized QR code data on success or an
            error message with status code on failure.
        :rtype: Response

        :raises ValidationError: If the input data or query parameters are
            invalid after serializer validation.
        :raises HTTPError: If there is a server-side issue while handling the QR code
            generation.
        """
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
        """
        Handles the retrieval of status information for a specific QR code by interacting
        with an external API service. Updates the QR code status in the database if the
        API call is successful and returns the status data. Handles potential errors
        emerging from the API call.

        :param request: The HTTP request object.
        :type request: rest_framework.request.Request
        :param pk: The primary key of the QR code object to retrieve its status.
        :type pk: str or None
        :return: A Response object containing the QR code status or an error message.
        :rtype: rest_framework.response.Response
        """
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
