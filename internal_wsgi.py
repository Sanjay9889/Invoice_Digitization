from invoice_internal_api_app.core import create_app
from flask import request, g
import traceback
import time
import logging

if __name__ == "__main__":  # pragma: no cover
    app = create_app()
    app.app_context().push()


    @app.before_request
    def before_request():
        g.start = time.time()

    @app.after_request
    def after_request(response):
        """ Logging after every request. """
        # This avoids the duplication of registry in the log,
        # since that 500 is already logged via @app.errorhandler.
        if response.status_code not in [400, 500, 422]:
            app.logger.info('%s %s %s %s %s',
                            request.remote_addr,
                            request.method,
                            request.scheme,
                            request.full_path,
                            response.status)
        if response.status_code == 400:
            print(" Status code 400")
            tb = traceback.format_exc()
            app.logger.error('%s %s %s %s 400 ERROR ENTITY\n%s',
                             request.remote_addr,
                             request.method,
                             request.scheme,
                             request.full_path,
                             tb)
            # return "BadRequest", 400

        # Adding execution time for each api call
        time_diff = time.time() - g.start
        app.logger.info("Execution Time: {} seconds".format(time_diff))

        return response


    @app.errorhandler(422)
    def exceptions(e):
        """ Logging after every Exception. """
        tb = traceback.format_exc()
        app.logger.error('%s %s %s %s 422 UNPROCESSABLE ENTITY\n%s',
                         request.remote_addr,
                         request.method,
                         request.scheme,
                         request.full_path,
                         tb)
        return "BadRequest", 400


    @app.errorhandler(Exception)
    def exceptions(e):
        """ Logging after every Exception. """
        print("in Exception")
        tb = traceback.format_exc()
        app.logger.error('%s %s %s %s 5xx INTERNAL SERVER ERROR\n%s',
                         request.remote_addr,
                         request.method,
                         request.scheme,
                         request.full_path,
                         tb)
        return "Internal Server Error", 500

    print("host name here", 5000)
    app.run(host="localhost", port=5000,
            debug=app.config.get('DEBUG', True))
else:
    app = create_app()
    app.app_context().push()


    @app.before_request
    def before_request():
        g.start = time.time()

    @app.after_request
    def after_request(response):
        """ Logging after every request. """
        # This avoids the duplication of registry in the log,
        # since that 500 is already logged via @app.errorhandler.
        if response.status_code not in [400, 500, 422]:
            app.logger.info('%s %s %s %s %s',
                            request.remote_addr,
                            request.method,
                            request.scheme,
                            request.full_path,
                            response.status)
        if response.status_code == 400:
            print(" Status code 400")
            tb = traceback.format_exc()
            app.logger.error('%s %s %s %s 400 ERROR ENTITY\n%s',
                             request.remote_addr,
                             request.method,
                             request.scheme,
                             request.full_path,
                             tb)
            # return "BadRequest", 400

        # Setting log level
        app.logger.setLevel(logging.DEBUG)

        # Adding execution time for each api call
        time_diff = time.time() - g.start
        app.logger.info("Execution Time: {} seconds".format(time_diff))

        return response


    @app.errorhandler(422)
    def exceptions(e):
        """ Logging after every Exception. """
        tb = traceback.format_exc()
        app.logger.error('%s %s %s %s 422 UNPROCESSABLE ENTITY\n%s',
                         request.remote_addr,
                         request.method,
                         request.scheme,
                         request.full_path,
                         tb)
        return "BadRequest", 400


    @app.errorhandler(Exception)
    def exceptions(e):
        """ Logging after every Exception. """
        print("in Exception")
        tb = traceback.format_exc()
        app.logger.error('%s %s %s %s 5xx INTERNAL SERVER ERROR\n%s',
                         request.remote_addr,
                         request.method,
                         request.scheme,
                         request.full_path,
                         tb)
        return "Internal Server Error", 500