from base64 import b64decode

from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import transaction
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from apps.ensurance.constants import FileTypes
from apps.ensurance.models import File
from apps.payment.mia_maib import MaibQrCodeService
from apps.payment.models import QrCode
from apps.payment.serializers import (
    QRCodeSerializer,
    SizeSerializer,
    VbPayeeQrDtoSerializer,
)


class QrCodeViewSet(GenericViewSet):
    """
    A viewset for managing QR codes and their related operations.

    This class provides two main functionalities: creating a new QR code and retrieving the
    status of an existing QR code. It includes methods to handle the creation of QR codes
    with specific dimensions based on user-provided inputs and query parameters, ensuring
    that the correct validation is applied before storing the QR code information in the
    database. It also enables the retrieval of the current status of a QR code by interfacing
    with an external service and updating the local database with the received status data.
    """

    serializer_class = VbPayeeQrDtoSerializer
    queryset = QrCode.objects.all()
    permission_classes = []
    authentication_classes = []
    lookup_field = "uuid"

    @extend_schema(
        request=VbPayeeQrDtoSerializer,
        responses=QRCodeSerializer,
        parameters=[
            OpenApiParameter(
                name="width",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                required=False,
                description="Width of the QR code in pixels. Defaults to 300.",
                default=300,
            ),
            OpenApiParameter(
                name="height",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                required=False,
                description="Height of the QR code in pixels. Defaults to 300.",
                default=300,
            ),
        ],
    )
    def create(self, request):
        """
        Creates a QR code based on the provided data and query parameters. This endpoint processes
        the incoming data, validates it, and generates a QR code both as text and an image. The
        generated QR code data is then stored in the database and returned in the response.

        Arguments:
            self: The instance of the class.
            request: The HTTP request object containing data and query parameters.

        Parameters:
            - width (int, optional): Width of the QR code in pixels. Defaults to 300.
            - height (int, optional): Height of the QR code in pixels. Defaults to 300.

        Raises:
            ValidationError: If input data or query parameters are invalid.

        Returns:
            dict: Serialized data representing the generated QR code including binary
            data or metadata as applicable.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data

        # Validate query parameters
        query_serializer = SizeSerializer(data=request.query_params)
        query_serializer.is_valid(raise_exception=True)

        with transaction.atomic():
            # Create the QR code and return the response
            instance = QrCode.objects.create()
            validated_data["order_id"] = str(instance.order_id)
            qrcode_service = MaibQrCodeService()
            response_data = qrcode_service.create_qr_code(validated_data, **query_serializer.validated_data)["result"]
            instance.uuid = response_data["qrId"]
            instance.type = response_data.get("type")
            instance.url = response_data.get("url")

            if response_data.get("qrAsImage"):
                with SimpleUploadedFile(f"{instance.uuid}.png", b64decode(response_data.get("qrAsImage"))) as f:
                    file = File.objects.create(
                        external_id=str(instance.uuid),
                        type=FileTypes.QR,
                        file=f,
                    )
                    instance.file = file
            instance.save()
            return Response(QRCodeSerializer(instance).data, status=status.HTTP_201_CREATED)

    @extend_schema(responses=QRCodeSerializer)
    @action(detail=True, methods=["get"], url_path="status")
    def get_status(self, request, uuid: str):
        """
        Handles the retrieval of the current status of a QR code.

        This method utilizes an external service to fetch the real-time status of
        a QR code using its unique identifier (UUID). The status, once fetched,
        is also updated in the local database record of the corresponding QR code.

        Parameters:
            request (HttpRequest): The HTTP request object containing the context of
                the request.
            uuid (str): A unique identifier for the QR code whose status needs to be
                fetched. This should correspond to a record in the local database.

        Returns:
            Response: An HTTP response object containing either the updated status
                information of the QR code or an error message in case of a failure.

        Raises:
            HTTPError: If there is an issue when attempting to fetch the status from
                the external service.
        """
        instance = get_object_or_404(QrCode, uuid=uuid)
        qrcode_service = MaibQrCodeService()
        response_data = qrcode_service.get_qr_status(uuid)

        # Update the status of the QR code in the database
        if response_data["result"]["status"] != instance.status:
            instance.status = response_data["result"]["status"]
            instance.save()
        return Response(QRCodeSerializer(instance).data)
