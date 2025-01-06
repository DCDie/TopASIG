from celery import shared_task
from django.conf import settings
from django.db import transaction

from apps.payment.constants import StatusChoices
from apps.payment.models import QrCode
from apps.payment.qr import QrCodeService


@shared_task
def update_qr_status():
    queryset = QrCode.objects.filter(status=StatusChoices.ACTIVE)

    data = {
        "updated": [],
        "failed": [],
    }

    for qr in queryset:
        qrcode_service = QrCodeService()
        try:
            with transaction.atomic():
                response_data = qrcode_service.get_qr_status(qr.uuid)
                # Update the status of the QR code in the database
                qr.status = response_data.get("status")
                if settings.DEBUG:
                    qr.status = StatusChoices.PAID
                qr.save()
                data["updated"].append(qr.pk)
        except Exception:  # noqa BLE001
            data["failed"].append(qr.pk)

    return data
