from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.payment.views import MaibPaymentViewSet, QrCodeViewSet

router = DefaultRouter()
router.register(r"qr", QrCodeViewSet, basename="qr-code")
router.register(r"maib", MaibPaymentViewSet, basename="maib-payment")

urlpatterns = [path("", include(router.urls))]
