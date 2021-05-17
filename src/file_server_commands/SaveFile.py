import os
from const import *
from file_server_commands.AbstractCommand import AbstractCommand
from handin_messaging import *
import logging
from handin_file_server import *

class SaveFile(AbstractCommand):
    COMMAND = FileServerCommands.FILE_SAVE

    def __init__(self):
        super().__init__()

    def handleRequest(self, request: Request):
        # TODO sending a file in a single request may be too big. Consider changing how large text is sent, maybe in handin_messaging check the size of the string and split it into multiple sendall calls with the final call having DONE at the end
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
            request_bad("FILE_SAVE", log_message)
            respond(request, False, error_message)
        else:
            newAssignmentPath = os.path.join(ROOTDIR + "/" + module + "/curr/assignments/" + assignment)
            logging.debug(f"Creating directory {newAssignmentPath}")
            os.makedirs(newAssignmentPath)
            filename = os.path.join(newAssignmentPath + "/params.yaml")
            logging.debug(f"Creating file {filename}")
            file = open(filename, 'w')
            file.write(self.textEdit_showFileContent.toPlainText())
            file.close()

            request_ok("FILE_SAVE")
            respond(request, True, "FILE_SAVE successful")
