import binascii
import hashlib
import os
import time

import requests
from Crypto.Cipher import PKCS1_v1_5
from django.conf import settings


class ECommerceGatewayClient:
    def __init__(self, merchant_id=498000049807022, terminal_id=49807022, private_key=None, public_key=None):
        self.merchant_id = merchant_id
        self.terminal_id = terminal_id
        # self.private_key = RSA.importKey(private_key)
        # self.public_key = RSA.importKey(public_key)
        self.gateway_url = settings.VICTORIA_BASE_URL

    def generate_nonce(self):
        return binascii.hexlify(os.urandom(32)).decode("utf-8")

    def generate_timestamp(self):
        return time.strftime("%Y%m%d%H%M%S", time.gmtime())

    def generate_psign(self, fields):
        # Step 1: Construct the control string
        control_string = "".join(f"{len(str(value))}{value}" for value in fields.values())

        # Step 2: Hash the control string using MD5
        md5_hash = hashlib.md5(control_string.encode("utf-8")).hexdigest()

        # Step 3: Add the HEX ASN.1 prefix
        asn1_prefix = "003020300C06082A864886F70D020505000410"
        padded_hash = f"0001FF{'FF' * (self.private_key.size_in_bits() // 8 - len(asn1_prefix) - len(md5_hash) // 2 - 3)}{asn1_prefix}{md5_hash}"

        # Step 4: Convert to binary and encrypt with private RSA key
        binary_data = binascii.unhexlify(padded_hash)
        cipher = PKCS1_v1_5.new(self.private_key)
        encrypted_hash = cipher.encrypt(binary_data)

        # Step 5: Convert the encrypted data back to HEX
        return binascii.hexlify(encrypted_hash).decode("utf-8")

    def send_request(self, payload):
        response = requests.post(self.gateway_url, data=payload)
        return response.json()

    def process_response(self, response):
        psign = response.get("P_SIGN")
        fields = {key: response[key] for key in ["ACTION", "RC", "RRN", "ORDER", "AMOUNT"]}
        control_string = "".join(f"{len(str(value))}{value}" for value in fields.values())
        md5_hash = hashlib.md5(control_string.encode("utf-8")).hexdigest()

        cipher = PKCS1_v1_5.new(self.public_key)
        decrypted_psign = cipher.decrypt(binascii.unhexlify(psign), None)
        if md5_hash not in decrypted_psign.decode("utf-8"):
            raise ValueError("Invalid P_SIGN verification")
        return response

    def authorize_transaction(
        self, order="111111", amount=10.00, currency="MDL", description="TEST", backref_url="http://localhost:8000"
    ):
        timestamp = self.generate_timestamp()
        nonce = self.generate_nonce()
        fields = {
            "ORDER": order,
            "AMOUNT": amount,
            "CURRENCY": currency,
            "DESC": description,
            "MERCH_NAME": "Test Merchant",
            "MERCH_URL": "http://localhost:8000",
            "TRTYPE": 0,
            "TIMESTAMP": timestamp,
            "NONCE": nonce,
            "MERCHANT": self.merchant_id,
            "TERMINAL": self.terminal_id,
            "BACKREF": backref_url,
        }
        fields["P_SIGN"] = self.generate_psign(fields)
        return self.send_request(fields)
