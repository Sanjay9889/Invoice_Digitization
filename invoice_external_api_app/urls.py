from invoice_external_api_app.api.invoice.views import InvoiceView
from invoice_external_api_app.api.invoice.views import InvoiceStatusView


def setup_blueprints(api):
    api.add_resource(InvoiceView, '/api/invoice/', '/api/invoice/<string:invoice_number>')
    api.add_resource(InvoiceStatusView, '/api/invoice_status/')
