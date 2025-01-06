from datetime import datetime, timedelta

import requests
from django.conf import settings
from rest_framework.exceptions import AuthenticationFailed, ValidationError


class QrCodeService:
    """
    Manages interactions with the Victoria API for creating, managing, and retrieving information
    on payee-presented QR codes.

    This class provides methods for authenticating with the API, generating and managing
    QR codes, as well as retrieving their statuses. It handles authentication token management
    and automatically refreshes the token if it has expired.

    :ivar base_url: Base URL of the Victoria API.
    :type base_url: str
    :ivar username: Username for API authentication.
    :type username: str
    :ivar password: Password for API authentication.
    :type password: str
    :ivar domain: Domain used for authentication requests.
    :type domain: str
    :ivar token: JWT token used for authenticated requests.
    :type token: Optional[str]
    :ivar token_expires_at: Datetime when the current token will expire.
    :type token_expires_at: datetime
    """

    def __init__(self):
        self.base_url = settings.VICTORIA_BASE_URL.rstrip("/")
        self.username = settings.VICTORIA_USERNAME
        self.password = settings.VICTORIA_PASSWORD
        self.domain = settings.DOMAIN
        self.token = None
        self.token_expires_at = datetime.utcnow()

    def authenticate(self):
        """
        Authenticate with the API to obtain a JWT token.
        """
        url = f"{self.base_url}/identity/token"
        payload = {
            "grant_type": "password",
            "username": self.username,
            "password": self.password,
        }
        try:
            response = requests.post(url, data=payload)
            response.raise_for_status()
            data = response.json()
            self.token = data.get("accessToken")
            expires_in = data.get("expiresIn", 3600)  # Default to 1 hour
            self.token_expires_at = datetime.utcnow() + timedelta(seconds=expires_in)
        except requests.exceptions.RequestException as e:
            raise AuthenticationFailed(f"Failed to authenticate with API: {e}") from e

    def get_headers(self):
        """
        Get the headers required for API requests, including the Authorization header.
        """
        if not self.token or datetime.utcnow() >= self.token_expires_at:
            self.authenticate()
        return {"Authorization": f"Bearer {self.token}", "Content-Type": "application/json"}

    def create_qr_code(self, vb_payee_qr_dto, width=300, height=300):
        """
        Create a new payee-presented QR code.

        :param vb_payee_qr_dto: Dict representing VbPayeeQrDto schema
        :param width: Width of the QR code in pixels
        :param height: Height of the QR code in pixels
        :return: Dict representing CreatePayeeQrResponse
        """
        url = f"{self.base_url}/api/v1/qr"
        headers = self.get_headers()
        try:
            response = requests.post(
                url, json=vb_payee_qr_dto, headers=headers, params={"width": width, "height": height}
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise ValidationError(f"Failed to create QR code: {e}") from e

    def cancel_qr_code(self, qr_header_uuid):
        """
        Cancel an existing QR code.

        :param qr_header_uuid: UUID of the QR header
        :return: HTTP status code
        """
        url = f"{self.base_url}/api/v1/qr/{qr_header_uuid}"
        headers = self.get_headers()
        try:
            response = requests.delete(url, headers=headers)
            response.raise_for_status()
            return response.status_code
        except requests.exceptions.RequestException as e:
            raise ValidationError(f"Failed to cancel QR code: {e}") from e

    def get_qr_status(self, qr_header_uuid, nb_of_ext=5, nb_of_txs=10):
        """
        Retrieve the status of a QR code.

        :param qr_header_uuid: UUID of the QR header
        :param nb_of_ext: Number of extensions to retrieve
        :param nb_of_txs: Number of transactions per extension
        :return: Dict representing PayeeQrStatusDto
        """
        url = f"{self.base_url}/api/v1/qr/{qr_header_uuid}/status"
        headers = self.get_headers()
        params = {"nbOfExt": nb_of_ext, "nbOfTxs": nb_of_txs}
        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise ValidationError(f"Failed to get QR status: {e}") from e
