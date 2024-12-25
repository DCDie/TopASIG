import zeep
from django.conf import settings
from rest_framework.exceptions import APIException, ValidationError
from zeep import Client
from zeep.transports import Transport


class RcaExportServiceClient:
    def __init__(self, wsdl_url=settings.RCA_URL):
        self.transport = Transport(timeout=30)
        self.client = Client(wsdl=wsdl_url, transport=self.transport)
        self.service = self.client.service
        self.security_token = None

    def authenticate(self, username=settings.RCA_USERNAME, password=settings.RCA_PASSWORD):
        """
        Calls the Authenticate method with given credentials.

        Parameters:
            security_token (str): A GUID or some token as per the WSDL requirement.
            username (str): Username for the service (if required).
            password (str): Password for the service (if required).

        After calling this method, the class instance should store the security_token
        returned by the service (if any), for subsequent calls.
        """

        author_type = self.client.get_type("ns0:AuthorizationInfo")
        author = author_type(UserName=username, UserPassword=password, SecurityToken=zeep.xsd.SkipValue)

        # Call the Authenticate operation
        response = self.service.Authenticate(author=author)

        # According to the WSDL, AuthenticateResult returns a GUID. We store it as our session token
        self.security_token = response.AuthenticateResult
        return response

    def check_access(self, login, password):
        """
        Calls the CheckAccess method.

        Parameters:
            login (str)
            password (str)

        Returns the response from the service.
        """
        response = self.service.CheckAccess(login=login, password=password)
        return response

    def calculate_rca(
        self,
        OperatingModes: str,
        PersonIsJuridical: bool,
        Territory: str,
        IDNX: str,
        VehicleRegistrationCertificateNumber: str,
        IDNP: str = settings.ASIG_IDNP
    ):
        """
        Calls CalculateRCAIPremium. Calculates the RCA cost for a given set of input parameters.

        You may supply employee IDNP if needed. If so, construct Employee object.
        """
        Employee = self.client.get_type("ns0:EmployeeInput")(IDNP=IDNP)

        RequestType = self.client.get_type("ns0:CalculateRCAIPremiumRequest")
        request_obj = RequestType(
            Employee=Employee,
            OperatingModes=OperatingModes,
            PersonIsJuridical=PersonIsJuridical,
            IDNX=IDNX,
            VehicleRegistrationCertificateNumber=VehicleRegistrationCertificateNumber,
            Territory=Territory,
        )
        try:
            self.authenticate()
            response = self.service.CalculateRCAIPremium(SecurityToken=self.security_token, request=request_obj)
        except Exception as e:  # noqa: BLE001
            raise APIException(detail={"detail": str(e)}) from e
        if response.IsSuccess is False:
            raise ValidationError(detail={"detail": response.ErrorMessage})
        return response

    def calculate_green_card(
        self,
        GreenCardZone: str,
        TermInsurance: str,
        IDNX: str,
        VehicleRegistrationCertificateNumber: str,
        IDNP: str = settings.ASIG_IDNP,
    ):
        """
        Calls CalculateRCAEPremium. Calculates the Green Card cost for a given set of input parameters.

        Parameters:
            GreenCardZone (str): GreenCardZone enum value.
            TermInsurance (str): TermInsurance enum value.
            IDNX (str): IDNP or IDNO.
            VehicleRegistrationCertificateNumber (str): Vehicle Registration Certificate Number.
            IDNP (str): Employee IDNP.
        """
        Employee = self.client.get_type("ns0:EmployeeInput")(IDNP=IDNP)

        RequestType = self.client.get_type("ns0:CalculateRCAEPremiumRequest")
        request_obj = RequestType(
            Employee=Employee,
            GreenCardZone=GreenCardZone,
            IDNX=IDNX,
            VehicleRegistrationCertificateNumber=VehicleRegistrationCertificateNumber,
            TermInsurance=TermInsurance,
        )
        try:
            self.authenticate()
            response = self.service.CalculateRCAEPremium(SecurityToken=self.security_token, request=request_obj)
        except Exception as e:  # noqa: BLE001
            raise APIException(detail={"detail": str(e)}) from e
        if response.IsSuccess is False:
            raise ValidationError(detail={"detail": response.ErrorMessage})
        return response

    def get_file(self, document_id, document_type, contract_type):
        """
        Calls GetFile method.

        document_type and contract_type must match the enumerations specified by WSDL.
        """
        FileRequestType = self.client.get_type("ns0:GetFileRequest")
        file_request = FileRequestType(DocumentId=document_id, DocumentType=document_type, ContractType=contract_type)

        return self.service.GetFile(SecurityToken=self.security_token, fileRequest=file_request)

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

    def save_rca_document(self, document_request):
        """
        Calls SaveRcaDocument.

        document_request should be constructed according to the ns0:RcaDocumentModel.
        """
        return self.service.SaveRcaDocument(SecurityToken=self.security_token, request=document_request)

    def save_greencard_document(self, document_request):
        """
        Calls SaveGreenCardDocument.

        document_request should be constructed according to the ns0:GreenCardDocumentModel.
        """
        return self.service.SaveGreenCardDocument(SecurityToken=self.security_token, request=document_request)

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
