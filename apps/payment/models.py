import uuid as uuid_lib

from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.payment.constants import AmountTypeChoices, MaibPaymentStatus, PmtContextChoices, QrTypeChoices, StatusChoices


class QrCode(models.Model):
    """
    Model representing a Payee-presented QR Code.
    """

    uuid = models.UUIDField(default=uuid_lib.uuid4, editable=False, unique=True, help_text="UUID of the QR Code")
    order_id = models.UUIDField(default=uuid_lib.uuid4, editable=False, help_text="UUID of the order", null=True)
    type = models.CharField(
        max_length=7, choices=QrTypeChoices.choices, default=QrTypeChoices.DYNAMIC, help_text="Type of the QR Code"
    )
    amount_type = models.CharField(
        max_length=10,
        choices=AmountTypeChoices.choices,
        default=AmountTypeChoices.FIXED,
        help_text="Type of the amount associated with the QR Code",
    )
    pmt_context = models.CharField(
        max_length=1, choices=PmtContextChoices.choices, blank=True, null=True, help_text="Payment context"
    )
    url = models.URLField(help_text="URL of the QR Code", blank=True, null=True)
    status = models.CharField(
        max_length=10,
        choices=StatusChoices.choices,
        default=StatusChoices.ACTIVE,
        help_text="Current status of the QR Code",
        db_index=True,
    )
    is_used = models.BooleanField(default=False, help_text="Whether the QR code has been used", db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    file = models.ForeignKey("ensurance.File", on_delete=models.SET_NULL, null=True, blank=True)
    data = models.JSONField(default=dict, help_text="Data associated with the QR Code")

    def __str__(self):
        return f"QR Code {self.uuid} - {self.status}"

    class Meta:
        verbose_name = _("QR Code")
        verbose_name_plural = _("QR Codes")


class MaibPayment(models.Model):
    """
    Model representing a MAIB E-commerce payment.
    """

    pay_id = models.CharField(max_length=36, unique=True, help_text="MAIB payment ID")
    amount = models.DecimalField(max_digits=10, decimal_places=2, help_text="Payment amount")
    currency = models.CharField(max_length=3, help_text="Payment currency", default="MDL")
    status = models.CharField(
        max_length=10,
        choices=MaibPaymentStatus.choices,
        default=MaibPaymentStatus.PENDING,
        help_text="Current status of the payment",
        db_index=True,
    )
    client_name = models.CharField(max_length=128, blank=True, null=True, help_text="Client name")
    client_email = models.EmailField(blank=True, null=True, help_text="Client email")
    client_phone = models.CharField(max_length=40, blank=True, null=True, help_text="Client phone")
    description = models.CharField(max_length=124, blank=True, null=True, help_text="Payment description")
    payment_url = models.URLField(help_text="URL for payment processing")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    data = models.JSONField(default=dict, help_text="Additional payment data")

    def __str__(self):
        return f"MAIB Payment {self.uuid} - {self.status}"

    class Meta:
        verbose_name = _("MAIB Payment")
        verbose_name_plural = _("MAIB Payments")
