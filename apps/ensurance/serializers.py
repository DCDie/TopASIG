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


class InsurerPrimeRCASerializer(serializers.Serializer):
    Name = serializers.CharField(max_length=255)
    IDNO = serializers.CharField(max_length=13, min_length=13)
    PrimeSum = serializers.DecimalField(max_digits=20, decimal_places=2)
    is_active = serializers.BooleanField(default=True)
    logo = serializers.URLField(
        allow_null=True,
        required=False,
        default="https://www.google.com/url?sa=i&url=https%3A%2F%2Fdataset.gov.md%2Fru%2Forganization%2F1015601000134&psig=AOvVaw0lWpKM2jNr6jxpf6d44FTo&ust=1736284024523000&source=images&cd=vfe&opi=89978449&ved=0CBQQjRxqFwoTCMDPkZyA4ooDFQAAAAAdAAAAABAE",
    )


class InsurersPrimeSerializer(serializers.Serializer):
    InsurerPrimeRCAI = InsurerPrimeRCASerializer(many=True)


class CalculateRCAOutputSerializer(serializers.Serializer):
    InsurersPrime = InsurersPrimeSerializer()
    BonusMalusClass = serializers.IntegerField()
    IsSuccess = serializers.BooleanField()
    ErrorMessage = serializers.CharField(allow_null=True, required=False)
    Territory = serializers.CharField(max_length=100)
    PersonFirstName = serializers.CharField(max_length=100)
    PersonLastName = serializers.CharField(max_length=100)
    VehicleMark = serializers.CharField(max_length=100)
    VehicleModel = serializers.CharField(max_length=100)
    VehicleRegistrationNumber = serializers.CharField(max_length=20)


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


class CompanyModelSerializer(serializers.Serializer):
    IDNO = serializers.CharField(required=False, allow_blank=True)


class PhysicalPersonModelSerializer(serializers.Serializer):
    IdentificationCode = serializers.CharField()
    BirthDate = serializers.DateField()
    IsFromTransnistria = serializers.BooleanField()
    PersonIsExternal = serializers.BooleanField()


class JuridicalPersonModelSerializer(serializers.Serializer):
    IdentificationCode = serializers.CharField()


class VehicleModelSerializer(serializers.Serializer):
    ProductionYear = serializers.IntegerField()
    RegistrationCertificateNumber = serializers.CharField(required=False, allow_blank=True)
    CilinderVolume = serializers.IntegerField()
    TotalWeight = serializers.IntegerField()
    EnginePower = serializers.IntegerField()
    Seats = serializers.IntegerField()


class SaveRcaDocumentSerializer(serializers.Serializer):
    Company = CompanyModelSerializer()
    InsuredPhysicalPerson = PhysicalPersonModelSerializer(required=False)
    InsuredJuridicalPerson = JuridicalPersonModelSerializer(required=False)
    InsuredVehicle = VehicleModelSerializer()
    StartDate = serializers.DateField()
    PaymentDate = serializers.DateField()
    PossessionBase = serializers.ChoiceField(choices=PossessionBase.choices, default=PossessionBase.PROPERTY)
    DocumentPossessionBaseDate = serializers.DateField()
    OperatingMode = serializers.ChoiceField(choices=OperationModesStrings.choices, default=OperationModesStrings.USUAL)
    qrCode = serializers.SlugRelatedField(
        help_text="QR Code UUID",
        queryset=QrCode.objects.filter(status=StatusChoices.PAID, is_used=False),
        slug_field="uuid",
    )


class GreenCardDocumentModelSerializer(serializers.Serializer):
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
    GreenCardZone = serializers.ChoiceField(choices=GreenCardZones.choices)
    qrCode = serializers.SlugRelatedField(
        required=True,
        allow_null=False,
        help_text="QR Code UUID",
        queryset=QrCode.objects.filter(status=StatusChoices.PAID, is_used=False),
        slug_field="uuid",
    )


class GetFileRequestSerializer(serializers.Serializer):
    DocumentType = serializers.ChoiceField(choices=DocumentType.choices, required=False, default=DocumentType.CONTRACT)
    ContractType = serializers.ChoiceField(choices=ContractType.choices, required=False, default=ContractType.RCAI)
