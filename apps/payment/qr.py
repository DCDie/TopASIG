from datetime import datetime, timedelta

import requests
from django.conf import settings
from rest_framework.exceptions import AuthenticationFailed, ValidationError


class QrCodeService:
    """
    Service to interact with IPS Business WebApi for QR Code operations.
    """

    def __init__(self):
        self.base_url = settings.IPS_API_BASE_URL.rstrip("/")
        self.client_id = settings.IPS_API_CLIENT_ID
        self.client_secret = settings.IPS_API_CLIENT_SECRET
        self.token = None
        self.token_expires_at = datetime.utcnow()

    def authenticate(self):
        """
        Authenticate with the API to obtain a JWT token.
        """
        url = f"{self.base_url}/identity/adtoken"
        payload = {
            "grant_type": "password",
            "username": self.client_id,
            "password": self.client_secret,
        }
        try:
            response = requests.post(url, data=payload)
            response.raise_for_status()
            data = response.json()
            self.token = data.get("access_token")
            expires_in = data.get("expires_in", 3600)  # Default to 1 hour
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

    def create_qr_code(self, vb_payee_qr_dto):
        """
        Create a new payee-presented QR code.

        :param vb_payee_qr_dto: Dict representing VbPayeeQrDto schema
        :return: Dict representing CreatePayeeQrResponse
        """
        url = f"{self.base_url}/api/v1/qr"
        headers = self.get_headers()
        try:
            response = requests.post(url, json=vb_payee_qr_dto, headers=headers)
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
