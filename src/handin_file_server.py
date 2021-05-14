from pydoc import locate
import yaml
import sys
import os
import signal
import logging
import threading
import file_server_commands
from handin_messaging import Request, listenerSocket, acceptSocket, respond
from traceback import format_exc
import const
from const import ROOTDIR, FileServerCommands
from password_security import check_encrypted_password

"""
    This program provides a server which provides remote access to files in the
    .handin directory. This access is made indirectly in the form of requests.
    A request is composed of a pre-defined command (see const.FileServerCommands) and
    that command's arguments. The server then responds with the necessary data retrieved from
    the files.

    Therefore, the client never gets direct access to the files, instead the server only
    handles a specified request, processes the files based on that request and responds
    with the results.

    An example is the AUTHENTICATE_LECTURER command. This command reads .handin/login-credentials.txt,
    authenticates the lecturer and returns the authentication status without providing direct access to the
    login-credentials file
"""

logfile = os.path.join(const.ROOTDIR, "handin_file_server.log")
logging.basicConfig(filename=logfile, level=const.FILE_LOG_LEVEL, format='%(levelname)s: %(asctime)s %(message)s')

s = None

commands = {}

def load_file_server_commands():
    path = const.HANDINHOME + "/src/file_server_commands"
    files = [f for f in os.listdir(path) if f.endswith(".py") and f != "AbstractCommand.py" and f != "__init__.py"]

    for f in files:
        module_name = f[0:f.index(".py")]
        class_name = module_name
        module_name = "file_server_commands." + module_name
        command_class = locate(f"{module_name}.{class_name}")
        commands[command_class.COMMAND] = command_class()

    logging.debug(f"Loaded {len(files)} commands")

def do_kill():
    print("handin_file_server has been terminated")
    logging.info("Terminating server")
    if s is not None:
        s.close()

    sys.exit(0)

def signal_handler(sig, frame):
    do_kill()

def request_ok(request):
    logging.info(f"{request} OK - 200")

def request_bad(request, message):
    logging.error(f"{request} BAD - 400 {message}")

def request_unauthorized(request):
    logging.error(f"{request} UNAUTHORIZED - 401")

def send_unauthorized_lecturer_response(request: Request):
    logging.debug("Lecturer not authenticated to make this request")
    respond(request, False, "NOT_AUTHENTICATED")

"""
    Used for AUTHENTICATE_LECTURER and also any requests that a lecturer
    needs to be logged in to make. Such requests should have these parameters passed
    to them as part of the request data
"""
def get_lecturer_auth_details(request: Request, request_name, error_response_on_empty = True):
    params = request.args

    lecturer = None
    password = None

    if 'lecturer' in params:
        lecturer = params['lecturer']

    if 'password' in params:
        password = params['password']

    if not lecturer and error_response_on_empty:
        request_bad(request_name, "Required lecturer value not provided")
        respond(request, False, "You need to provide a lecturer in an AUTHENTICATE_LECTURER request")
        return
    elif not lecturer and not error_response_on_empty:
        return

    if not password and error_response_on_empty:
        request_bad(request_name, "Required password value not provided")
        respond(request, False, "You need to provide a password in an AUTHENTICATE_LECTURER request")
        return
    elif not password and not error_response_on_empty:
        return

    return lecturer, password


""" lecturer and password needs to be passed in with every request that involves lecturers so they'll
be the only ones able to access the files

    If checkCredentials is True, an error response is sent if lecturer or password is empty, else it
    is just treated as an authentication error
"""
def authenticate_lecturer(request: Request, request_name, checkCredentials = True):
    lecturer_details = get_lecturer_auth_details(request, request_name, checkCredentials)

    if lecturer_details is not None:
        lecturer = lecturer_details[0]
        password = lecturer_details[1]
        if lecturer is not None and password is not None:
            filepath = ROOTDIR + "/login_credentials.txt"
            logging.debug(f"Reading file {filepath}")
            with open(filepath, 'r') as f:
                for ln in f:
                    if ln.startswith(lecturer):
                        data = ln.split()
                        if check_encrypted_password(password, data[1]):
                            logging.debug(f"Lecturer {lecturer} authenticated")
                            return True
                        else:
                            logging.debug(f"Lecturer {lecturer} not authenticated")
                            return False

    return False

def processCommand(request: Request, command):
    commandUpper = command.upper()
    logging.debug(f"Command {commandUpper} received")

    if command in commands:
        command_handler = commands[command]
        command_handler.handleRequest(request)
    else:
        logging.error(f"Command: {commandUpper} is defined in const.FileServerCommands but the request has not been implemented in the server")
        respond(request, False, f"Command provided: {commandUpper} is valid, but the server does not have the rquest implemented")

def serveRequest(request: Request, addr):
    while True:
        try:
            request.receive()

            if not request.disconnected and not request.http_requested:
                command = request.command

                if not command:
                    logging.error("No command provided to server, sending error response")
                    respond(request, False, "A command needs to be provided to the server")
                else:
                    if command in FileServerCommands.VALID_COMMANDS:
                        processCommand(request, command)
                    else:
                        logging.error(f"Command {command} is not valid, sending error response")
                        respond(request, False, f"The command provided: {command} is not valid. Expected: {FileServerCommands.VALID_COMMANDS}")
            elif request.http_requested:
                logging.info("Server was accessed with a HTTP request. Information HTML page sent to browser")
                break
            else:
                logging.debug(f"{addr} disconnected")
                break
        except Exception as e:
            if not isinstance(e, BrokenPipeError):
                e = format_exc()
                logging.error(e)
                respond(request, False, f"An exception occurred: {e}")
            break

if __name__ == "__main__":
    logging.info(f"Starting handin_file_server on host {const.FILE_SERVER_HOST} and port {const.FILE_SERVER_PORT}")
    load_file_server_commands()
    print(f"Starting handin_file_server on host {const.FILE_SERVER_HOST} and port {const.FILE_SERVER_PORT}")
    signal.signal(signal.SIGINT, signal_handler)
    s = listenerSocket(const.FILE_ADDR)

    while True: # continuously loop through accepting any new connections that arrive
        conn, addr = acceptSocket(s)
        log_string = f"New connection to handin_file_server: {addr}"
        print(log_string)
        logging.info(log_string)
        request = Request(conn) # create the request object to parse the request made to the server

        t = threading.Thread(target=serveRequest, args=(request,addr))
        t.daemon = True
        t.start()

    s.close()
