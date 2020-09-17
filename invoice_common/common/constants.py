class AsyncProcessingStatus:
    INVOICE_TIMEOUT = 120
    INVOICE_SLEEP = 60


class SampleInvoice:
    SAMPLE_INVOICES = [{
        "Invoice_Number": "SAMP001",
        "Invoice_Data": {
            "Invoice_Number": "SAMP001",
            "DueDate": "2013-02-15",
            "Balance": 1990.19,
            "Status": "Payable",
            "Vendor": "Sample Bank",
            "APRef":  "Accounts Payable",
            "TotalAmt": 1990.19
        }
    }]

