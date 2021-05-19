import os
from const import *
from file_server_commands.AbstractCommand import AbstractCommand
from handin_messaging import *
import logging
from handin_file_server import *

class CreateAssignmentDirectory(AbstractCommand):
    COMMAND = FileServerCommands.CREATE_ASSIGNMENT_DIRECTORY

    def __init__(self):
        super().__init__()

    def handleRequest(self, request: Request):
        params = request.args

        module = None
        assignment = None

        if 'module' in params:
            module = params['module']

        if 'assignment' in params:
            assignment = params['assignment']

        log_message = ""
        error_message = ""
        showError = False

        if not module:
            log_message = "Mandatory module parameter not provided"
            error_message = "You need to provide a module parameter"
            showError = True
        elif not assignment:
            log_message = "Mandatory assignment parameter not provided"
            error_message = "You need to provide an assignment parameter"
            showError = True

        if showError:
            request_bad("CREATE_ASSIGNMENT_DIRECTORY", log_message)
            respond(request, False, error_message)
        else:
            path = f"{ROOTDIR}/{module}/curr/assignments/{assignment}"
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

            request_ok("CREATE_ASSIGNMENT_DIRECTORY")
            respond(request, True, "CREATE_ASSIGNMENT_DIRECTORY successful", response_data)
