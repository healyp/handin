from const import *
from file_server_commands.AbstractCommand import AbstractCommand
from handin_messaging import *
import logging
from handin_file_server import *

class GetLecturerModules(AbstractCommand):
    COMMAND = FileServerCommands.GET_LECTURER_MODULES

    def __init__(self):
        super().__init__()

    def handleRequest(self, request: Request):
        if (authenticate_lecturer(request, "GET_LECTURER_MODULES", False)):
            params = request.args
            lecturer = params['lecturer']

            filepath = ROOTDIR + "/access_rights.txt"
            logging.debug(f"Reading file {filepath}")
            modules = []

            if os.path.isfile(filepath):
                with open(filepath, 'r') as f:
                    for ln in f:
                        if ln.startswith(lecturer):
                            data = ln.split()
                            for module in data[1:]:
                                modules.append(module)

            response_data = {
                'modules': modules
            }

            request_ok("GET_LECTURER_MODULES")
            respond(request, True, "GET_LECTURER_MODULES successful", response_data)
        else:
            request_unauthorized("GET_LECTURER_MODULES")
            send_unauthorized_lecturer_response(request)
