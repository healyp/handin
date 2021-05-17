import os
from const import *
from file_server_commands.AbstractCommand import AbstractCommand
from handin_messaging import *
import logging
from handin_file_server import *

class CreateDefinitionsFile(AbstractCommand):
    COMMAND = FileServerCommands.CREATE_DEFINITIONS_FILE

    def __init__(self):
        super().__init__()

    def handleRequest(self, request: Request):
        params = request.args

        module = None
        academic_year = None

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
            request_bad("CREATE_DEFINITIONS_FILE", log_message)
            respond(request, False, error_message)
        else:
            logging.debug(f"Creating definitions file for module {module} and academic year {academic_year}")
            moduleDir = const.modulePath(module, academic_year)
            """create tmpdir and definitions file"""
            definitions_path = os.path.join(moduleDir, "definitions.yaml")
            if not os.path.exists(definitions_path):
                logging.debug(f"{definitions_path} does not exist, creating it")
                with open(definitions_path, "w"):
                    pass
            else:
                logging.debug(f"{definitions_path} already exists, not creating it")

            response_data = {
                'definitions_path': definitions_path
            }

            request_ok("CREATE_DEFINITIONS_FILE")
            respond(request, True, "CREATE_DEFINITIONS_FILE successful", response_data)
