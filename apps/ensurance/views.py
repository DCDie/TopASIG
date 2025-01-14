from django.db import transaction
from django.http import HttpResponse
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.serializers import Serializer
from rest_framework.viewsets import GenericViewSet
from zeep.helpers import serialize_object

from apps.ensurance.constants import ContractType
from apps.ensurance.helpers import insert_image_into_pdf
from apps.ensurance.models import File
from apps.ensurance.rca import RcaExportServiceClient
from apps.ensurance.serializers import (
    CalculateGreenCardInputSerializer,
    CalculateGreenCardOutputSerializer,
    CalculateRCAInputSerializer,
    CalculateRCAOutputSerializer,
    GetFileRequestSerializer,
    GreenCardDocumentModelSerializer,
    SaveRcaDocumentSerializer,
)
from apps.ensurance.tasks import download_rcai_document


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

        # TODO: Use this when BNM will fix RCA API
        # # Validate and serialize the response
        # output_serializer = CalculateRCAOutputSerializer(data=serialize_object(response))
        # output_serializer.is_valid(raise_exception=True)
        # return Response(output_serializer.data, status=status.HTTP_200_OK)

        # Validate and serialize the response
        import xml.etree.ElementTree as ET

        namespaces = {
            "soap": "http://schemas.xmlsoap.org/soap/envelope/",
            "ns": "http://172.30.255.11:5368/RcaExportService.asmx",
        }
        root = ET.fromstring(response.text)

        # Extract data into a dictionary
        response_data = {}
        calculate_result = root.find(".//ns:CalculateRCAIPremiumResult", namespaces)

        if calculate_result is not None:
            if calculate_result.find("ns:IsSuccess", namespaces).text.lower() == "false":
                response_data["detail"] = calculate_result.find("ns:ErrorMessage", namespaces).text
                return Response(response_data, status=status.HTTP_400_BAD_REQUEST)
            response_data["InsurersPrime"] = {"InsurerPrimeRCAI": []}
            for insurer in calculate_result.findall(".//ns:InsurerPrimeRCAI", namespaces):
                response_data["InsurersPrime"]["InsurerPrimeRCAI"].append(
                    {
                        "Name": insurer.find("ns:Name", namespaces).text,
                        "IDNO": insurer.find("ns:IDNO", namespaces).text,
                        "PrimeSum": float(insurer.find("ns:PrimeSum", namespaces).text),
                        "PrimeSumMDL": float(insurer.find("ns:PrimeSum", namespaces).text),
                    }
                )
            response_data["BonusMalusClass"] = int(calculate_result.find("ns:BonusMalusClass", namespaces).text)
            response_data["IsSuccess"] = calculate_result.find("ns:IsSuccess", namespaces).text.lower() == "true"
            response_data["Territory"] = calculate_result.find("ns:Territory", namespaces).text
            response_data["PersonFirstName"] = calculate_result.find("ns:PersonFirstName", namespaces).text
            response_data["PersonLastName"] = calculate_result.find("ns:PersonLastName", namespaces).text
            response_data["VehicleMark"] = calculate_result.find("ns:VehicleMark", namespaces).text
            response_data["VehicleModel"] = calculate_result.find("ns:VehicleModel", namespaces).text
            response_data["VehicleRegistrationNumber"] = calculate_result.find(
                "ns:VehicleRegistrationNumber", namespaces
            ).text
            response_data["AgeUnder23"] = calculate_result.find("ns:AgeUnder23", namespaces).text.lower() == "true"
            response_data["ExperienceUnder2"] = (
                calculate_result.find("ns:ExperienceUnder2", namespaces).text.lower() == "true"
            )

        output_serializer = CalculateRCAOutputSerializer(data=response_data)
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

            qr_code = serializer.validated_data.pop("qrCode")
            qr_code.is_used = True
            qr_code.save()

            # Call the SOAP method
            response = RcaExportServiceClient().save_rca_document(serializer.validated_data)
            DocumentId = response.Response["Id"]
            download_rcai_document.apply_async(args=[DocumentId])
            return Response({"DocumentId": DocumentId}, status=status.HTTP_200_OK)

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

            # Call the SOAP method
            response = RcaExportServiceClient().save_greencard_document(serializer.validated_data)

            return Response({"DocumentId": response.Response["Id"]}, status=status.HTTP_200_OK)

    @extend_schema(responses={200: Serializer})
    @action(
        detail=False,
        methods=["post"],
        url_path="calculate-medical-insurance",
        serializer_class=Serializer,
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

        # Some logic to calculate the cost
        return Response({}, status=status.HTTP_200_OK)

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
        if file and serializer.validated_data["ContractType"] == ContractType.RCAI:
            return HttpResponse(file.file.read(), content_type="application/pdf")

        # Call the SOAP method to get the file in case it does not exist in the database
        response = RcaExportServiceClient().get_file(DocumentId=pk, **serializer.validated_data)
        content = insert_image_into_pdf(response.FileContent)
        return HttpResponse(content, content_type="application/pdf")
