import uuid
from base64 import b64decode

from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

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
    qr_as_image = models.TextField(blank=True, null=True, help_text="QR code represented as an image encoded in base64")
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

    def __str__(self):
        return f"QR Code {self.uuid} - {self.status}"


@receiver(post_save, sender=QrCode)
def qr_code_post_save(sender, instance, created, **kwargs):
    if created:
        from apps.ensurance.constants import FileTypes
        from apps.ensurance.models import File

        with SimpleUploadedFile(f"{instance.uuid}.png", b64decode(instance.qr_as_image)) as f:
            File.objects.create(
                external_id=str(instance.uuid),
                type=FileTypes.QR,
                file=f,
            )
