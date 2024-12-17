from rest_framework import serializers

from apps.ensurance.constants import (
    GreenCardVehicleCategories,
    GreenCardZones,
    OperationModes,
    TermInsurance,
    Territories,
)


class CalculateRCAIPremiumInputSerializer(serializers.Serializer):
    idnp = serializers.CharField(required=False, allow_blank=True, allow_null=True, help_text="IDNP of employee")
    operating_modes = serializers.ChoiceField(choices=OperationModes.choices)
    person_is_juridical = serializers.BooleanField()
    territory = serializers.ChoiceField(choices=Territories.choices)

    # Optional fields
    idnx = serializers.CharField(
        required=False, allow_blank=True, allow_null=True, max_length=13, min_length=13, help_text="IDNP or IDNO"
    )
    vrcn = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True,
        max_length=9,
        min_length=9,
        help_text="Vehicle Registration Certificate Number",
    )


class CalculateRCAEPremiumInputSerializer(serializers.Serializer):
    idnp = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True,
        help_text="IDNP of employee",
    )

    greencard_zone = serializers.ChoiceField(choices=GreenCardZones.choices)
    term_insurance = serializers.ChoiceField(choices=TermInsurance.choices)

    # Optional fields
    idnx = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True,
        help_text="IDNP or IDNO",
        max_length=13,
        min_length=13,
    )
    vrcn = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True,
        max_length=9,
        min_length=9,
        help_text="Vehicle Registration Certificate Number",
    )


class CalculateRCAIPremiumOutputSerializer(serializers.Serializer):
    PrimeSum = serializers.DecimalField(max_digits=15, decimal_places=2)
    BonusMalusClass = serializers.IntegerField()
    IsSuccess = serializers.BooleanField()
    ErrorMessage = serializers.CharField(allow_null=True, allow_blank=True)


class CalculateRCAEPremiumOutputSerializer(serializers.Serializer):
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
