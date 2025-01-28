from datetime import timedelta

from celery import shared_task
from django.db import transaction
from django.utils import timezone

from apps.payment.constants import StatusChoices
from apps.payment.mia_maib import MaibQrCodeService
from apps.payment.models import QrCode


@shared_task
def update_qr_status():
    queryset = QrCode.objects.filter(status=StatusChoices.ACTIVE)

    data = {
        "updated": [],
        "failed": [],
        "not_changed": [],
    }

    for qr in queryset:
        qrcode_service = MaibQrCodeService()
        try:
            with transaction.atomic():
                response_data = qrcode_service.get_qr_status(str(qr.uuid))
                # Update the status of the QR code in the database
                status = response_data["result"].get("status")
                if status and status != qr.status:
                    qr.status = status
                    qr.save()
                    data["updated"].append(qr.pk)
                elif qr.created_at + timedelta(minutes=15) < timezone.now():
                    qr.status = StatusChoices.EXPIRED
                    qr.save()
                    data["updated"].append(qr.pk)
                else:
                    data["not_changed"].append(qr.pk)
        except Exception:  # noqa BLE001
            data["failed"].append(qr.pk)
            if qr.created_at + timedelta(minutes=15) < timezone.now():
                qr.status = StatusChoices.EXPIRED
                qr.save()
                data["updated"].append(qr.pk)

    return data
