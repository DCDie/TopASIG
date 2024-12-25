from rest_framework import serializers

from apps.ensurance.constants import (
    GreenCardVehicleCategories,
    GreenCardZones,
    OperationModes,
    TermInsurance,
    Territories,
)


class CalculateRCAInputSerializer(serializers.Serializer):
    OperatingModes = serializers.ChoiceField(choices=OperationModes.choices)
    PersonIsJuridical = serializers.BooleanField(default=False)
    Territory = serializers.ChoiceField(choices=Territories.choices)
    IDNX = serializers.CharField(
        required=False, allow_blank=True, allow_null=True, max_length=13, min_length=13, help_text="IDNP or IDNO"
    )
    VehicleRegistrationCertificateNumber = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True,
        max_length=9,
        min_length=9,
        help_text="Vehicle Registration Certificate Number",
    )


class CalculateGreenCardInputSerializer(serializers.Serializer):
    GreenCardZone = serializers.ChoiceField(choices=GreenCardZones.choices)
    TermInsurance = serializers.ChoiceField(choices=TermInsurance.choices)
    IDNX = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True,
        help_text="IDNP or IDNO",
        max_length=13,
        min_length=13,
    )
    VehicleRegistrationCertificateNumber = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True,
        max_length=9,
        min_length=9,
        help_text="Vehicle Registration Certificate Number",
    )


class CalculateRCAOutputSerializer(serializers.Serializer):
    PrimeSum = serializers.DecimalField(max_digits=15, decimal_places=2)
    BonusMalusClass = serializers.IntegerField()
    IsSuccess = serializers.BooleanField()
    ErrorMessage = serializers.CharField(allow_null=True, allow_blank=True)


class CalculateGreenCardOutputSerializer(serializers.Serializer):
    PrimeSum = serializers.DecimalField(max_digits=15, decimal_places=2)
    BonusMalusClass = serializers.IntegerField()
    IsSuccess = serializers.BooleanField()
    ErrorMessage = serializers.CharField(allow_null=True, allow_blank=True)
    Territory = serializers.ChoiceField(choices=Territories.choices)
    PersonFirstName = serializers.CharField(allow_null=True, allow_blank=True)
    PersonLastName = serializers.CharField(allow_null=True, allow_blank=True)
    VehicleMark = serializers.CharField(allow_null=True, allow_blank=True)
    VehicleModel = serializers.CharField(allow_null=True, allow_blank=True)
    VehicleRegistrationNumber = serializers.CharField(allow_null=True, allow_blank=True)

    # Additional fields as per later WSDL sections
    PrimeSumMDL = serializers.DecimalField(max_digits=15, decimal_places=2)
    ExchangeRate = serializers.DecimalField(max_digits=15, decimal_places=4)
    VehicleCategory = serializers.ChoiceField(
        allow_null=True, allow_blank=True, choices=GreenCardVehicleCategories.choices
    )
