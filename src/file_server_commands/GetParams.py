import os
from const import *
from file_server_commands.AbstractCommand import AbstractCommand
from handin_messaging import *
import logging
from handin_file_server import *

class GetParams(AbstractCommand):
    COMMAND = FileServerCommands.GET_PARAMS

    def __init__(self):
        super().__init__()

    def handleRequest(self, request: Request):
        args = requesta.args

        module = None
        assignment = None

        log_message = ""
        error_message = ""
        showError = False

        if 'module' in params:
            module = params['module']

        if 'assignment' in params:
            assignment = params['assignment']

        if not module:
            log_message = "Mandatory module parameter not provided"
            error_message = "You need to provide a module parameter"
            showError = True
        elif not assignment:
            log_message = "Mandatory assignment parameter not provided"
            error_message = "You need to provide an assignment parameter"
            showError = True

        if showError:
            request_bad("GET_PARAMS", log_message)
            respond(request, False, error_message)
        else:
            filename = os.path.join(ROOTDIR + module + "/curr/assignments/" + assignment +"/params.yaml")
            logging.debug(f"Reading file {filename}")
            try:
                with open(filename, 'rb') as f:
                    content = f.read().decode('utf-8')
            except Exception as e:
                content = ""

            response_data = {
                'content': content,
                'filename': filename
            }

            request_ok("GET_PARAMS")
            respond(request, True, "GET_PARAMS successful", response_data)
