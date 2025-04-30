from datetime import datetime

from rest_framework import serializers

from apps.ensurance.constants import (
    ContractType,
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
        default="https://i.pinimg.com/736x/ab/3d/e2/ab3de2f5cc08f507f728f39c66e596b8.jpg",
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
    ContractType = serializers.ChoiceField(choices=ContractType.choices, required=False, default=ContractType.RCAI)


class SendFileRequestSerializer(serializers.Serializer):
    ContractType = serializers.ChoiceField(choices=ContractType.choices, required=False, default=ContractType.RCAI)
    email = serializers.EmailField(required=True)


class DateStringField(serializers.DateField):
    """
    A custom DateField that:
      1. Expects a string date from the request (like "2025.03.07")
      2. Parses it to a Python date object internally
      3. Returns a string in the desired format in validated_data
    """

    def to_internal_value(self, data):
        # Let the default `DateField` parsing happen first:
        date_obj = super().to_internal_value(data)
        # Now convert that date object to a string in the desired format:
        return date_obj.strftime("%Y.%m.%d")


class PersonSerializer(serializers.Serializer):
    idnp = serializers.CharField(max_length=13)
    fullName = serializers.CharField(max_length=255)
    birthday = DateStringField()


class DogMEDPHSerializer(serializers.Serializer):
    UIN_Dokumenta = serializers.CharField(max_length=255, allow_blank=True, read_only=True)
    valiuta_ = serializers.CharField(max_length=3, required=False, default="840")
    data = DateStringField()
    startDate = DateStringField()
    endDate = DateStringField()
    ProductUIN = serializers.CharField(max_length=255)
    RegiuniUIN = serializers.CharField(max_length=255)
    ScopulCalatorieiUIN = serializers.CharField(max_length=255)
    TaraUIN = serializers.CharField(max_length=255)
    TipSportUIN = serializers.CharField(max_length=255, allow_blank=True)
    SARS_COV19 = serializers.BooleanField(required=False, default=True)
    # ZileDeAcoperire = serializers.IntegerField()
    SumaDeAsig = serializers.IntegerField(required=False, default=30000)
    # MesiatsevPeriodaStrahovania = serializers.IntegerField()
    persons = PersonSerializer(many=True)

    def to_internal_value(self, data):
        data = super().to_internal_value(data)
        # calculate from startDate and endDate
        start = (
            datetime.strptime(data["startDate"], "%Y.%m.%d")
            if isinstance(data["startDate"], str)
            else data["startDate"]
        )
        end = datetime.strptime(data["endDate"], "%Y.%m.%d") if isinstance(data["endDate"], str) else data["endDate"]
        data["ZileDeAcoperire"] = (start - end).days or 1
        data["MesiatsevPeriodaStrahovania"] = (start.month - end.month) + 1
        return data


class DotDateField(serializers.DateField):
    def to_internal_value(self, value):
        try:
            return datetime.strptime(value, "%Y.%m.%d").date()
        except ValueError as e:
            raise serializers.ValidationError("Date format must be YYYY.MM.DD") from e


class PersonReturnSerializer(PersonSerializer):
    birthday = DotDateField()
    PrimaVAL = serializers.FloatField(read_only=True)


class DogMEDPHReturnSerializer(DogMEDPHSerializer):
    IDNO = serializers.CharField(max_length=13)
    Name = serializers.CharField(max_length=255)
    is_active = serializers.BooleanField(default=True)
    logo = serializers.URLField(
        allow_null=True,
        required=False,
        default="https://i.pinimg.com/736x/ab/3d/e2/ab3de2f5cc08f507f728f39c66e596b8.jpg",
    )
    data = DotDateField()
    startDate = DotDateField()
    endDate = DotDateField()
    persons = PersonReturnSerializer(many=True)
    PrimaTotalaVAL = serializers.FloatField(read_only=True)
    PrimaTotalaLEI = serializers.FloatField(read_only=True)


class RootSerializer(serializers.Serializer):
    DogMEDPH = DogMEDPHSerializer(many=True)


class RootReturnSerializer(serializers.Serializer):
    DogMEDPH = DogMEDPHReturnSerializer(many=True)
