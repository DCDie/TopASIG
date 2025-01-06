import uuid

from django.db import models

from apps.payment.constants import AmountTypeChoices, PmtContextChoices, QrTypeChoices, StatusChoices


class QrCode(models.Model):
    """
    Model representing a Payee-presented QR Code.
    """

    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, help_text="UUID of the QR Code")
    qr_type = models.CharField(
        max_length=4, choices=QrTypeChoices.choices, default=QrTypeChoices.DYNAMIC, help_text="Type of the QR Code"
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
    qr_as_text = models.TextField(blank=True, null=True, help_text="QR code represented as text")
    qr_as_image = models.TextField(blank=True, null=True, help_text="QR code represented as an image")
    status = models.CharField(
        max_length=10,
        choices=StatusChoices.choices,
        default=StatusChoices.ACTIVE,
        help_text="Current status of the QR Code",
        db_index=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"QR Code {self.uuid} - {self.status}"
