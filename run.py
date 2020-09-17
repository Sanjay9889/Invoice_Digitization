from invoice_external_api_app.core import create_app as external_app
from invoice_internal_api_app.core import create_app as internal_app
from invoice_common.core import create_app as common_app
from werkzeug.serving import run_simple
from werkzeug.wsgi import DispatcherMiddleware

ext_app = external_app()
int_app = internal_app()
app = common_app()
application = DispatcherMiddleware(app, {
    '/external_app': ext_app,
    '/internal_app': int_app
})

if __name__ == '__main__':
    run_simple('localhost', 5000, application, use_reloader=True,
               use_debugger=True, use_evalex=True)
