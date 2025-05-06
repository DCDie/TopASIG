from datetime import datetime, timedelta

import requests
from django.conf import settings
from rest_framework.exceptions import AuthenticationFailed


class MaibEcommerceService:
    """
    Handles the communication with the MAIB E-commerce service.

    This service is designed to interact with the MAIB E-commerce API to authenticate,
    create payments, and handle payment callbacks. The class facilitates functionalities
    such as token-based authentication and prepares all necessary request headers for
    secure API interaction.
    """

    def __init__(self):
        self.base_url = "https://api.maibmerchants.md/v1"
        self.project_id = settings.MAIB_PROJECT_ID
        self.project_secret = settings.MAIB_PROJECT_SECRET
        self.domain = settings.DOMAIN
        self.token = None
        self.token_expires_at = datetime.utcnow()
        self.refresh_token = None
        self.refresh_token_expires_at = datetime.utcnow()

    def authenticate(self):
        """
        Authenticates with the MAIB E-commerce API using project credentials.

        :raises AuthenticationFailed: If there is an issue during the API authentication process.
        """
        url = f"{self.base_url}/generate-token"
        payload = {
            "projectId": self.project_id,
            "projectSecret": self.project_secret,
        }
        try:
            response = requests.post(url, json=payload)
            response.raise_for_status()
            data = response.json()

            if not data.get("ok"):
                raise AuthenticationFailed("Failed to authenticate with MAIB E-commerce API")

            result = data["result"]
            self.token = result["accessToken"]
            self.refresh_token = result["refreshToken"]

            # Set expiration times with 60-second buffer
            self.token_expires_at = datetime.utcnow() + timedelta(seconds=result["expiresIn"] - 60)
            self.refresh_token_expires_at = datetime.utcnow() + timedelta(seconds=result["refreshExpiresIn"] - 60)

        except requests.exceptions.RequestException as e:
            raise AuthenticationFailed(f"Failed to authenticate with API: {e}") from e

    def refresh_access_token(self):
        """
        Refreshes the access token using the refresh token.

        :raises AuthenticationFailed: If there is an issue during token refresh.
        """
        if not self.refresh_token or datetime.utcnow() >= self.refresh_token_expires_at:
            self.authenticate()
            return

        url = f"{self.base_url}/refresh-token"
        payload = {"refreshToken": self.refresh_token}
        try:
            response = requests.post(url, json=payload)
            response.raise_for_status()
            data = response.json()

            if not data.get("ok"):
                raise AuthenticationFailed("Failed to refresh token with MAIB E-commerce API")

            result = data["result"]
            self.token = result["accessToken"]
            self.token_expires_at = datetime.utcnow() + timedelta(seconds=result["expiresIn"] - 60)

        except requests.exceptions.RequestException as e:
            raise AuthenticationFailed(f"Failed to refresh token: {e}") from e

    def get_headers(self):
        """
        Generates and retrieves the HTTP headers required for making authenticated requests.

        :return: A dictionary containing the HTTP headers.
        :rtype: dict
        """
        if not self.token or datetime.utcnow() >= self.token_expires_at:
            if datetime.utcnow() >= self.refresh_token_expires_at:
                self.authenticate()
            else:
                self.refresh_access_token()

        return {"Authorization": f"Bearer {self.token}", "Content-Type": "application/json"}

    def create_payment(self, payment_data):
        """
        Creates a new payment request.

        :param payment_data: Dictionary containing payment details
        :type payment_data: dict
        :return: Response from the payment creation API
        :rtype: dict
        :raises: requests.exceptions.RequestException if the request fails
        """
        url = f"{self.base_url}/pay"
        headers = self.get_headers()

        # Prepare the request data
        request_data = {
            "amount": payment_data["amount"],
            "currency": payment_data["currency"],
            "clientIp": payment_data["client_ip"],
            "language": payment_data.get("language", "en"),
            "description": payment_data.get("description", "Payment www.topasig.md"),
            "clientName": payment_data.get("client_name"),
            "email": payment_data.get("email"),
            "phone": payment_data.get("phone"),
            "orderId": str(payment_data["order_id"]),
            "delivery": payment_data.get("delivery"),
            "items": payment_data.get("items", []),
            "callbackUrl": f"{self.domain}/api/maib/callback",
            "okUrl": f"{self.domain}/api/maib/callback",
            "failUrl": f"{self.domain}/api/maib/callback",
        }

        response = requests.post(url, json=request_data, headers=headers)
        response.raise_for_status()
        return response.json()

    def get_payment_status(self, pay_id):
        """
        Retrieves the status of a payment using its unique identifier.

        :param pay_id: The unique identifier of the payment
        :type pay_id: str
        :return: JSON response containing the payment status
        :rtype: dict
        :raises: requests.exceptions.RequestException if the request fails
        """
        url = f"{self.base_url}/pay-info/{pay_id}"
        response = requests.get(url, headers=self.get_headers())
        response.raise_for_status()
        return response.json()
