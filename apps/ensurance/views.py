from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.serializers import Serializer
from rest_framework.viewsets import GenericViewSet

from apps.ensurance.rca import RcaExportServiceClient
from apps.ensurance.serializers import (
    CalculateGreenCardInputSerializer,
    CalculateGreenCardOutputSerializer,
    CalculateRCAInputSerializer,
    CalculateRCAOutputSerializer, GreenCardDocumentModelSerializer, RcaDocumentModelSerializer,
    GetFileRequestSerializer,
)


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

    @extend_schema(responses={200: CalculateRCAOutputSerializer})
    @action(
        detail=False,
        methods=["post"],
        url_path="calculate-rca",
        serializer_class=CalculateRCAInputSerializer,
    )
    def calculate_rca(self, request):
        """
        Handles the calculation of RCA using SOAP services. The method validates the input
        data passed in the request, performs a call to the RCA calculation SOAP method,
        validates the SOAP response data, and serializes it for consistent structuring.


        Raises:
            ValidationError: If input data or the SOAP response data is invalid.

        Parameters:
            request (HttpRequest): The HTTP request object containing input data for RCA
                calculation.

        Returns:
            Response: An HTTP 200 response object with validated and serialized RCA
                calculation results.
        """
        # Validate input data
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Call the SOAP method
        response = RcaExportServiceClient().calculate_rca(serializer.validated_data)

        # Validate and serialize the response
        output_serializer = CalculateRCAOutputSerializer(data=response)
        output_serializer.is_valid(raise_exception=True)
        return Response(output_serializer.data, status=status.HTTP_200_OK)


    @extend_schema(responses={200: Serializer})
    @action(
        detail=False,
        methods=["post"],
        url_path="save-rca",
        serializer_class=RcaDocumentModelSerializer,
    )
    def save_rca(self, request):
        """
            save_rca(request)

            Handles the saving of RCA document by performing
            input validation and invoking a SOAP service call to save the document.

            Parameters:
            request : HttpRequest
                The HTTP request object containing data for the RCA document.

            Returns:
            Response
                A Response object with an empty body and HTTP 200 status code if the
                operation is successful.

            Raises:
            ValidationError
                If the input data is invalid according to the serializer.
        """
        # Validate input data
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Call the SOAP method
        response = RcaExportServiceClient().save_rca_document(serializer.validated_data)

        return Response({}, status=status.HTTP_200_OK)

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

        output_serializer = CalculateGreenCardOutputSerializer(data=response)
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
        # Validate input data
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Call the SOAP method
        response = RcaExportServiceClient().save_greencard_document(serializer.validated_data)

        return Response({}, status=status.HTTP_200_OK)

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

    @extend_schema(responses={200: Serializer})
    @action(
        detail=False,
        methods=["post"],
        url_path="get-rca-file",
        serializer_class=GetFileRequestSerializer,
    )
    def get_rca_file(self, request):
        """
        Handles the functionality to fetch an RCA file through a SOAP service call. Validates the
        provided request data and triggers the associated SOAP service method to retrieve the
        required file.

        Parameters:
            request: HttpRequest
                The incoming HTTP request carrying the required payload for requesting an RCA file.

        Returns:
            Response: The HTTP response object signaling success (200 OK) or an error status.

        Raises:
            ValidationError
                Raised if the serialized input data fails validation.

        Workflow:
        1. Accepts a POST request at the specified endpoint.
        2. Validates the incoming request data using the provided serializer.
        3. Invokes the `get_file` method of the `RcaExportServiceClient` SOAP service with the
           validated data.
        4. Returns an HTTP 200 OK response upon successful execution of the SOAP method.
        """
        # Validate input data
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Call the SOAP method
        response = RcaExportServiceClient().get_file(**serializer.validated_data)

        return Response({}, status=status.HTTP_200_OK)
