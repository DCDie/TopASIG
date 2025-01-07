import zeep
from django.conf import settings
from rest_framework.exceptions import APIException, ValidationError
from zeep import Client
from zeep.exceptions import TransportError
from zeep.transports import Transport

from apps.ensurance.constants import PaymentModes, TermInsurance


class RcaExportServiceClient:
    def __init__(self, wsdl_url=settings.RCA_URL):
        self.transport = Transport(timeout=30)
        self.client = Client(wsdl=wsdl_url, transport=self.transport)
        self.service = self.client.service
        self.security_token = None

    def authenticate(self, username: str = settings.RCA_USERNAME, password: str = settings.RCA_PASSWORD):
        """
        Authenticates a user by using provided credentials and retrieves a security token.

        This method initiates a user authentication process by calling the Authenticate
        operation in a specified service. The operation is supplied with a username
        and password, which are used to validate the user. Upon successful validation,
        a GUID is returned and stored as the session token.

        Parameters:
            username (str): The username for authentication. Defaults to settings.RCA_USERNAME.
            password (str): The password for authentication. Defaults to settings.RCA_PASSWORD.

        Returns:
            Any: The response from the Authenticate operation containing the authentication result.
        """

        author_type = self.client.get_type("ns0:AuthorizationInfo")
        author = author_type(UserName=username, UserPassword=password, SecurityToken=zeep.xsd.SkipValue)

        # Call the Authenticate operation
        response = self.service.Authenticate(author=author)

        # According to the WSDL, AuthenticateResult returns a GUID. We store it as our session token
        self.security_token = response.AuthenticateResult
        return response

    def check_access(self, login: str = settings.RCA_USERNAME, password: str = settings.RCA_PASSWORD):
        """
        Checks if the user has access by verifying the provided login credentials.

        This method communicates with an external service to validate the provided
        login and password combination. The result is returned as a response object
        from the service, indicating whether access is granted or denied.

        Args:
            login: str. The login credential for the user.
            password: str. The password credential for the user.

        Returns:
            The response object from the service indicating the result of the
            authentication process.

        """
        response = self.service.CheckAccess(login=login, password=password)
        return response

    def calculate_rca(self, request_obj: dict):
        """
        Calculates the RCA insurance premium based on the provided employee and
        request details. This method prepares the necessary request object using
        provided employee information and request parameters, authenticates the
        current session, and interacts with the API service to retrieve the RCA
        insurance premium.

        Parameters
        ----------
        request_obj : dict
            A dictionary containing parameters necessary for calculating RCA
            insurance premiums. The dictionary includes keys matching the
            request's expected input structure.

        Returns
        -------
        object
            The response object returned by the RCA insurance premium API
            service. Contains details of the calculation results.

        Raises
        ------
        APIException
            Raised when there is an error while interacting with the API service,
            providing details of the exception.
        ValidationError
            Raised if the response from the API service indicates failure,
            including an error message returned by the service.
        """
        Employee = self.client.get_type("ns0:EmployeeInput")(IDNP=settings.ASIG_IDNP)

        RequestType = self.client.get_type("ns0:CalculateRCAIPremiumRequest")
        request_obj = RequestType(
            Employee=Employee,
            **request_obj,
        )
        try:
            self.authenticate()
            response = self.service.CalculateRCAIPremium(SecurityToken=self.security_token, request=request_obj)
        except Exception as e:  # noqa: BLE001
            raise APIException(detail={"detail": str(e)}) from e
        if response.IsSuccess is False:
            raise ValidationError(detail={"detail": response.ErrorMessage})
        return response

    def calculate_green_card(self, request_obj: dict):
        """
        Calculates the green card premium based on the provided request object.

        The method interacts with a remote service, initializing required parameters
        from predefined client types. It handles authentication, performs the
        service call, and manages potential exceptions or errors during the
        communication process. On successful execution, returns the response
        object from the external service.

        Arguments:
            request_obj (dict): A dictionary containing parameters required
            for the service request.

        Raises:
            APIException: If any exception occurs during the external service call.
            ValidationError: If the response indicates an error or unsuccessful operation.

        Returns:
            Response object from the external service call.
        """
        Employee = self.client.get_type("ns0:EmployeeInput")(IDNP=settings.ASIG_IDNP)

        RequestType = self.client.get_type("ns0:CalculateRCAEPremiumRequest")
        request_obj = RequestType(
            Employee=Employee,
            **request_obj,
        )
        try:
            self.authenticate()
            response = self.service.CalculateRCAEPremium(SecurityToken=self.security_token, request=request_obj)
        except Exception as e:  # noqa: BLE001
            raise APIException(detail={"detail": str(e)}) from e
        if response.IsSuccess is False:
            raise ValidationError(detail={"detail": response.ErrorMessage})
        return response

    def save_greencard_document(self, document_request: dict, IDNP: str = settings.ASIG_IDNP):
        """
        Saves a green card document by sending a request to the corresponding service.

        This function is used to authenticate and send a green card document request to
        an external service. It first constructs the required request payload using the
        received input, authenticates with the service, and sends the data. The function
        handles errors such as those raised by the external service or issues during
        authentication. It ensures that the server response indicates a successful
        operation; otherwise, raises appropriate validation errors.

        Args:
            document_request (dict): A dictionary containing the details of the green
                card document to be saved. Must include required keys and values as
                expected by the external service API.
            IDNP (str): The unique personal identifier. Defaults to ASIG_IDNP from
                settings.

        Raises:
            APIException: Raised when an error occurs during communication with the
                external service.
            ValidationError: Raised when the service response indicates a failure,
                including explaining errors.

        Returns:
            Response object: A representation of the result of the save operation
                returned by the external service.
        """
        Employee = self.client.get_type("ns0:EmployeeInput")(IDNP=IDNP)
        RequestType = self.client.get_type("ns0:GreenCardDocumentModel")
        document_request["Employee"] = Employee
        document_request = RequestType(**document_request, PaymentMode=PaymentModes.TRANSFER)

        try:
            self.authenticate()
            response = self.service.SaveGreenCardDocument(SecurityToken=self.security_token, request=document_request)
        except Exception as e:  # noqa: BLE001
            raise APIException(detail={"detail": str(e)}) from e
        if response.Success is False:
            raise ValidationError(detail={"detail": response.Errors.string})
        return response

    def save_rca_document(self, document_request: dict, IDNP: str = settings.ASIG_IDNP) -> bytes:
        """
        Saves an RCA document to the external service using the provided document
        request details and optional IDNP.

        This method authenticates the client before attempting to save the document
        using the external service. It converts the input request into the appropriate
        type expected by the service, ensuring that the Employee data is included in
        the request payload.

        Raises `APIException` if an exception occurs during the process of
        authentication or saving the document.

        Raises `ValidationError` if the external service response indicates a failure.

        Parameters:
            document_request (dict): The dictionary containing document details that are
                to be sent to the external service.
            IDNP (str, optional): The unique identifier for an employee. Defaults to a
                predefined setting value.

        Returns:
            The response object from the external service containing the result of the
            save operation.
        """
        Employee = self.client.get_type("ns0:EmployeeInput")(IDNP=IDNP)
        RequestType = self.client.get_type("ns0:RcaDocumentModel")
        document_request["Employee"] = Employee
        document_request = RequestType(
            **document_request, TermInsurance=TermInsurance.M12, PaymentMode=PaymentModes.TRANSFER
        )

        try:
            self.authenticate()
            response = self.service.SaveRcaDocument(SecurityToken=self.security_token, request=document_request)
        except TransportError as e:
            if e.status_code == 200:
                return e.content
            raise APIException(detail={"detail": str(e)}) from e
        except Exception as e:  # noqa: BLE001
            raise APIException(detail={"detail": str(e)}) from e
        if response.Success is False:
            raise ValidationError(detail={"detail": response.Errors.string})
        return response

    def get_file(self, DocumentId: str, DocumentType: str = "InsurancePolicy", ContractType: str = "RCAI"):
        """
        Fetches a file based on provided document details.

        This method sends a request to retrieve a file using the supplied DocumentId,
        DocumentType, and ContractType. It constructs the necessary request object
        and communicates with the service to fetch the file.

        Parameters:
            DocumentId: str
                Unique identifier of the document to be retrieved.

        Returns:
            object
                The requested file object obtained from the service.
        """
        FileRequestType = self.client.get_type("ns0:GetFileRequest")
        file_request = FileRequestType(DocumentId=DocumentId, DocumentType=DocumentType, ContractType=ContractType)

        try:
            self.authenticate()
            response = self.service.GetFile(SecurityToken=self.security_token, fileRequest=file_request)
        except Exception as e:  # noqa: BLE001
            raise APIException(detail={"detail": str(e)}) from e
        if response.IsSuccess is False:
            raise ValidationError(detail={"detail": response.ErrorMessage})
        return response

    def get_rca_documents_list(self, start_date, end_date):
        """
        Calls GetRcaDocumentsList.

        start_date and end_date should be datetime or ISO string as required.
        """
        return self.service.GetRcaDocumentsList(
            SecurityToken=self.security_token, StartDate=start_date, EndDate=end_date
        )

    def get_rca_document_keys_list(self, start_date, end_date):
        """
        Calls GetRcaDocumentKeysList.
        """
        return self.service.GetRcaDocumentKeysList(
            SecurityToken=self.security_token, StartDate=start_date, EndDate=end_date
        )

    def get_rca_document_by_key(self, rca_document_id):
        """
        Calls GetRcaDocumentByKey.
        """
        return self.service.GetRcaDocumentByKey(SecurityToken=self.security_token, rcaDocumentId=rca_document_id)

    def get_greencard_documents_list(self, start_date, end_date):
        """
        Calls GetGreenCardDocumentsList.
        """
        return self.service.GetGreenCardDocumentsList(
            SecurityToken=self.security_token, StartDate=start_date, EndDate=end_date
        )

    def get_greencard_document_keys_list(self, start_date, end_date):
        """
        Calls GetGreenCardDocumentKeysList.
        """
        return self.service.GetGreenCardDocumentKeysList(
            SecurityToken=self.security_token, StartDate=start_date, EndDate=end_date
        )

    def get_greencard_document_by_key(self, green_card_id):
        """
        Calls GetGreenCardDocumentByKey.
        """
        return self.service.GetGreenCardDocumentByKey(SecurityToken=self.security_token, greenCardId=green_card_id)

    def get_rca_compensation_documents_list(self, start_date, end_date):
        """
        Calls GetRcaCompensationDocumentsList.
        """
        return self.service.GetRcaCompensationDocumentsList(
            SecurityToken=self.security_token, StartDate=start_date, EndDate=end_date
        )

    def get_rca_compensation_document_by_key(self, rca_compensation_id):
        """
        Calls GetRcaCompensationDocumentByKey.
        """
        return self.service.GetRcaCompensationDocumentByKey(
            SecurityToken=self.security_token, RcaCompensationId=rca_compensation_id
        )

    def get_greencard_compensation_documents_list(self, start_date, end_date):
        """
        Calls GetGreenCardCompensationDocumentsList.
        """
        return self.service.GetGreenCardCompensationDocumentsList(
            SecurityToken=self.security_token, StartDate=start_date, EndDate=end_date
        )

    def get_greencard_compensation_document_by_key(self, green_card_compensation_id):
        """
        Calls GetGreenCardCompensationDocumentByKey.
        """
        return self.service.GetGreenCardCompensationDocumentByKey(
            SecurityToken=self.security_token, GreenCardCompensationId=green_card_compensation_id
        )

    def save_rca_compensation(self, compensation_record):
        """
        Calls SaveRcaCompensation.

        compensation_record should be constructed as ns0:RcaCompensationRecordInput.
        """
        return self.service.SaveRcaCompensation(SecurityToken=self.security_token, record=compensation_record)

    def save_greencard_compensation(self, compensation_record):
        """
        Calls SaveGreenCardCompensation.

        compensation_record should be constructed as ns0:GreenCardCompensationRecordInput.
        """
        return self.service.SaveGreenCardCompensation(SecurityToken=self.security_token, record=compensation_record)

    def get_last_contract_expiration_date(self, request_obj):
        """
        Calls GetLastContractExpirationDate.

        request_obj should be ns0:LastContractExpirationDateRequest with required fields.
        """
        return self.service.GetLastContractExpirationDate(SecurityToken=self.security_token, request=request_obj)
