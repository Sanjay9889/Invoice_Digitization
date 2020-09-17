import json
import threading
import time
import uuid
from datetime import datetime
from functools import wraps
from http.client import HTTPException

from flask import Response, request, current_app
from flask_restful import Resource
from werkzeug.exceptions import InternalServerError

from invoice_common.common.constants import AsyncProcessingStatus, SampleInvoice

TASKS = {}


def process_invoice_background(wrapped_function):
    """This is a decorator function."""

    @wraps(wrapped_function)
    def new_function(*args, **kwargs):
        def task_call(flask_app, environ):
            # Create a request context similar to that of the original request
            # so that the task can have access to flask.g, flask.request, etc.
            with flask_app.request_context(environ):
                try:
                    TASKS[task_id]['return_value'] = wrapped_function(*args, **kwargs)
                except HTTPException as http_exception:
                    TASKS[task_id]['return_value'] = current_app.handle_http_exception(
                        http_exception)
                except Exception:
                    # The function raised an exception, so we set a 500 error
                    TASKS[task_id]['return_value'] = InternalServerError()
                    if current_app.debug:
                        # We want to find out if something happened so reraise
                        raise
                finally:
                    # We record the time of the response, to help in garbage
                    # collecting old tasks
                    TASKS[task_id]['completion_timestamp'] = datetime.timestamp(
                        datetime.utcnow())
                    # close the database session (if any)

        # Assign an id to the asynchronous task
        task_id = uuid.uuid4().hex

        # Record the task, and then launch it
        TASKS[task_id] = {'task_thread': threading.Thread(
            target=task_call, args=(current_app._get_current_object(), request.environ))}
        TASKS[task_id]['task_thread'].start()

        # Return a 202 response, with a link that the client can use to
        # obtain task status

        return Response(response=json.dumps({
            "status": "Accepted",
            "Timeout": str(AsyncProcessingStatus.INVOICE_TIMEOUT),
            "Operation_Id": str(task_id)
        }), status=200, mimetype='application/json')

    return new_function


class InvoiceView(Resource):

    def get(self, invoice_number):
        """
        Get digital invoice data for a given invoice number
        :param invoice_number: Invoice number for processed invoice
        :return: Digitalized invoice data if success, error otherwise
        """
        try:
            for existing_invoice in SampleInvoice.SAMPLE_INVOICES:
                if invoice_number == existing_invoice["Invoice_Number"]:
                    return Response(
                        response=json.dumps({'invoice': existing_invoice["Invoice_Data"]}),
                        status=200, mimetype='application/json'
                    )
            return Response(
                response=json.dumps({'message': f"There is no matching invoice for invoice "
                                                f"number:- {invoice_number}"}),
                status=400, mimetype='application/json'
            )

        except Exception as e:
            return Response(
                response=json.dumps({'message': f"Unable to fetch invoice and the error is {e}"}),
                status=400, mimetype='application/json'
            )

    # PDF Invoice processing might be a time consuming operation
    # Using threading to process invoice in background - Ideally it thread is not a correct
    # solution. We should be using celery or similar tools. But for this this assignment it is
    # fine.
    @process_invoice_background
    def post(self):
        try:

            data_file = request.files['invoice_file']
            if not data_file:
                return Response(response=json.dumps({
                    "message": "Invalid invoice file"}),
                    status=400, mimetype='application/json')

            # TODO: logic to process pdf invoice file
            # Assuming pdf process take a minute
            time.sleep(AsyncProcessingStatus.INVOICE_SLEEP)

            return Response(response=json.dumps({
                "Operation_Status": "Processed",
                "Invoice_Number": "SAMP001"}),
                status=200, mimetype='application/json')

        except Exception as e:
            return Response(
                response=json.dumps({'message': f"Unable to process invoice "
                                                f"file and the error was {e}"}),
                status=400, mimetype='application/json'
            )


class InvoiceStatusView(Resource):

    def post(self):
        """
            Return status about an invoice processing async task. If this request returns a 202
            status code, it means that task hasn't finished yet. Else, the response
            from the task is returned.
            """
        try:
            json_data = request.json
            task_id = json_data["Operation_Id"]
            task = TASKS.get(task_id)
            if task is None:
                return Response(response=json.dumps({
                    "Operation_Status": "Failed",
                    "Failed_Message": "Invalid operation id"
                }), status=400, mimetype='application/json')

            if 'return_value' not in task:
                return Response(response=json.dumps({
                    "Operation_Status": "In-Progress",
                }), status=202, mimetype='application/json')
            return task['return_value']
        except Exception as e:
            return Response(response=json.dumps({
                "message": f"Unable to fetch the status and error was {e}"
            }), status=400, mimetype='application/json')