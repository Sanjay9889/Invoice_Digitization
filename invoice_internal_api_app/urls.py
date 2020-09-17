from invoice_internal_api_app.api.invoice.views import InvoiceView


def setup_blueprints(api):
    api.add_resource(InvoiceView, '/api/invoice/', '/api/invoice/<string:invoice_number>')
