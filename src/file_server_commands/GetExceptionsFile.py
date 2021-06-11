import os.path

import yaml

import const
from const import FileServerCommands, check_if_module_exists, check_if_ass_exists, whatAY
from file_server_commands.AbstractCommand import AbstractCommand
from handin_messaging import *
from handin_file_server import *

class GetExceptionsFile(AbstractCommand):
    COMMAND = FileServerCommands.GET_EXCEPTIONS_FILE

    def __init__(self):
        super().__init__()

    def get_exceptions(self, exceptions_path):
        if os.path.isfile(exceptions_path):
            with open(exceptions_path, 'r') as file:
                return yaml.safe_load(file)

        return {}

    def getExceptionsFile(self, request, module, assignment):
        if not check_if_module_exists(module):
            request_ok("GET_EXCEPTIONS_FILE")
            respond(request, False, f"Module {module} doesn't exist")
            return False
        elif not check_if_ass_exists(module, whatAY(), assignment):
            request_ok("GET_EXCEPTIONS_FILE")
            respond(request, False, f"Assignment {assignment} doesn't exist")
            return False

        exceptions_path = os.path.join(const.ROOTDIR, module, "curr", "assignments", assignment, "exceptions.yaml")

        return self.get_exceptions(exceptions_path) or {}

    def handleRequest(self, request: Request):
        if authenticate_lecturer(request, "GET_EXCEPTIONS_FILE", False):
            args = request.args

            module = None
            assignment = None

            if 'module' in args:
                module = args['module']

            if 'assignment' in args:
                assignment = args['assignment']

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
                request_bad("GET_EXCEPTIONS_FILE", log_message)
                respond(request, False, error_message)
            else:
                exceptions = self.getExceptionsFile(request, module, assignment)

                if exceptions is not None and exceptions != False:
                    data = {
                        'exceptions': exceptions
                    }
                    request_ok("GET_EXCEPTIONS_FILE")
                    respond(request, True, "GET_EXCEPTIONS_FILE successful", data)
                else:
                    request_ok("GET_EXCEPTIONS_FILE")
                    respond(request, False, "An unknown error occurred retrieving exceptions")

        else:
            request_unauthorized("GET_EXCEPTIONS_FILE")
            send_unauthorized_lecturer_response(request)
