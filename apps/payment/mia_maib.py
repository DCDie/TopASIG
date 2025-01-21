from datetime import datetime, timedelta

import requests
from django.conf import settings
from rest_framework.exceptions import AuthenticationFailed

from apps.payment.constants import AmountTypeChoices, QrTypeChoices


class MaibQrCodeService:
    """
    Handles the communication with the MAIB QR code service.

    This service is designed to interact with the MAIB API to authenticate, create QR codes,
    and fetch QR code statuses. The class facilitates functionalities such as token-based
    authentication and prepares all necessary request headers for secure API interaction.

    :ivar base_url: The base URL for the MAIB API.
    :type base_url: str
    :ivar clientId: Client ID for authentication with the API.
    :type clientId: str
    :ivar clientSecret: Client secret for authentication with the API.
    :type clientSecret: str
    :ivar domain: Domain of the application for callback and redirect URIs.
    :type domain: str
    :ivar token: Bearer token for authenticated API calls.
    :type token: Optional[str]
    :ivar token_expires_at: The UTC time when the current token expires.
    :type token_expires_at: datetime
    """

    def __init__(self):
        self.base_url = settings.MAIB_MIA_BASE_URL.rstrip("/")
        self.clientId = settings.MAIB_CLIENT_ID
        self.clientSecret = settings.MAIB_CLIENT_SECRET
        self.domain = settings.DOMAIN
        self.token = None
        self.token_expires_at = datetime.utcnow()

    def authenticate(self):
        """
        Authenticates the client with the API using the provided credentials. This
        method sends a POST request to the authentication endpoint, retrieves, and
        stores the access token and its expiration time. If the authentication fails,
        an exception will be raised.

        :raises AuthenticationFailed: If there is an issue during the API authentication
            process.

        """
        url = f"{self.base_url}/auth/token"
        payload = {
            "clientId": self.clientId,
            "clientSecret": self.clientSecret,
        }
        try:
            response = requests.post(url, json=payload)
            response.raise_for_status()
            data = response.json()
            self.token = data["result"].get("accessToken")
            expires_in = data["result"].get("expiresIn", 3600)  # Default to 1 hour
            self.token_expires_at = datetime.utcnow() + timedelta(seconds=expires_in - 60)
        except requests.exceptions.RequestException as e:
            raise AuthenticationFailed(f"Failed to authenticate with API: {e}") from e

    def get_headers(self):
        """
        Generates and retrieves the HTTP headers required for making authenticated requests.

        If the token is expired or missing, the method automatically initiates a new
        authentication process to update the token before constructing the headers.

        :return: A dictionary containing the HTTP headers, with the `Authorization`
            field set to the current token and `Content-Type` set to `application/json`.
        :rtype: dict
        """
        if not self.token or datetime.utcnow() >= self.token_expires_at:
            self.authenticate()
        return {"Authorization": f"Bearer {self.token}"}

    def create_qr_code(self, vb_payee_qr_dto, **kwargs):
        """
        Generate a new QR code for payment requests by creating a dynamic QR code. The method
        accepts details about the payment, including amount, currency, expiration date, and
        additional information to format the QR code request. It handles API interaction with
        the necessary headers and endpoint setup for achieving the functionality.

        :param vb_payee_qr_dto: A dictionary containing payment details including amount,
                                currency, expiration date, description, and other required
                                data for QR code creation.
        :type vb_payee_qr_dto: dict
        :param kwargs: Additional parameters to customize or enhance the request.
        :type kwargs: dict
        :return: The response of the QR code creation API, typically includes details of the
                 generated QR code.
        :rtype: dict
        """
        url = f"{self.base_url}/mia/qr"
        headers = self.get_headers()

        # Prepare the request data
        request_data = {
            "type": QrTypeChoices.DYNAMIC,
            "amountType": AmountTypeChoices.FIXED,
            "amount": vb_payee_qr_dto["extension"]["amount"]["sum"],
            "currency": vb_payee_qr_dto["extension"]["amount"]["currency"],
            "expiresAt": (datetime.utcnow() + timedelta(days=1)).isoformat(),
            "order_id": vb_payee_qr_dto["order_id"],
            "description": "Payment for services on www.topasig.md",
            "redirectUrl": f"{self.domain}/payment/success",
            "callbackUrl": f"{self.domain}/payment/callback",
        }

        response = requests.post(url, json=request_data, headers=headers)
        response.raise_for_status()
        return response.json()

    def get_qr_status(self, qr_header_uuid):
        """
        Retrieves the status of a QR code using its unique identifier.

        This method constructs a URL with the given `qr_header_uuid`,
        adds any necessary headers using the `get_headers` method, and
        sends an HTTP GET request to retrieve the QR status. If the request
        is unsuccessful, this method will raise an HTTP error. On success,
        it returns the JSON response containing the QR status.

        :param qr_header_uuid: The unique identifier of the QR code header.
        :type qr_header_uuid: str
        :return: JSON response containing the status of the QR code.
        :rtype: dict
        :raises HTTPError: If the request to the QR status endpoint fails.
        """
        url = f"{self.base_url}/mia/qr/{qr_header_uuid}"
        response = requests.get(url, headers=self.get_headers())
        response.raise_for_status()
        return response.json()
