from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.payment.views import QrCodeViewSet

router = DefaultRouter()
router.register(r"qr", QrCodeViewSet, basename="qr-code")

urlpatterns = [
    path("", include(router.urls)),
]
