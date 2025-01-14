from django.db import connection
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response

from apps.ensurance.rca import RcaExportServiceClient


class HealthCheckView(GenericAPIView):
    """
    View for performing health checks on the application.

    This class provides functionality to check the overall health of the application, including
    database connectivity and service dependencies like RCA. It handles a GET request to return
    a detailed status report of various application components. This view does not require
    authentication or permissions to access.

    Attributes:
    authentication_classes (list): A list of authentication classes; empty indicating no
    authentication.
    permission_classes (list): A list of permission classes; empty indicating no
    authorization.

    """

    authentication_classes = []
    permission_classes = []
    serializer_class = None

    @staticmethod
    def get(request):
        data = {
            "status": "ok",
        }

        # Check db connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            row = cursor.fetchone()
            if row is None:
                data["db"] = "error"
            else:
                data["db"] = "ok"
        # Check RCA service
        try:
            RcaExportServiceClient().check_access()
            data["rca"] = "ok"
        except Exception:  # noqa BLE001
            data["rca"] = "error"

        return Response(data)
