from rest_framework import serializers


class VbPayeeQrHeaderDtoSerializer(serializers.Serializer):
    qrType = serializers.ChoiceField(choices=["DYNM", "STAT", "HYBR"])  # noqa: N815
    amountType = serializers.ChoiceField(choices=["Fixed", "Controlled", "Free"])  # noqa: N815
    pmtContext = serializers.ChoiceField(choices=["m", "e", "i", "0"], allow_blank=True, required=False)  # noqa: N815


class MoneyDtoSerializer(serializers.Serializer):
    sum = serializers.FloatField()
    currency = serializers.CharField(max_length=10, allow_blank=True, required=False)


class PayeeAccountDtoSerializer(serializers.Serializer):
    iban = serializers.CharField(max_length=34, allow_blank=True, required=False)


class TtlDtoSerializer(serializers.Serializer):
    length = serializers.IntegerField()
    units = serializers.ChoiceField(choices=["ss", "mm"], allow_blank=True, required=False)


class VbPayeeQrExtensionDtoSerializer(serializers.Serializer):
    creditorAccount = PayeeAccountDtoSerializer()  # noqa: N815
    amount = MoneyDtoSerializer()
    amountMin = MoneyDtoSerializer()  # noqa: N815
    amountMax = MoneyDtoSerializer()  # noqa: N815
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
    status = serializers.ChoiceField(choices=["Active", "Paid", "Expired", "Cancelled", "Replaced", "Inactive"])


class PaymentDtoSerializer(serializers.Serializer):
    system = serializers.CharField(max_length=256, allow_blank=True, required=False)
    reference = serializers.CharField(max_length=256, allow_blank=True, required=False)
    amount = MoneyDtoSerializer()


class VbPayeeQrExtensionResponseSerializer(serializers.Serializer):
    uuid = serializers.UUIDField()
    isLast = serializers.BooleanField()  # noqa: N815
    status = serializers.ChoiceField(choices=["Active", "Paid", "Expired", "Cancelled", "Replaced", "Inactive"])
    statusDtTm = serializers.DateTimeField(format="%Y-%m-%dT%H:%M:%S.%fZ")  # noqa: N815
    isHeaderLocked = serializers.BooleanField()  # noqa: N815
    ttl = TtlDtoSerializer()
    payments = PaymentDtoSerializer()


class GetQrStatusResponseSerializer(serializers.Serializer):
    uuid = serializers.UUIDField()  # noqa: N815
    status = serializers.ChoiceField(choices=["Active", "Paid", "Expired", "Cancelled", "Replaced", "Inactive"])
    statusDtTm = serializers.DateTimeField(format="%Y-%m-%dT%H:%M:%S.%fZ")  # noqa: N815
    lockTtl = TtlDtoSerializer()  # noqa: N815
    extensions = VbPayeeQrExtensionResponseSerializer(many=True)


class SizeSerializer(serializers.Serializer):
    width = serializers.IntegerField(min_value=0, default=300)
    height = serializers.IntegerField(min_value=0, default=300)
