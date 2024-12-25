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
    CalculateRCAOutputSerializer,
)


class RcaViewSet(GenericViewSet):
    """
    A ViewSet to handle RCA-related SOAP operations.
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
        Calculates the RCA cost for a given set of input parameters.
        """
        # Validate input data
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Call the SOAP method
        response = RcaExportServiceClient().calculate_rca(**serializer.validated_data)

        # Validate and serialize the response
        output_serializer = CalculateRCAOutputSerializer(data=response)
        output_serializer.is_valid(raise_exception=True)
        return Response(output_serializer.data, status=status.HTTP_200_OK)

    @extend_schema(responses={200: CalculateGreenCardOutputSerializer})
    @action(
        detail=False,
        methods=["post"],
        url_path="calculate-green-card",
        serializer_class=CalculateGreenCardInputSerializer,
    )
    def calculate_green_card(self, request):
        """
        Calculates the Green Card cost for a given set of input parameters.
        """
        # Validate input data
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Call the SOAP method
        response = RcaExportServiceClient().calculate_green_card(**serializer.validated_data)

        output_serializer = CalculateGreenCardOutputSerializer(data=response)
        output_serializer.is_valid(raise_exception=True)
        return Response(output_serializer.data, status=status.HTTP_200_OK)

    @extend_schema(responses={200: Serializer})
    @action(
        detail=False,
        methods=["post"],
        url_path="calculate-medical-insurance",
        serializer_class=Serializer,
    )
    def calculate_medical_insurance(self, request):
        """
        Calculates the Medical Insurance cost for a given set of input parameters.
        """
        # Validate input data
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Some logic to calculate the cost
        return Response({}, status=status.HTTP_200_OK)
