from django.db import models
from django.utils.translation import gettext_lazy as _


class Territories(models.TextChoices):
    C = "C", _("C")
    BL = "BL", _("BL")
    HN = "HN", _("HN")
    OR = "OR", _("OR")
    ST = "ST", _("ST")
    IL = "IL", _("IL")
    AN = "AN", _("AN")
    CR = "CR", _("CR")
    OTHER = "OTHER", _("OTHER")


class GreenCardZones(models.TextChoices):
    Z1 = "Z1", _("Zona 1 - Ucraina și Belarus")
    Z3 = "Z3", _("Zona 3 - Toate țările sistemului carte verde")


class TermInsurance(models.TextChoices):
    D15 = "d15", _("15 zile")
    M1 = "m1", _("1 lună")
    M2 = "m2", _("2 luni")
    M3 = "m3", _("3 luni")
    M4 = "m4", _("4 luni")
    M5 = "m5", _("5 luni")
    M6 = "m6", _("6 luni")
    M7 = "m7", _("7 luni")
    M8 = "m8", _("8 luni")
    M9 = "m9", _("9 luni")
    M10 = "m10", _("10 luni")
    M11 = "m11", _("11 luni")
    M12 = "m12", _("12 luni")


class GreenCardVehicleCategories(models.TextChoices):
    A = "A", "A"
    C1 = "C1", "C1"
    C2 = "C2", "C2"
    E1 = "E1", "E1"
    E2 = "E2", "E2"
    B = "B", "B"
    F = "F", "F"


class OperationModes(models.TextChoices):
    USUAL = "1", _("Usual")
    MINIBUS = "2", _("Minibus")
    INTERCITYBUS = "3", _("IntercityBus")
    TAXI = "4", _("Taxi")
    RENTACAR = "5", _("RentACar")


class OperationModesStrings(models.TextChoices):
    USUAL = "Usual", _("Usual")
    MINIBUS = "Minibus", _("Minibus")
    INTERCITYBUS = "IntercityBus", _("IntercityBus")
    TAXI = "Taxi", _("Taxi")
    RENTACAR = "RentACar", _("RentACar")


class PaymentModes(models.TextChoices):
    CASH = "Cash", _("Cash")
    TRANSFER = "Transfer", _("Transfer")


class PossessionBase(models.TextChoices):
    PROPERTY = "Property", _("Property")
    LEASE = "Lease", _("Lease")
    LEASING = "Leasing", _("Leasing")
    POWER_OF_ATTORNEY = "PowerOfAttorney", _("Power of Attorney")


class DocumentType(models.TextChoices):
    CONTRACT = "Contract", _("Contract")
    DEMAND = "Demand", _("Demand")
    INSURANCE_POLICY = "InsurancePolicy", _("Insurance Policy")

class ContractType(models.TextChoices):
    RCAI = "RCAI", _("RCAI")
    CV = "CV", _("CV")