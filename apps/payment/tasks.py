from datetime import timedelta

from celery import shared_task
from django.conf import settings
from django.db import transaction
from django.utils import timezone

from apps.payment.constants import MaibPaymentStatus, StatusChoices
from apps.payment.maib_ecommerce import MaibEcommerceService
from apps.payment.mia_maib import MaibQrCodeService
from apps.payment.models import MaibPayment, QrCode


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


@shared_task
def update_qr_status_if_debug(qr: str):
    if settings.DEBUG:
        QrCode.objects.filter(status=StatusChoices.ACTIVE, uuid=qr).update(status=StatusChoices.PAID)


@shared_task
def check_payment_status(pay_id):
    """
    Checks the status of a MAIB payment and updates it in the database.

    Args:
        pay_id (str): The MAIB payment ID to check
    """
    try:
        payment = MaibPayment.objects.get(pay_id=pay_id)

        # Skip if payment is already in final state
        if payment.status in [MaibPaymentStatus.SUCCESS, MaibPaymentStatus.FAILED]:
            return

        # Initialize MAIB E-commerce service
        maib_service = MaibEcommerceService()

        # Get payment status from MAIB
        response = maib_service.get_payment_status(pay_id)

        if not response.get("ok"):
            return

        result = response["result"]

        # Update payment status
        payment.status = (
            MaibPaymentStatus.SUCCESS if result["status"] == MaibPaymentStatus.SUCCESS else MaibPaymentStatus.FAILED
        )

        # Update payment data
        payment.data.update(
            {
                "status_code": result["statusCode"],
                "status_message": result["statusMessage"],
                "three_ds": result.get("threeDs"),
                "rrn": result.get("rrn"),
                "approval": result.get("approval"),
                "card_number": result.get("cardNumber"),
                "last_check": timezone.now().isoformat(),
            }
        )

        payment.save()

    except MaibPayment.DoesNotExist:
        pass
