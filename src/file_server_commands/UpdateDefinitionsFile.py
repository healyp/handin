import os
import yaml
from const import *
from file_server_commands.AbstractCommand import AbstractCommand
from handin_messaging import *
import logging
from handin_file_server import *

class UpdateDefinitionsFile(AbstractCommand):
    COMMAND = FileServerCommands.UPDATE_DEFINITIONS_FILE

    def __init__(self):
        super().__init__()

    def handleRequest(self, request: Request):
        args = request.args

        definitions_file = None
        definitions = None

        if 'definitions_file' in args:
            definitions_file = args['definitions_file']

        if 'definitions' in args:
            definitions = args['definitions']

        log_message = ""
        error_message = ""
        showError = False

        if not definitions_file:
            log_message = "Mandatory definitions_file parameter not provided"
            error_message = "You need to provide a definitions_file parameter"
            showError = True
        elif not definitions:
            log_message = "Mandatory definitions parameter not provided"
            error_message = "You need to provide a definitions parameter"
            showError = True

        if showError:
            request_bad("UPDATE_DEFINITIONS_FILE", log_message)
            respond(request, False, error_message)
        else:
            logging.debug(f"Updating definitions file {definitions_file}")
            if not os.path.isfile(definitions_file):
                logging.debug(f"File does not exist, creating it")
                with open(definitions_file, 'w') as file:
                    pass

            with open(definitions_file, 'w') as file:
                # TODO: any more defs to add??
                yaml.dump(definitions, file, default_flow_style=False)

            request_ok("UPDATE_DEFINITIONS_FILE")
            respond(request, True, "UPDATE_DEFINITIONS_FILE successful")
