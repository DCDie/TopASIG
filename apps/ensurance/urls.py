from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.ensurance.views import RcaViewSet

router = DefaultRouter()
router.register(r"rca", RcaViewSet, basename="rca")

urlpatterns = [
    path("", include(router.urls)),
]
