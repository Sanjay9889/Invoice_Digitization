from schematics import Model
from schematics.types import StringType, FloatType, IntType, DateTimeType


class InvoiceForm(Model):
    Invoice_Number = StringType(required=True)
    DueDate = StringType(required=False)
    Balance = StringType(required=False)
    Status = StringType(required=False)
    Vendor = StringType(required=False)
    APRef = StringType(required=False)
    TotalAmt = StringType(required=False)

