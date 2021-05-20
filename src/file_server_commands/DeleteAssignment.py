import os
from const import *
from file_server_commands.AbstractCommand import AbstractCommand
from handin_messaging import *
import logging
from handin_file_server import *
import shutil

class DeleteAssignment(AbstractCommand):
    COMMAND = FileServerCommands.DELETE_ASSIGNMENT

    def __init__(self):
        super().__init__()

    def handleRequest(self, request: Request):
        params = request.args

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
            request_bad("DELETE_ASSIGNMENT", log_message)
            respond(request, False, error_message)
        else:
            assignment_path = ROOTDIR + "/" + module + "/curr/assignments/" + assignment

            if os.path.isdir(assignment_path):
                logging.debug(f"Removing directory {assignment_path}")
                shutil.rmtree(assignment_path)


            data_path = ROOTDIR + "/" + module + "/curr/data"

            if os.path.isdir(data_path):
                for f in os.listdir(data_path):
                    student = data_path + "/" + f
                    assignment_path = student + "/" + assignment

                    if os.path.isdir(assignment_path):
                        logging.debug(f"Removing directory {assignment_path}")
                        shutil.rmtree(assignment_path)

            request_ok("DELETE_ASSIGNMENT")
            respond(request, True, "DELETE_ASSIGNMENT successful")
