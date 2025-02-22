from concurrent.futures import ThreadPoolExecutor, as_completed

import requests
from django.conf import settings


class MedicinaAPI:
    """
    Client for interacting with the "Миграция Медицина За Рубежом" API.

    This service provides several GET endpoints for справочники (directories)
    and POST endpoints for tariff calculation, contract creation, and obtaining
    printed forms.

    Example base URL:
        https://1c.donaris.md/donaris_web

    All API endpoints are under the path: /hs/medicina_peste_hotare/v1/
    """

    def __init__(self, base_url: str = settings.DONARIS_BASE_URL):
        """
        Initialize the API client.

        :param base_url: Base URL of the published database, e.g., "https://1c.donaris.md/donaris_web"
        """
        password = settings.DONARIS_PASSWORD
        login = settings.DONARIS_USERNAME
        self.base_url = base_url.rstrip("/")
        self.api_path = "/hs/medicina_peste_hotare/v1/"
        self.session = requests.Session()
        self.session.auth = (login, password)

    def _get(self, endpoint, params=None):
        """
        Helper method for GET requests.

        :param endpoint: API endpoint (e.g., "medicina_producti").
        :param params: (Optional) Dictionary of query parameters.
        :return: Parsed JSON response.
        :raises: requests.HTTPError if an error occurs.
        """
        url = self.base_url + self.api_path + endpoint.lstrip("/")
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return response.json()

    def _post(self, endpoint, json_data=None):
        """
        Helper method for POST requests.

        :param endpoint: API endpoint (e.g., "medicina_calcul_tarif").
        :param json_data: (Optional) Dictionary to send as JSON.
        :return: Parsed JSON response.
        :raises: requests.HTTPError if an error occurs.
        """
        url = self.base_url + self.api_path + endpoint.lstrip("/")
        response = self.session.post(url, json=json_data)
        response.raise_for_status()
        return response.json()

    # --- GET methods for справочники (directories) ---

    def get_medicina_producti(self):
        """
        Retrieve the "Медицина продукты" справочник.

        Endpoint: GET /medicina_producti
        """
        return self._get("medicina_producti")

    def get_medicina_tseli_poezdki(self):
        """
        Retrieve the "Медицина Цель Поездки" справочник.

        Endpoint: GET /medicina_tseli_poezdki
        """
        return self._get("medicina_tseli_poezdki")

    def get_medicina_regioni(self):
        """
        Retrieve the "Регионы" справочник.

        Endpoint: GET /medicina_regioni
        """
        return self._get("medicina_regioni")

    def get_spravociniki_strani(self):
        """
        Retrieve the "Страна клиента" справочник.

        Endpoint: GET /spravociniki_strani
        """
        return self._get("spravociniki_strani")

    def get_medicina_sport(self):
        """
        Retrieve the "Тип спорта" справочник.

        Endpoint: GET /medicina_sport
        """
        return self._get("medicina_sport")

    def get_medicina_straniUF(self):
        """
        Retrieve the "Страна для страхования" справочник.

        Endpoint: GET /medicina_straniUF
        """
        return self._get("medicina_straniUF")

    def get_spravociniki_goroda(self):
        """
        Retrieve the "Города" справочник.

        Endpoint: GET /spravociniki_goroda
        """
        return self._get("spravociniki_goroda")

    def get_regioni_i_strani(self):
        """
        Retrieve the "Справочник связки города с регионом" справочник.

        Endpoint: GET /regioni_i_strani
        """
        return self._get("regioni_i_strani")

    def get_all_directories(self):
        """
        Retrieve all справочники (directories) using threads for concurrent requests.

        :return: A dictionary with the following keys:
                 - medicina_producti
                 - medicina_tseli_poezdki
                 - medicina_regioni
                 - spravociniki_strani
                 - medicina_sport
                 - medicina_straniUF
                 - spravociniki_goroda
                 - regioni_i_strani
        """
        # Map keys to the corresponding method that retrieves the data
        endpoints = {
            "medicina_producti": self.get_medicina_producti,
            "medicina_tseli_poezdki": self.get_medicina_tseli_poezdki,
            "medicina_regioni": self.get_medicina_regioni,
            "spravociniki_strani": self.get_spravociniki_strani,
            "medicina_sport": self.get_medicina_sport,
            "medicina_straniUF": self.get_medicina_straniUF,
            "spravociniki_goroda": self.get_spravociniki_goroda,
            "regioni_i_strani": self.get_regioni_i_strani,
        }

        results = {}

        # Use a ThreadPoolExecutor to make concurrent GET calls
        with ThreadPoolExecutor(max_workers=len(endpoints)) as executor:
            future_to_key = {executor.submit(func): key for key, func in endpoints.items()}

            # As each future completes, store the result or handle exceptions
            for future in as_completed(future_to_key):
                key = future_to_key[future]
                try:
                    results[key] = future.result()
                except Exception:
                    # In case of error, you could log the error or set the result to None
                    # For example, results[key] = {"error": str(e)}
                    results[key] = None

        return results

    # --- POST methods for operations ---

    def calculate_tariff(self, tariff_data):
        """
        Calculate the tariff for a contract.

        Endpoint: POST /medicina_calcul_tarif

        The provided JSON should include parameters such as:
            - UIN_Dokumenta (as an empty string)
            - valiuta_
            - data, startDate, endDate
            - ProductUIN, RegiuniUIN, ScopulCalatorieiUIN,
              TaraUIN, TipSportUIN, SARS_COV19, ZileDeAcoperire,
              SumaDeAsig, MesiatsevPeriodaStrahovania, persons, etc.

        :param tariff_data: Dictionary with the tariff calculation data.
        :return: JSON response with tariff details.
        """
        return self._post("medicina_calcul_tarif", json_data=tariff_data)

    def create_contract(self, contract_data):
        """
        Create a new contract (полис).

        Endpoint: POST /medicina_sozdati_polis

        The JSON data should follow the example (Contract Standard.json) with proper
        parameters obtained from the справочники.

        :param contract_data: Dictionary with the contract data.
        :return: JSON response containing, for example, the created contract number.
        """
        return self._post("medicina_sozdati_polis", json_data=contract_data)

    def get_contract_info(self, uin_dokumenta):
        """
        Retrieve full information of a contract.

        Endpoint: GET /medicina_vsia_informatia_o_dogovore

        :param uin_dokumenta: The unique document identifier (UIN_Dokumenta).
        :return: JSON response with full contract information.
        """
        params = {"UIN_Dokumenta": uin_dokumenta}
        return self._get("medicina_vsia_informatia_o_dogovore", params=params)

    def get_print_forms(self, print_data):
        """
        Retrieve printed forms for a contract.

        Endpoint: POST /medicina_forme_printate

        The JSON should have a structure similar to:
            {
                "DogMEDPH": [
                    {
                        "UIN_Dokumenta": "<contract_uin>"
                    }
                ]
            }

        :param print_data: Dictionary with data required to obtain printed forms.
        :return: JSON response with printed form details.
        """
        return self._post("medicina_forme_printate", json_data=print_data)
