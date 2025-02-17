from rest_framework import serializers

from apps.ensurance.constants import (
    ContractType,
    DocumentType,
    GreenCardVehicleCategories,
    GreenCardZones,
    OperationModes,
    PossessionBase,
    TermInsurance,
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
    GreenCardZone = serializers.ChoiceField(choices=GreenCardZones.choices, required=True)
    TermInsurance = serializers.ChoiceField(choices=TermInsurance.choices, required=True)
    IDNX = serializers.CharField(
        required=True,
        help_text="IDNP or IDNO",
        max_length=13,
        min_length=13,
    )
    VehicleRegistrationCertificateNumber = serializers.CharField(
        required=True,
        max_length=9,
        min_length=9,
        help_text="Vehicle Registration Certificate Number",
    )


class InsurerPrimeRCAESerializer(serializers.Serializer):
    Name = serializers.CharField(max_length=255)
    IDNO = serializers.CharField(max_length=13, min_length=13)
    PrimeSum = serializers.DecimalField(max_digits=20, decimal_places=2)
    PrimeSumMDL = serializers.DecimalField(max_digits=20, decimal_places=2)
    is_active = serializers.BooleanField(default=True)
    logo = serializers.URLField(
        allow_null=True,
        required=False,
        default="https://www.google.com/url?sa=i&url=https%3A%2F%2Fdataset.gov.md%2Fru%2Forganization%2F1015601000134&psig=AOvVaw0lWpKM2jNr6jxpf6d44FTo&ust=1736284024523000&source=images&cd=vfe&opi=89978449&ved=0CBQQjRxqFwoTCMDPkZyA4ooDFQAAAAAdAAAAABAE",
    )


class InsurerPrimeRCAISerializer(InsurerPrimeRCAESerializer):
    PrimeSumMDL = serializers.SerializerMethodField()

    @staticmethod
    def get_PrimeSumMDL(obj):  # noqa: N802
        return obj.get("PrimeSum")


class InsurersPrimeRCASerializer(serializers.Serializer):
    InsurerPrimeRCAI = InsurerPrimeRCAISerializer(many=True)


class InsurersPrimeGreenCardSerializer(serializers.Serializer):
    InsurerPrimeRCAE = InsurerPrimeRCAESerializer(many=True)


class CalculateRCAOutputSerializer(serializers.Serializer):
    InsurersPrime = InsurersPrimeRCASerializer()
    BonusMalusClass = serializers.IntegerField()
    IsSuccess = serializers.BooleanField()
    ErrorMessage = serializers.CharField(allow_null=True, required=False)
    Territory = serializers.CharField(max_length=100)
    PersonFirstName = serializers.CharField(max_length=100, required=False, default=None, allow_null=True)
    PersonLastName = serializers.CharField(max_length=100, required=False, default=None, allow_null=True)
    VehicleMark = serializers.CharField(max_length=100)
    VehicleModel = serializers.CharField(max_length=100)
    VehicleRegistrationNumber = serializers.CharField(max_length=20)


class CalculateGreenCardOutputSerializer(serializers.Serializer):
    InsurersPrime = InsurersPrimeGreenCardSerializer()
    IsSuccess = serializers.BooleanField()
    ErrorMessage = serializers.CharField(allow_null=True, allow_blank=True)
    PersonFirstName = serializers.CharField(allow_null=True, allow_blank=True)
    PersonLastName = serializers.CharField(allow_null=True, allow_blank=True)
    VehicleMark = serializers.CharField(allow_null=True, allow_blank=True)
    VehicleModel = serializers.CharField(allow_null=True, allow_blank=True)
    VehicleRegistrationNumber = serializers.CharField(allow_null=True, allow_blank=True)
    VehicleCategory = serializers.ChoiceField(
        allow_null=True, allow_blank=True, choices=GreenCardVehicleCategories.choices
    )


class CompanyModelSerializer(serializers.Serializer):
    IDNO = serializers.CharField(required=False, allow_blank=True)


class PhysicalPersonModelSerializer(serializers.Serializer):
    IdentificationCode = serializers.CharField()
    BirthDate = serializers.DateField(required=False, default="2000-01-01")
    IsFromTransnistria = serializers.BooleanField(default=False, required=False)
    PersonIsExternal = serializers.BooleanField(default=False, required=False)


class JuridicalPersonModelSerializer(serializers.Serializer):
    IdentificationCode = serializers.CharField()


class VehicleModelSerializer(serializers.Serializer):
    ProductionYear = serializers.IntegerField(required=False, default=2025)
    RegistrationCertificateNumber = serializers.CharField(required=True)
    CilinderVolume = serializers.IntegerField(required=False, default=2000)
    TotalWeight = serializers.IntegerField(required=False, default=2000)
    EnginePower = serializers.IntegerField(required=False, default=200)
    Seats = serializers.IntegerField(required=False, default=5)


class SaveRcaDocumentSerializer(serializers.Serializer):
    Company = CompanyModelSerializer()
    InsuredPhysicalPerson = PhysicalPersonModelSerializer(required=False)
    InsuredJuridicalPerson = JuridicalPersonModelSerializer(required=False)
    InsuredVehicle = VehicleModelSerializer()
    StartDate = serializers.DateField()
    PossessionBase = serializers.ChoiceField(
        choices=PossessionBase.choices, default=PossessionBase.PROPERTY, required=False
    )
    DocumentPossessionBaseDate = serializers.DateField(required=False, default="2000-01-01")
    OperatingModes = serializers.ChoiceField(choices=OperationModes.choices, default=OperationModes.USUAL)
    qrCode = serializers.SlugRelatedField(
        help_text="QR Code UUID",
        queryset=QrCode.objects.filter(status=StatusChoices.PAID, is_used=False),
        slug_field="uuid",
    )

    @staticmethod
    def validate_StartDate(value):  # noqa: N802X
        if value < value.today():
            raise serializers.ValidationError("StartDate must be in the future")
        return value


class GreenCardDocumentModelSerializer(serializers.Serializer):
    Company = CompanyModelSerializer(required=False)
    InsuredPhysicalPerson = PhysicalPersonModelSerializer(required=False)
    InsuredJuridicalPerson = JuridicalPersonModelSerializer(required=False)
    InsuredVehicle = VehicleModelSerializer()
    StartDate = serializers.DateField()
    TermInsurance = serializers.ChoiceField(choices=TermInsurance.choices)
    PossessionBase = serializers.ChoiceField(choices=PossessionBase.choices)
    DocumentPossessionBaseDate = serializers.DateTimeField(allow_null=True)
    GreenCardZone = serializers.ChoiceField(choices=GreenCardZones.choices)
    qrCode = serializers.SlugRelatedField(
        required=True,
        allow_null=False,
        help_text="QR Code UUID",
        queryset=QrCode.objects.filter(status=StatusChoices.PAID, is_used=False),
        slug_field="uuid",
    )

    @staticmethod
    def validate_StartDate(value):  # noqa: N802
        if value < value.today():
            raise serializers.ValidationError("StartDate must be in the future")
        return value


class GetFileRequestSerializer(serializers.Serializer):
    DocumentType = serializers.ChoiceField(choices=DocumentType.choices, required=False, default=DocumentType.CONTRACT)
    ContractType = serializers.ChoiceField(choices=ContractType.choices, required=False, default=ContractType.RCAI)


class SendFileRequestSerializer(serializers.Serializer):
    DocumentType = serializers.ChoiceField(choices=DocumentType.choices, required=False, default=DocumentType.CONTRACT)
    ContractType = serializers.ChoiceField(choices=ContractType.choices, required=False, default=ContractType.RCAI)
    email = serializers.EmailField(required=True)
