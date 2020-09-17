"""
This file is designed to handle long running digiMOPs.
"""
import json
import threading
import time
import uuid
from datetime import datetime
from functools import wraps

from flask import current_app, request, url_for, Response
from werkzeug.exceptions import HTTPException, InternalServerError

from invoice_common.common.constants import AsyncProcessingStatus
from wsgi import application

# Creating a data structure to store request.
# This will be used for storing long running requests
TASKS = {}


# Remove below function if there is no long running digiMOP
@application.before_first_request
def before_first_request():
    """Start a background thread that cleans up old tasks."""

    def clean_old_tasks():
        """
        This function cleans up old tasks from our in-memory data structure.
        """
        global TASKS
        while not TASKS:
            # Only keep tasks that are running or that finished less than 5
            # minutes ago.
            five_min_ago = datetime.timestamp(datetime.utcnow()) - 5 * 60
            TASKS = {task_id: task for task_id, task in TASKS.items()
                     if 'completion_timestamp' not in task or task[
                         'completion_timestamp'] > five_min_ago}
            time.sleep(60)

    thread = threading.Thread(target=clean_old_tasks)
    thread.start()


def async_task(wrapped_function):
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
            "Operation_Id": str(task_id),
            "status_url": url_for('request_status', task_id=task_id),
        }), status=200, mimetype='application/json')

    return new_function


# Below rest API would be used to get the status for long running digiMOP
@application.route('/OperationStatus', methods=['GET', 'POST'])
def request_status():
    """
    Return status about an asynchronous task. If this request returns a 202
    status code, it means that task hasn't finished yet. Else, the response
    from the task is returned.
    """
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
            "status_url": url_for('request_status', task_id=task_id),
        }), status=202, mimetype='application/json')
    return task['return_value']
