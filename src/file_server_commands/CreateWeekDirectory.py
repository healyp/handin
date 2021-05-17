import os
from const import *
from file_server_commands.AbstractCommand import AbstractCommand
from handin_messaging import *
import logging
from handin_file_server import *

class CreateWeekDirectory(AbstractCommand):
    COMMAND = FileServerCommands.CREATE_WEEK_DIRECTORY

    def __init__(self):
        super().__init__()

    def handleRequest(self, request: Request):
        params = request.args

        module = None
        week_number = None

        if 'module' in params:
            module = params['module']

        if 'week_number' in params:
            week_number = params['week_number']

        log_message = ""
        error_message = ""
        showError = False

        if not module:
            log_message = "Mandatory module parameter not provided"
            error_message = "You need to provide a module parameter"
            showError = True
        elif not week_number:
            log_message = "Mandatory week_number parameter not provided"
            error_message = "You need to provide a week_number parameter"
            showError = True

        if showError:
            request_bad("CREATE_WEEK_DIRECTORY", log_message)
            respond(request, False, error_message)
        else:
            path = f"{ROOTDIR}/{module}/curr/assignments/{week_number}"
            if not os.path.exists(path):
                os.makedirs(path)
                logging.debug(f"Creating directory {path}")
            else:
                logging.debug(f"Path {path} already exists, not creating it")

            params_path = os.path.join(path, "params.yaml")
            if not os.path.exists(params_path):
                with open(params_path, "w"):
                    pass

            response_data = {
                'params_path': params_path
            }

            request_ok("CREATE_WEEK_DIRECTORY")
            respond(request, True, "CREATE_WEEK_DIRECTORY successful", response_data)
