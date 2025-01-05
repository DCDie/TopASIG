from rest_framework import serializers

from apps.ensurance.constants import (
    ContractType,
    DocumentType,
    GreenCardVehicleCategories,
    GreenCardZones,
    OperationModes,
    OperationModesStrings,
    PaymentModes,
    PossessionBase,
    TermInsurance,
    Territories,
)
from apps.payment.constants import StatusChoices
from apps.payment.models import QrCode


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


# Serializers for save rca and green card documents


class AddressModelSerializer(serializers.Serializer):
    RegionName = serializers.CharField(required=False, allow_blank=True)
    Locality = serializers.CharField(required=False, allow_blank=True)
    Street = serializers.CharField(required=False, allow_blank=True)
    House = serializers.CharField(required=False, allow_blank=True)
    Block = serializers.CharField(required=False, allow_blank=True)
    Flat = serializers.CharField(required=False, allow_blank=True)


class CompanyModelSerializer(serializers.Serializer):
    IDNO = serializers.CharField(required=False, allow_blank=True)


class PhysicalPersonModelSerializer(serializers.Serializer):
    IdentificationCode = serializers.CharField(required=False, allow_blank=True)
    LastName = serializers.CharField(required=False, allow_blank=True)
    FirstName = serializers.CharField(required=False, allow_blank=True)
    MiddleName = serializers.CharField(required=False, allow_blank=True)
    BirthDate = serializers.DateTimeField()
    Phone = serializers.CharField(required=False, allow_blank=True)
    Address = AddressModelSerializer(required=False)
    IsFromTransnistria = serializers.BooleanField()
    PersonIsExternal = serializers.BooleanField()


class JuridicalPersonModelSerializer(serializers.Serializer):
    IdentificationCode = serializers.CharField(required=False, allow_blank=True)
    Name = serializers.CharField(required=False, allow_blank=True)
    Phone = serializers.CharField(required=False, allow_blank=True)
    Address = AddressModelSerializer(required=False)


class VehicleModelSerializer(serializers.Serializer):
    MarkName = serializers.CharField(required=False, allow_blank=True)
    Model = serializers.CharField(required=False, allow_blank=True)
    ProductionYear = serializers.IntegerField()
    RegistrationNumber = serializers.CharField(required=False, allow_blank=True)
    RegistrationCertificateNumber = serializers.CharField(required=False, allow_blank=True)
    CilinderVolume = serializers.IntegerField()
    TotalWeight = serializers.IntegerField()
    EnginePower = serializers.IntegerField()
    Seats = serializers.IntegerField()
    VinCode = serializers.CharField(required=False, allow_blank=True)
    IDNV = serializers.CharField(required=False, allow_blank=True)
    EngineNr = serializers.CharField(required=False, allow_blank=True)
    OwnerPersonalCode = serializers.CharField(required=False, allow_blank=True)


class BaseDocumentModelSerializer(serializers.Serializer):
    Company = CompanyModelSerializer(required=False)
    Broker = CompanyModelSerializer(required=False)
    InsuredPhysicalPerson = PhysicalPersonModelSerializer(required=False)
    InsuredJuridicalPerson = JuridicalPersonModelSerializer(required=False)
    InsuredVehicle = VehicleModelSerializer(required=False)
    InsuredTrailer = VehicleModelSerializer(required=False)
    StartDate = serializers.DateTimeField()
    PaymentDate = serializers.DateTimeField()
    TermInsurance = serializers.ChoiceField(choices=TermInsurance.choices)
    PaymentMode = serializers.ChoiceField(choices=PaymentModes.choices)
    FiscalDocumentNumber = serializers.CharField(required=False, allow_blank=True)
    PossessionBase = serializers.ChoiceField(choices=PossessionBase.choices)
    DocumentPossessionBaseNumber = serializers.CharField(required=False, allow_blank=True)
    DocumentPossessionBaseDate = serializers.DateTimeField(allow_null=True)
    DocumentPossessionBaseOtherTitle = serializers.CharField(required=False, allow_blank=True)
    DocumentPossessionBaseNote = serializers.CharField(required=False, allow_blank=True)


class RcaDocumentModelSerializer(BaseDocumentModelSerializer):
    OperatingMode = serializers.ChoiceField(choices=OperationModesStrings.choices)
    QRCode = serializers.PrimaryKeyRelatedField(
        required=True,
        allow_null=False,
        help_text="QR Code ID",
        queryset=QrCode.objects.filter(status=StatusChoices.PAID),
    )


class GreenCardDocumentModelSerializer(BaseDocumentModelSerializer):
    GreenCardZone = serializers.ChoiceField(choices=GreenCardZones.choices)
    QRCode = serializers.PrimaryKeyRelatedField(
        required=True,
        allow_null=False,
        help_text="QR Code ID",
        queryset=QrCode.objects.filter(status=StatusChoices.PAID),
    )


class GetFileRequestSerializer(serializers.Serializer):
    DocumentId = serializers.IntegerField()
    DocumentType = serializers.ChoiceField(choices=DocumentType.choices)
    ContractType = serializers.ChoiceField(choices=ContractType.choices)
