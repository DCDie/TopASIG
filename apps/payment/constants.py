from django.db import models


class QrTypeChoices(models.TextChoices):
    DYNAMIC = "Dynamic", "Dynamic"
    STATIC = "Static", "Static"
    HYBRID = "Hybrid", "Hybrid"


class AmountTypeChoices(models.TextChoices):
    FIXED = "Fixed", "Fixed"
    CONTROLLED = "Controlled", "Controlled"
    FREE = "Free", "Free"


class PmtContextChoices(models.TextChoices):
    MOBILE_PAYMENT = "m", "Mobile Payment"
    ECOMMERCE_PAYMENT = "e", "E-commerce Payment"
    INVOICE_PAYMENT = "i", "Invoice Payment"
    OTHER = "0", "Other"


class StatusChoices(models.TextChoices):
    ACTIVE = "Active", "Active"
    PAID = "Paid", "Paid"
    EXPIRED = "Expired", "Expired"
    CANCELLED = "Cancelled", "Cancelled"
    REPLACED = "Replaced", "Replaced"
    INACTIVE = "Inactive", "Inactive"


class UnitsChoices(models.TextChoices):
    MM = "mm", "Minutes"
    SS = "ss", "Seconds"
