from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from apps.ensurance.rca import RcaExportServiceClient
from apps.ensurance.serializers import (
    CalculateRCAEPremiumInputSerializer,
    CalculateRCAEPremiumOutputSerializer,
    CalculateRCAIPremiumInputSerializer,
    CalculateRCAIPremiumOutputSerializer,
)


class RcaViewSet(GenericViewSet):
    """
    A ViewSet to handle RCA-related SOAP operations.
    """

    @extend_schema(responses={200: CalculateRCAIPremiumOutputSerializer})
    @action(
        detail=False,
        methods=["post"],
        url_path="calculate-rcai-premium",
        serializer_class=CalculateRCAIPremiumInputSerializer,
    )
    def calculate_rcai_premium(self, request):
        """
        Handles the CalculateRCAIPremium SOAP method.
        """
        # Validate input data
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Call the SOAP method
        try:
            client = RcaExportServiceClient().authenticate()
            response = client.calculate_rcai_premium(serializer.validated_data)
        except Exception as e:
            return Response(
                {"detail": "An error occurred while processing the request.", "error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        # Validate and serialize the response
        output_serializer = CalculateRCAIPremiumOutputSerializer(data=response)
        output_serializer.is_valid(raise_exception=True)
        return Response(output_serializer.data, status=status.HTTP_200_OK)

    @extend_schema(responses={200: CalculateRCAEPremiumOutputSerializer})
    @action(
        detail=False,
        methods=["post"],
        url_path="calculate-rcae-premium",
        serializer_class=CalculateRCAEPremiumInputSerializer,
    )
    def calculate_rcae_premium(self, request):
        """
        Handles the CalculateRCAEPremium SOAP method.
        """
        # Validate input data
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Call the SOAP method
        try:
            client = RcaExportServiceClient().authenticate()
            response = client.calculate_rcae_premium(serializer.validated_data)
        except Exception as e:
            # Log the exception as needed
            return Response(
                {"detail": "An error occurred while processing the request.", "error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        # Validate and serialize the response
        output_serializer = CalculateRCAEPremiumOutputSerializer(data=response)
        output_serializer.is_valid(raise_exception=True)
        return Response(output_serializer.data, status=status.HTTP_200_OK)
