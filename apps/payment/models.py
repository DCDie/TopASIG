import uuid as uuid_lib

from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.payment.constants import AmountTypeChoices, PmtContextChoices, QrTypeChoices, StatusChoices


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

    def __str__(self):
        return f"QR Code {self.uuid} - {self.status}"

    class Meta:
        verbose_name = _("QR Code")
        verbose_name_plural = _("QR Codes")
