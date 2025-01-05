from rest_framework import serializers

from apps.payment.constants import AmountTypeChoices, PmtContextChoices, QrTypeChoices, StatusChoices, UnitsChoices


class VbPayeeQrHeaderDtoSerializer(serializers.Serializer):
    qrType = serializers.ChoiceField(choices=QrTypeChoices.choices)  # noqa: N815
    amountType = serializers.ChoiceField(choices=AmountTypeChoices.choices)  # noqa: N815
    pmtContext = serializers.ChoiceField(choices=PmtContextChoices.choices, allow_blank=True, required=False)  # noqa: N815


class MoneyDtoSerializer(serializers.Serializer):
    sum = serializers.FloatField(min_value=0)
    currency = serializers.CharField(max_length=10, allow_blank=True, required=False, default="MDL")


class PayeeAccountDtoSerializer(serializers.Serializer):
    iban = serializers.CharField(max_length=34, allow_blank=True, required=False)


class TtlDtoSerializer(serializers.Serializer):
    length = serializers.IntegerField(default=5, min_value=1)
    units = serializers.ChoiceField(
        choices=UnitsChoices.choices, allow_blank=True, required=False, default=UnitsChoices.MM
    )


class VbPayeeQrExtensionDtoSerializer(serializers.Serializer):
    creditorAccount = PayeeAccountDtoSerializer()  # noqa: N815
    amount = MoneyDtoSerializer()
    amountMin = MoneyDtoSerializer(required=False)  # noqa: N815
    amountMax = MoneyDtoSerializer(required=False)  # noqa: N815x
    dba = serializers.CharField(max_length=25, min_length=2, allow_blank=True, required=False)
    remittanceInfo4Payer = serializers.CharField(max_length=35, min_length=2, allow_blank=True, required=False)  # noqa: N815
    creditorRef = serializers.CharField(max_length=35, min_length=2, allow_blank=True, required=False)  # noqa: N815
    ttl = TtlDtoSerializer()


class VbPayeeQrDtoSerializer(serializers.Serializer):
    header = VbPayeeQrHeaderDtoSerializer()
    extension = VbPayeeQrExtensionDtoSerializer()


class CreatePayeeQrResponseSerializer(serializers.Serializer):
    qrHeaderUUID = serializers.UUIDField(required=False)  # noqa: N815
    qrExtensionUUID = serializers.UUIDField(required=False)  # noqa: N815
    qrAsText = serializers.CharField(required=False)  # noqa: N815
    qrAsImage = serializers.CharField(required=False)  # noqa: N815
    status = serializers.ChoiceField(choices=StatusChoices.choices)


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
