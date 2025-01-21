from rest_framework import serializers

from apps.payment.constants import AmountTypeChoices, PmtContextChoices, QrTypeChoices, StatusChoices, UnitsChoices
from apps.payment.models import QrCode


class VbPayeeQrHeaderDtoSerializer(serializers.Serializer):
    qrType = serializers.ChoiceField(choices=QrTypeChoices.choices, default=QrTypeChoices.DYNAMIC, required=False)  # noqa: N815
    amountType = serializers.ChoiceField(
        choices=AmountTypeChoices.choices, default=AmountTypeChoices.FIXED, required=False
    )  # noqa: N815
    pmtContext = serializers.ChoiceField(
        choices=PmtContextChoices.choices, default=PmtContextChoices.MOBILE_PAYMENT, required=False
    )  # noqa: N815


class MoneyDtoSerializer(serializers.Serializer):
    sum = serializers.FloatField(min_value=0.01)
    currency = serializers.CharField(max_length=10, allow_blank=True, required=False, default="MDL")


class PayeeAccountDtoSerializer(serializers.Serializer):
    iban = serializers.CharField(max_length=34, allow_blank=True, required=False)


class TtlDtoSerializer(serializers.Serializer):
    length = serializers.IntegerField(default=5, min_value=1)
    units = serializers.ChoiceField(
        choices=UnitsChoices.choices, allow_blank=True, required=False, default=UnitsChoices.MM
    )


class VbPayeeQrExtensionDtoSerializer(serializers.Serializer):
    amount = MoneyDtoSerializer()


class VbPayeeQrDtoSerializer(serializers.Serializer):
    extension = VbPayeeQrExtensionDtoSerializer()


class CreatePayeeQrResponseSerializer(serializers.Serializer):
    qrHeaderUUID = serializers.UUIDField(required=False)  # noqa: N815
    qrExtensionUUID = serializers.UUIDField(required=False)  # noqa: N815
    qrAsText = serializers.URLField(required=False)  # noqa: N815
    qrAsImage = serializers.CharField(required=False)  # noqa: N815
    qrCode = serializers.IntegerField(required=False)


class QRCodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = QrCode
        fields = "__all__"


class PaymentDtoSerializer(serializers.Serializer):
    system = serializers.CharField(max_length=256, allow_blank=True, required=False)
    reference = serializers.CharField(max_length=256, allow_blank=True, required=False)
    amount = MoneyDtoSerializer()


class VbPayeeQrExtensionResponseSerializer(serializers.Serializer):
    uuid = serializers.UUIDField()
    isLast = serializers.BooleanField()  # noqa: N815
    status = serializers.ChoiceField(choices=StatusChoices.choices)
    statusDtTm = serializers.DateTimeField(format="%Y-%m-%dT%H:%M:%S.%fZ")  # noqa: N815
    isHeaderLocked = serializers.BooleanField()  # noqa: N815
    ttl = TtlDtoSerializer()
    payments = PaymentDtoSerializer()


class GetQrStatusResponseSerializer(serializers.Serializer):
    uuid = serializers.UUIDField()
    status = serializers.ChoiceField(choices=StatusChoices.choices)
    statusDtTm = serializers.DateTimeField(format="%Y-%m-%dT%H:%M:%S.%fZ")  # noqa: N815
    lockTtl = TtlDtoSerializer()  # noqa: N815
    extensions = VbPayeeQrExtensionResponseSerializer(many=True)


class SizeSerializer(serializers.Serializer):
    width = serializers.IntegerField(min_value=0, default=300)
    height = serializers.IntegerField(min_value=0, default=300)
