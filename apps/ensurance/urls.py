from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.ensurance.views import MedicalInsuranceViewSet, RcaViewSet

router = DefaultRouter()
router.register(r"rca", RcaViewSet, basename="rca")
router.register(r"medical-insurance", MedicalInsuranceViewSet, basename="medical-insurance")

urlpatterns = [
    path("", include(router.urls)),
]
