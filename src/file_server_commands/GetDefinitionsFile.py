import os
import yaml
from const import *
from file_server_commands.AbstractCommand import AbstractCommand
from handin_messaging import *
import logging
from handin_file_server import *

class GetDefinitionsFile(AbstractCommand):
    COMMAND = FileServerCommands.GET_DEFINITIONS_FILE

    def __init__(self):
        super().__init__()

    def handleRequest(self, request: Request):
        params = request.args

        if 'module' in params:
            module = params['module']

        if 'academic_year' in params:
            academic_year = params['academic_year']

        log_message = ""
        error_message = ""
        showError = False

        if not module:
            log_message = "Mandatory module parameter not provided"
            error_message = "You need to provide a module parameter"
            showError = True
        elif not academic_year:
            log_message = "Mandatory academic_year parameter not provided"
            error_message = "You need to provide an academic_year parameter"
            showError = True

        if showError:
            request_bad("GET_DEFINITIONS_FILE", log_message)
            respond(request, False, error_message)
        else:
            moduleDir = const.modulePath(module, academic_year)
            definitions_file = os.path.join(moduleDir, "definitions.yaml")
            if os.path.isfile(definitions_file):
                logging.debug(f"Opening definitions file {definitions_file}")
                with open(definitions_file, 'r') as stream:
                    definitions: dict = yaml.safe_load(stream)
            else:
                logging.debug(f"The file {definitions_file} doesn't exist")
                definitions = {}

            response_data = {
                'definitions': definitions
            }

            request_ok("GET_DEFINITIONS_FILE")
            respond(request, True, "GET_DEFINITIONS_FILE successful", response_data)
