from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.db import transaction
from django.http import HttpResponse
from django.templatetags.static import static
from django.utils.translation import gettext as _
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.serializers import Serializer
from rest_framework.viewsets import GenericViewSet
from zeep.helpers import serialize_object

from apps.ensurance.constants import ContractType
from apps.ensurance.donaris import MedicinaAPI
from apps.ensurance.models import File, MedicalInsuranceCompany, RCACompany
from apps.ensurance.rca import RcaExportServiceClient
from apps.ensurance.serializers import (
    CalculateGreenCardInputSerializer,
    CalculateGreenCardOutputSerializer,
    CalculateRCAInputSerializer,
    CalculateRCAOutputSerializer,
    GetFileRequestSerializer,
    GreenCardDocumentModelSerializer,
    RootReturnSerializer,
    RootSerializer,
    SaveRcaDocumentSerializer,
    SendFileRequestSerializer,
)
from apps.ensurance.tasks import download_and_merge_documents


class RcaViewSet(GenericViewSet):
    """
    A viewset for performing RCA-related operations, such as calculations and saving documents.

    This class extends GenericViewSet and provides multiple endpoints for managing RCA and related
    documents. It handles operations such as calculating RCA costs, saving RCA and Green Card
    documents, calculating Green Card costs, calculating Medical Insurance costs, and retrieving
    RCA files. Each operation is handled by a separate method with appropriate serializers and
    responses.

    Attributes:
        permission_classes (list): List of permission classes used to control access to these actions.
        authentication_classes (list): List of authentication classes used for these actions.
    """

    permission_classes = []
    authentication_classes = []
    serializer_class = Serializer

    @extend_schema(responses={200: CalculateRCAOutputSerializer})
    @action(
        detail=False,
        methods=["post"],
        url_path="calculate-rca",
        serializer_class=CalculateRCAInputSerializer,
    )
    def calculate_rca(self, request):
        """
        Performs the RCA calculation by using a SOAP service client and returns a serialized
        response containing the result. The input is validated through a serializer, processed
        using the SOAP client, and the output is validated and serialized before sending
        it back to the client.

        Parameters:
            request (Request): The HTTP request carrying the serialized input data required
                               for the RCA calculation.

        Returns:
            Response: An HTTP response containing the serialized output data from the RCA
                      calculation with a status of 200 OK.
        """
        # Validate input data
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Call the SOAP method
        response = RcaExportServiceClient().calculate_rca(serializer.validated_data)

        # Get settings for RCA companies and link them to the response
        rca_companies = RCACompany.objects.all()
        rca_companies = {company.idno: company for company in rca_companies}

        for insurer in response.InsurersPrime.InsurerPrimeRCAI:
            company = rca_companies.get(insurer.IDNO)
            if not company:
                company = RCACompany.objects.create(
                    name=insurer.Name, idno=insurer.IDNO, is_active=True, is_public=True
                )
            if not company.is_public:
                response.InsurersPrime.InsurerPrimeRCAI.remove(insurer)
            insurer["is_active"] = company.is_active if company else False
            insurer["logo"] = company.logo.url if company.logo else static("public/Logo.png")

        # Validate and serialize the response
        output_serializer = CalculateRCAOutputSerializer(data=serialize_object(response))
        output_serializer.is_valid(raise_exception=True)
        return Response(output_serializer.data, status=status.HTTP_200_OK)

    @extend_schema(responses={200: Serializer})
    @action(
        detail=False,
        methods=["post"],
        url_path="save-rca",
        serializer_class=SaveRcaDocumentSerializer,
    )
    def save_rca(self, request):
        """
        Save RCA Document using the provided data. This method validates the input,
        marks the corresponding QR code as used, invokes an external SOAP method to save
        the RCA document, and returns the document ID in the response.

        Args:
            request (HttpRequest): The HTTP request object containing input data.

        Returns:
            Response: A Response object containing the document ID.

        Raises:
            ValidationError: If the input data is invalid.
        """
        with transaction.atomic():
            # Validate input data
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            operating_modes = serializer.validated_data.pop("OperatingModes")

            operating_modes_strings = {
                "1": "Usual",
                "2": "Minibus",
                "3": "IntercityBus",
                "4": "Taxi",
                "5": "RentACar",
            }

            qr_code = serializer.validated_data.pop("qrCode")
            serializer.validated_data["PaymentDate"] = qr_code.updated_at.date()
            serializer.validated_data["OperatingMode"] = operating_modes_strings[str(operating_modes)]
            qr_code.is_used = True
            qr_code.save()

            # Call the SOAP method
            response = RcaExportServiceClient().save_rca_document(serializer.validated_data)
            document_id = response.Response["Id"]
            download_and_merge_documents(document_id, ContractType.RCAI)
            return Response(
                {
                    "DocumentId": document_id,
                    "url": f"{settings.CSRF_TRUSTED_ORIGINS[0]}/api/rca/{document_id}/get-rca-file/?ContractType=RCAI&DocumentType=Contract",
                },
                status=status.HTTP_200_OK,
            )

    @extend_schema(responses={200: CalculateGreenCardOutputSerializer})
    @action(
        detail=False,
        methods=["post"],
        url_path="calculate-green-card",
        serializer_class=CalculateGreenCardInputSerializer,
    )
    def calculate_green_card(self, request):
        """
        Handles the calculation of Green Card information by validating incoming input
        data, invoking an external SOAP service, and returning the computed results.
        This method is implemented as a POST API action.

        Parameters:
            request (HttpRequest): The HTTP request object containing the POST request
            data.

        Returns:
            Response: An HTTP response containing serialized Green Card output
            data with a status code of 200.
        """
        # Validate input data
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Call the SOAP method
        response = RcaExportServiceClient().calculate_green_card(serializer.validated_data)

        # Get settings for RCA companies and link them to the response
        rca_companies = RCACompany.objects.all()
        rca_companies = {company.idno: company for company in rca_companies}

        for insurer in response.InsurersPrime.InsurerPrimeRCAE:
            company = rca_companies.get(insurer.IDNO)
            if not company:
                company = RCACompany.objects.create(
                    name=insurer.Name, idno=insurer.IDNO, is_active=True, is_public=True
                )
            if not company.is_public:
                response.InsurersPrime.InsurerPrimeRCAE.remove(insurer)
            insurer["is_active"] = company.is_active if company else False
            insurer["logo"] = company.logo.url if company.logo else static("public/Logo.png")

        output_serializer = CalculateGreenCardOutputSerializer(data=serialize_object(response))
        output_serializer.is_valid(raise_exception=True)
        return Response(output_serializer.data, status=status.HTTP_200_OK)

    @extend_schema(responses={200: Serializer})
    @action(
        detail=False,
        methods=["post"],
        url_path="save-green-card",
        serializer_class=GreenCardDocumentModelSerializer,
    )
    def save_green_card(self, request):
        """
        Saves a green card document by validating the incoming request data,
        invoking an external SOAP service via a client, and returning an
        appropriate HTTP response.

        Parameters:
            request: HttpRequest
                The HTTP request containing the data to be saved. Request data should
                match the serializer class schema for validation.

        Returns:
            Response
                An HTTP response indicating the status of the save operation. Returns
                an HTTP 200 response when the operation is successful.

        Raises:
            ValidationError
                Raised if the incoming request data fails validation based on the
                serializer schema.
            Other SOAP-related errors depending on the behavior of the external SOAP
            service client during the operation.
        """

        with transaction.atomic():
            # Validate input data
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            qr_code = serializer.validated_data.pop("qrCode")
            qr_code.is_used = True
            qr_code.save()

            serializer.validated_data["PaymentDate"] = qr_code.updated_at

            # Call the SOAP method
            response = RcaExportServiceClient().save_greencard_document(serializer.validated_data)

            document_id = response.Response["Id"]
            download_and_merge_documents(document_id, ContractType.CV)

            return Response(
                {
                    "DocumentId": document_id,
                    "url": f"{settings.CSRF_TRUSTED_ORIGINS[0]}/api/rca/{document_id}/get-rca-file/?ContractType=RCAI&DocumentType=Contract",
                },
                status=status.HTTP_200_OK,
            )

    @extend_schema(
        parameters=[GetFileRequestSerializer],
        responses={
            200: OpenApiResponse(
                description="RCA PDF file retrieved successfully.",
                response=HttpResponse(content_type="application/pdf"),
            )
        },
    )
    @action(
        detail=True,
        methods=["get"],
        url_path="get-rca-file",
        serializer_class=GetFileRequestSerializer,
    )
    def get_rca_file(self, request, pk: str):
        """
        Retrieves an RCA PDF file associated with a given document ID.

        The method uses a serializer to validate request query parameters and communicates with an external RCA
        Export Service to fetch the PDF file. An image is then embedded into the fetched file for customization,
        and the resulting file is returned as an HTTP response with a PDF content type.

        Args:
            request: The HTTP request object containing query parameters for fetching the RCA file.
            pk (str): The primary key that identifies the document for which the PDF is to be retrieved.

        Returns:
            HttpResponse: An HTTP response containing the modified PDF file with a content type of
            application/pdf.
        """
        serializer = self.get_serializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        file = File.objects.filter(external_id=pk).first()
        if file:
            return HttpResponse(file.file.read(), content_type="application/pdf")

        download_and_merge_documents(pk, serializer.validated_data["ContractType"])
        file = File.objects.filter(external_id=pk).first()
        return HttpResponse(file.file.read(), content_type="application/pdf")

    @action(
        detail=True,
        methods=["post"],
        url_path="send-file",
        serializer_class=SendFileRequestSerializer,
    )
    def send_file(self, request, pk: str):
        """
        Sends a file to the user by email.

        This method validates the incoming request data, fetches the file from the database, and sends it to the user
        via email. The file is attached to the email, and the user is notified about the successful operation.

        Parameters:
            request: The HTTP request object containing the data required for sending the file.
            pk: The primary key of the file to be sent.

        Returns:
            Response: An HTTP response indicating the status of the operation.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        file = File.objects.filter(external_id=pk).first()
        if not file:
            download_and_merge_documents(pk, serializer.validated_data["ContractType"])
            file = File.objects.filter(external_id=pk).first()
            if not file:
                return Response({"detail": "File not found."}, status=status.HTTP_404_NOT_FOUND)

        # Send the file to the user by email
        message = EmailMultiAlternatives(
            subject=_("Your file"),
            body=_("Please find the attached file."),
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[serializer.validated_data["email"]],
        )
        message.attach(file.file.name, file.file.read(), "application/pdf")
        message.send()

        return Response({"detail": "File sent successfully."}, status=status.HTTP_200_OK)


class MedicalInsuranceViewSet(GenericViewSet):
    """
    A viewset for performing RCA-related operations, such as calculations and saving documents.

    This class extends GenericViewSet and provides multiple endpoints for managing RCA and related
    documents. It handles operations such as calculating RCA costs, saving RCA and Green Card
    documents, calculating Green Card costs, calculating Medical Insurance costs, and retrieving
    RCA files. Each operation is handled by a separate method with appropriate serializers and
    responses.

    Attributes:
        permission_classes (list): List of permission classes used to control access to these actions.
        authentication_classes (list): List of authentication classes used for these actions.
    """

    permission_classes = []
    authentication_classes = []
    serializer_class = Serializer

    @action(
        detail=False,
        methods=["get"],
        url_path="medical-insurance-constants",
    )
    def get_medical_insurance_constants(self, request):
        data = MedicinaAPI().get_all_directories()
        return Response(data, status=status.HTTP_200_OK)

    @extend_schema(responses={200: RootReturnSerializer(many=True)})
    @action(
        detail=False,
        methods=["post"],
        url_path="calculate-medical-insurance",
        serializer_class=RootSerializer,
        filter_backends=[],
        pagination_class=None,
    )
    def calculate_medical_insurance(self, request):
        """
        Calculate the estimated cost of medical insurance based on input data.

        This endpoint validates the input data through the associated serializer.
        Upon successful validation, it processes the data and performs specific
        logic to compute the estimated medical insurance cost. The computed result
        is returned as part of the HTTP response.

        Arguments:
            request: REST framework's Request instance containing input data
                for calculating medical insurance.

        Returns:
            Response containing the result of the medical insurance calculation
            along with an appropriate HTTP status code.
        """
        # Validate input data
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = MedicinaAPI().calculate_tariff(serializer.validated_data)
        medical_insurance_company = MedicalInsuranceCompany.objects.first()
        data["DogMEDPH"][0]["IDNO"] = medical_insurance_company.idno
        data["DogMEDPH"][0]["Name"] = medical_insurance_company.name
        data["DogMEDPH"][0]["is_active"] = medical_insurance_company.is_active
        data["DogMEDPH"][0]["logo"] = (
            medical_insurance_company.logo.url if medical_insurance_company.logo else static("public/Logo.png")
        )
        return_data = RootReturnSerializer(data=[data], many=True)
        return_data.is_valid(raise_exception=True)
        return Response(return_data.data, status=status.HTTP_200_OK)
