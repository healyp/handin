from const import *
from file_server_commands.AbstractCommand import AbstractCommand
from handin_messaging import *
import logging
from handin_file_server import *

class AuthenticateLecturer(AbstractCommand):
    COMMAND = FileServerCommands.AUTHENTICATE_LECTURER

    def __init__(self):
        super().__init__()

    def handleRequest(self, request: Request):
        params = request.args

        # the AUTHENTICATE_LECTURER request for checkCredentials is essentially the same call made to authenticate
        # a request from a lecturer to access lecturer resources, so use the same authenticate_lecturer method and only
        # that method to carry out this request
        if (authenticate_lecturer(request, "AUTHENTICATE_LECTURER")):
            request_ok("AUTHENTICATE_LECTURER")
            logging.debug(f"Sending success response with AUTHENTICATED message")
            respond(request, True, "AUTHENTICATED")
        else:
            request_ok("AUTHENTICATE_LECTURER")
            logging.debug(f"Sending success response with NOT_AUTHENTICATED message")
            respond(request, True, "NOT_AUTHENTICATED")
