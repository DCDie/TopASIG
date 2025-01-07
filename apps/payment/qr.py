from datetime import datetime, timedelta

import requests
from django.conf import settings
from rest_framework.exceptions import AuthenticationFailed, ValidationError

from apps.payment.constants import UnitsChoices


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
        Authenticate the user by sending credentials to the API and retrieving an
        access token. The function sends a POST request with user credentials to
        fetch the token and its expiry details, then sets the token and expiration
        time attributes for subsequent API usage. If an error occurs during the
        request, an authentication failure exception is raised.

        Arguments:
            None

        Returns:
            None

        Raises:
            AuthenticationFailed: Raised when the authentication request to the API
            fails, encapsulating the underlying exception.

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
        Creates a QR code for a payee using provided details and API endpoint.

        This method interacts with an API endpoint to generate a payment QR code for
        a payee. The QR code is created based on the input data provided, including
        the desired width and height dimensions. It requires a DTO (data transfer
        object) specifying details about the payee, and it uses predefined configurations
        to adjust the content of the request. The method ensures secure communication
        with the API and handles potential exceptions during the network interaction.

        Parameters:
            vb_payee_qr_dto (dict): The data transfer object containing payee
                information and other required properties for generating the QR code.
            width (int): Desired width of the returned QR code. Defaults to 300.
            height (int): Desired height of the returned QR code. Defaults to 300.

        Raises:
            ValidationError: If the QR code generation fails due to a request exception.

        Returns:
            dict: The API response containing the generated QR code data.
        """
        url = f"{self.base_url}/api/v1/qr"
        headers = self.get_headers()
        vb_payee_qr_dto["extension"]["creditorAccount"] = {"iban": settings.ASIG_IBAN}
        vb_payee_qr_dto["extension"]["ttl"] = {"length": 15, "units": UnitsChoices.MM}
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
        Gets the QR status including extensions and transactions count.

        This method is used to retrieve the status of a QR header specified by
        its unique identifier. It fetches the data from the related API endpoint
        and includes two customizable parameters: the number of extensions and
        the number of transactions.

        Parameters:
            qr_header_uuid (str): Unique identifier for the QR header.
            nb_of_ext (int, optional): Number of extensions to include in the
                response, defaults to 5 if not provided.
            nb_of_txs (int, optional): Number of transactions to include in the
                response, defaults to 10 if not provided.

        Returns:
            dict: Parsed JSON response received from the server, which contains
            the required QR status information.

        Raises:
            ValidationError: If there is any issue with the API request, such as
                network errors, invalid responses, or server-side errors.
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
