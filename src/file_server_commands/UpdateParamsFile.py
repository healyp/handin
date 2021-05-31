import shlex
from const import *
from file_server_commands.AbstractCommand import AbstractCommand
from handin_messaging import *
import logging
from handin_file_server import *

class UpdateParamsFile(AbstractCommand):
    COMMAND = FileServerCommands.UPDATE_PARAMS_FILE

    def __init__(self):
        super().__init__()

    def escapeCommand(self, command):
        split_command = shlex.split(command)
        return shlex.join(split_command) # this should have sufficient escaping

    """
        Escape the commands in the params file to avoid security gaps
    """
    def escapeCommands(self, params: dict):
        if "tests" in params:
            tests = params["tests"]
            for key, val in tests.items():
                if "command" in val:
                    command = tests[key]["command"]
                    if command != "":
                        tests[key]["command"] = self.escapeCommand(command)

                if "filterCommand" in val:
                    filterCommand = tests[key]["filterCommand"]
                    if filterCommand != "":
                        tests[key]["filterCommand"] = self.escapeCommand(filterCommand)


    def handleRequest(self, request: Request):
        args = request.args

        params_file = None
        params = None

        if 'params_file' in args:
            params_file = args['params_file']

        if 'params' in args:
            params = args['params']

        log_message = ""
        error_message = ""
        showError = False

        if not params_file:
            log_message = "Mandatory params_file parameter not provided"
            error_message = "You need to provide a params_file parameter"
            showError = True
        elif not params:
            log_message = "Mandatory params parameter not provided"
            error_message = "You need to provide a params parameter"
            showError = True

        if showError:
            request_bad("UPDATE_PARAMS_FILE", log_message)
            respond(request, False, error_message)
        else:
            logging.debug(f"Updating params file {params_file}")
            if not os.path.isfile(params_file):
                logging.debug(f"File does not exist, creating it")
                with open(params_file, 'w') as file:
                    pass

            self.escapeCommands(params)

            with open(params_file, 'w') as file: # TODO make sure w instead of a is ok
                # TODO: any more params to add??
                yaml.dump(params, file, default_flow_style=False)

            request_ok("UPDATE_PARAMS_FILE")
            respond(request, True, "UPDATE_PARAMS_FILE successful")
