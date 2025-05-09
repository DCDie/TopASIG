from rest_framework import serializers

from apps.payment.constants import AmountTypeChoices, PmtContextChoices, QrTypeChoices, StatusChoices, UnitsChoices
from apps.payment.models import MaibPayment, QrCode


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
    data = serializers.JSONField(required=False, default=dict)


class CreatePayeeQrResponseSerializer(serializers.Serializer):
    qrHeaderUUID = serializers.UUIDField(required=False)  # noqa: N815
    qrExtensionUUID = serializers.UUIDField(required=False)  # noqa: N815
    qrAsText = serializers.URLField(required=False)  # noqa: N815
    qrAsImage = serializers.CharField(required=False)  # noqa: N815
    qrCode = serializers.IntegerField(required=False)


class QrCodeSerializer(serializers.ModelSerializer):
    qr_as_image = serializers.URLField(required=False, source="file.file.url")

    class Meta:
        model = QrCode
        fields = [
            "uuid",
            "order_id",
            "type",
            "amount_type",
            "pmt_context",
            "url",
            "status",
            "is_used",
            "created_at",
            "updated_at",
            "file",
            "data",
            "qr_as_image",
        ]
        read_only_fields = ["uuid", "order_id", "url", "status", "is_used", "created_at", "updated_at", "qr_as_image"]


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


class MaibPaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = MaibPayment
        fields = [
            "id",
            "pay_id",
            "amount",
            "currency",
            "status",
            "client_name",
            "client_email",
            "client_phone",
            "description",
            "payment_url",
            "created_at",
            "updated_at",
            "data",
        ]
        read_only_fields = ["id", "pay_id", "status", "payment_url", "created_at", "updated_at"]


class MaibPaymentItemSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=124)
    quantity = serializers.IntegerField(min_value=1)
    price = serializers.DecimalField(
        max_digits=10, decimal_places=2, min_value=0.01, required=True, coerce_to_string=True
    )


class MaibPaymentCreateSerializer(serializers.Serializer):
    amount = serializers.DecimalField(
        max_digits=10, decimal_places=2, min_value=0.01, required=True, coerce_to_string=True
    )
    description = serializers.CharField(max_length=124, required=False, allow_null=True)
    items = serializers.ListField(child=MaibPaymentItemSerializer(), required=True, allow_null=False)
