import os
import yaml
from const import *
from file_server_commands.AbstractCommand import AbstractCommand
from handin_messaging import *
import logging
from handin_file_server import *

class GetVars(AbstractCommand):
    COMMAND = FileServerCommands.GET_VARS

    def __init__(self):
        super().__init__()

    def handleRequest(self, request: Request):
        params = self.getVarsParameters(request)

        if params is not None:
            module, week_number, student_id = params
            vars_filepath = const.get_vars_file_path(module, week_number, student_id)
            logging.debug(f"Using filepath {vars_filepath}")

            vars = {}
            if os.path.isfile(vars_filepath):
                with open(vars_filepath, 'r') as stream:
                    vars: dict = yaml.safe_load(stream)
            else:
                logging.debug(f"File {vars_filepath} does not exist")

            response_data = {
                'vars': vars,
                'test': 'succeeded'
            }

            request_ok("GET_VARS")
            respond(request, True, "GET_VARS successful", response_data)

    def getVarsParameters(self, request: Request):
        params = request.args

        module = None
        week_number = None
        student_id = None

        if 'module' in params:
            module = params['module']

        if 'week_number' in params:
            week_number = params['week_number']

        if 'student_id' in params:
            student_id = params['student_id']

        log_message = ""
        error_message = ""
        send_error = False

        if not module:
            log_message = "Mandatory module parameter not provided"
            error_message = "You need to provide a module to this request"
            send_error = True
        elif not week_number:
            log_message = "Mandatory week_number parameter not provided"
            error_message = "You need to provide a week_number to this request"
            send_error = True
        elif not student_id:
            log_message = "Mandatory student_id parameter not provided"
            error_message = "You need to provide a student_id to this request"
            send_error = True

        if send_error:
            request_bad("GET_VARS", log_message)
            respond(request, False, error_message)
            return None
        else:
            return module, week_number, student_id
