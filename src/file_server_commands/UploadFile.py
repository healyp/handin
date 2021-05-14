import os
from const import *
from file_server_commands.AbstractCommand import AbstractCommand
from handin_messaging import *
import logging
from handin_file_server import *

class UploadFile(AbstractCommand):
    COMMAND = FileServerCommands.UPLOAD_FILE

    def __init__(self):
        super().__init__()

    def handleRequest(self, request: Request):
        params = request.args

        contents = None
        destination = None

        log_message = ""
        error_message = ""
        showError = False

        if 'contents' in params:
            contents = params['contents']

        if 'destination' in params:
            destination = params['destination']

        if not contents:
            log_message = "Mandatory contents parameter not provided"
            error_message = "You need to provide a contents parameter"
            showError = True
        elif not destination:
            log_message = "Mandatory destination parameter not provided"
            error_message = "You need to provide a destination parameter"
            showError = True

        if showError:
            request_bad("UPLOAD_FILE", log_message)
            respond(request, False, error_message)
        else:
            path = ROOTDIR + "/" + destination
            if not os.path.isdir(path):
                dir = os.path.dirname(path)

                try:
                    if not os.path.isdir(dir):
                        logging.debug(f"The path {dir} does not exist, attempting to create it before uploading the file")
                        os.makedirs(dir)

                    with open(path, 'w', newline='') as destination_file:
                        destination_file.write(contents)

                    request_ok("UPLOAD_FILE")
                    respond(request, True, "UPLOAD_FILE successful")
                except (OSError, FileNotFoundError) as e:
                    e = format_exc()
                    request_ok("UPLOAD_FILE")
                    logging.debug(f"Could not upload file to path due to error: {e}")
                    respond(request, False, "An error occurred uploading the file, please try again")
            else:
                request_ok("UPLOAD_FILE")
                logging.debug(f"The path {path} exists as a directory, cannot create file")
                respond(request, False, "Could not upload the file as it already exists as a directory")
