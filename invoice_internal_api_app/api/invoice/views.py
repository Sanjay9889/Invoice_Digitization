import json

from flask import request, Response
from flask_restful import Resource

from invoice_common.common.constants import SampleInvoice
from invoice_internal_api_app.api.invoice.forms import InvoiceForm


class InvoiceView(Resource):

    def post(self):
        """
        Add invoice by internal user
        :return:
        """
        try:
            form = InvoiceForm(request.json)
            form.validate()
            data = request.json
            data_dict = dict()
            data_dict["Invoice_Number"] = data["Invoice_Number"]
            child_dict = dict()
            child_dict["DueDate"] = data.get("DueDate", "")
            child_dict["Balance"] = data.get("Balance", "")
            child_dict["Status"] = data.get("Status", "")
            child_dict["Vendor"] = data.get("Vendor", "")
            child_dict["APRef"] = data.get("APRef", "")
            child_dict["TotalAmt"] = data.get("TotalAmt", "")
            data_dict["Invoice_Data"] = child_dict
            SampleInvoice.SAMPLE_INVOICES.append(data_dict)
            return Response(response=json.dumps({
                "message": "Invoice created successfully"}),
                status=200, mimetype='application/json')

        except Exception as e:
            return Response(response=json.dumps({
                "message": f"Unable to create invoice and error was: {e}"}),
                status=400, mimetype='application/json')

    def put(self):
        """
        Update invoice by internal user
        :return:
        """
        try:
            form = InvoiceForm(request.json)
            form.validate()
            data = request.json
            invoice_number = data["Invoice_Number"]
            due_date = data.get("DueDate", "")
            balance = data.get("Balance", "")
            status = data.get("Status", "")
            vendor = data.get("Vendor", "")
            ap_ref = data.get("APRef", "")
            total_amt = data.get("TotalAmt", "")
            for invoice in SampleInvoice.SAMPLE_INVOICES:
                if invoice_number == invoice["Invoice_Number"]:
                    data_dict = invoice["Invoice_Data"]
                    data_dict["DueDate"] = due_date
                    data_dict["Balance"] = balance
                    data_dict["Status"] = status
                    data_dict["Vendor"] = vendor
                    data_dict["APRef"] = ap_ref
                    data_dict["TotalAmt"] = total_amt
                    return Response(response=json.dumps({
                        "message": "Updated successfully"}),
                        status=200, mimetype='application/json')

            return Response(response=json.dumps({
                "message": "Invalid invoice number"}),
                status=400, mimetype='application/json')

        except Exception as e:
            return Response(response=json.dumps({
                "message": f"Unable to update invoice and error was {e}"}),
                status=400, mimetype='application/json')

    def get(self, invoice_number):
        """
        Get the status of invoice. Whether the invoice is digitalised or not
        :param invoice_number: Invoice number
        :return: Status of digitisation
        """
        try:
            for invoice in SampleInvoice.SAMPLE_INVOICES:
                if invoice_number == invoice["Invoice_Number"]:
                    return Response(response=json.dumps({
                        "message": "Invoice is digitalised"}),
                        status=200, mimetype='application/json')

            return Response(response=json.dumps({
                "message": "The invoice is not yet digitalised"}),
                status=400, mimetype='application/json')

        except Exception as e:
            return Response(response=json.dumps({
                "message": f"Unable to get the status and error was {e}"}),
                status=400, mimetype='application/json')