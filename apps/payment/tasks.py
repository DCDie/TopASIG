from celery import shared_task
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
        "not_changed": [],
    }

    for qr in queryset:
        qrcode_service = QrCodeService()
        try:
            with transaction.atomic():
                response_data = qrcode_service.get_qr_status(qr.uuid)
                # Update the status of the QR code in the database
                status = response_data.get("status")
                if status and status != qr.status:
                    qr.status = status
                    qr.save()
                    data["updated"].append(qr.pk)
                else:
                    data["not_changed"].append(qr.pk)
        except Exception:  # noqa BLE001
            data["failed"].append(qr.pk)

    return data
