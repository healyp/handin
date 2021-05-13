import socket
import ast
import re
import const

"""
    This file provides a means of messaging between a handin client and handin server using sockets.
    It is designed to use Request/Response architecture, i.e. a client sends a request and then waits
    for a response, processing that response accordingly.

    Any associated data is sent using key=value pairs. A request is a means of sending
    a command to the server to tell the server what request to serve, provided with the arguments required to serve
    that request.

    A response is a means of returning with True/False for success of the request, a message and optional Response
    data in key=value pairs

    The procedure for sending a request is as follows (the provided example is for authenticating a lecturer):
        Client side:
            s = connectedSocket(const.FILE_ADDR)
            args = {
                'lecturer': lecturer,
                'password': password
            }

            request = Request(s, FileServerCommands.AUTHENTICATE_LECTURER, args) # FileServerCommands is in const
            response = Response(s) # create the response object we will use to parse a response with

            request.send() # send the request to the server
            response.receive() # now wait for a response

        Server side:
            request = Request(conn) # conn is returned by acceptSocket
            request.receive() # receive the request

            if not request.disconnected:
                # request is valid

                command = request.command

                ## logic to check if command is valid

                if command == FileServerCommands.AUTHENTICATE_LECTURER:
                    checkCredentials(request)

            # in checkCredentials on successful auth
            response = Response(request.socket, True, "AUTHENTICATED") # conn is the socket returned by acceptedSocket
            response.send() # send the response which will be received by a corresponding response.receive method

            # arguments in a request can be accessed using request.args and it is a dict

        Client side after receive() returns:
            if not response.disconnected:
                # this is a valid response and didnt disconnect while waiting
                if (response.success == "True"):
                    if (response.message == "AUTHENTICATED"):
                        return True

                # other logic if success is not true

            # if data is returned by the request (it is a dict), it can be accessed with response.data

        The methods respond and request help simplify this. The server calls respond with the received
        request object and the response parameters (sucess, success_message, optional data) and the client calls
        request method and receives the parsed response object provided that the request did not get disconnected
"""

# Separator for all components of a request/response line
SEPARATOR = "&amp"
# Marks the end of a request/response line
END_OF_LINE = "DONE"
# Separator for key=value pairs
KEY_VALUE_SEPARATOR = ";"
# error message for when timeout error occurs
TIMEOUT_ERROR_MESSAGE = "There has been a timeout while waiting for a response from the file server. This is usually caused after an error on the server occurred or the request took too long (Try increasing response_timeout in conf.yaml). Please try again"
# string flag to return to indicate that html should be returned
SEND_HTML = "SEND HTML"
# the regex to look for in a http get request
HTTP_GET_REQUEST = r"GET\s+([^?\s]+)((?:[?&][^&\s]+)*)\s+(HTTP\/.*)"
# the regex to look for in a http post request
HTTP_POST_REQUEST = r"POST\s+([^?\s]+)((?:[?&][^&\s]+)*)\s+(HTTP\/.*)"
# the header to send back with the html page
HTTP_HEADER = "HTTP/1.1 200 OK\n\n"

"""Waits to retrieve a line of input from the socket until END_OF_LINE is encountered"""
def retrieve_input(socket):
    input = socket.recv(1024).decode()

    if not input:
        return ""
    else:
        if re.search(HTTP_GET_REQUEST, input) or re.search(HTTP_POST_REQUEST, input):
            return SEND_HTML
        else:
            while not input.endswith(END_OF_LINE):
                input += socket.recv(1024).decode()

                if not input:
                    return ""

            input = input[0:input.index(END_OF_LINE)]

        return input

"""From the provided string, this method parses it into key value pairs
   A key=value pair contains a key pointing to a value which will then be stored in
   the provided dict.

   Each key=value pair is separated by KEY_VALUE_SEPARATOR
"""
def parse_key_value_pairs(string, dict):
    splitArgs = string.split(KEY_VALUE_SEPARATOR)
    for i in splitArgs:
        if i != "":
            PATTERN = re.compile(r'''((?:[^="']|"[^"]*"|'[^']*')+)''') # this regex iensures that we don't split on = inside in quotation marks
            param = PATTERN.split(i)[1::2]
            key = param[0].strip()
            value = ""
            if len(param) > 1:
                value = param[1].strip()

            if value.startswith("[") and value.endswith("]"):
                # we have a list
                value = parse_string_to_list(value)
            elif value.startswith("{") and value.endswith("}"):
                # we have a dictionary
                value = parse_string_to_dict(value)

            dict[key] = value

"""
    Parses the provided arguments to a format suitable for a request/response
"""
def parse_args_to_request(args: dict):
    argsString = ""

    for key, value in args.items():
        argsString += f"{key}={value}{KEY_VALUE_SEPARATOR}"

    return argsString

"""
    Parses a string representation of a list that was returned from parse_list_to_string
"""
def parse_string_to_list(string):
    if not string.startswith("[") or not string.endswith("]"):
        raise MessagingError("parse_string_to_list called with a string that is an invalid representation of a list")
    else:
        return ast.literal_eval(string)


"""
    Parses a string representation of a dictionary that was returned from parse_dict_to_string
"""
def parse_string_to_dict(string):
    if not string.startswith("{") or not string.endswith("}"):
        raise MessagingError("parse_string_to_dict called with a string that is an invalid representation of a list")
    else:
        return ast.literal_eval(string)

"""
    This class represents a Request that can be made from a client to a server.
    It provides the means of providing a command and the arguments for that command as key=value pairs.

    The sending and receiving of a request is also handled by this class using the send and receive methods
    respectively. The client is expected to use the send method and server is to use the receive method
"""
class Request:
    """
        Create a Request with the socket that has been returned from a socket.accept() call,
        the command to use and the arguments to provide with it. A client using send is expected
        to provide a command and args. However, a server using receive does not since the receive
        method will parse these parameters from a sent request
    """
    def __init__(self, socket, command=None, args={}):
        self.socket = socket
        self.command = command
        self.args = args
        self.disconnected = False
        self.http_requested = False
        self.error = False
        self.error_message = ""

    """
        This method is to be called by the client to send the request to the server
    """
    def send(self):
        request = f"{self.command}{SEPARATOR}"
        args = parse_args_to_request(self.args)

        request += f"{args}{END_OF_LINE}"
        self.socket.sendall(bytes(request, 'utf-8'))

    def __sendHTML(self):
        self.http_requested = True
        html = HTTP_HEADER
        with open(const.FILE_HTML_LANDING, 'r') as file:
            html += file.read()
        self.socket.sendall(bytes(html, 'utf-8'))
        self.socket.close()

    """
        This method is to be called by the server to receive and parse a request that was sent with the send() method
        The parsed parameters can be accesed after this call returns using the command and args attributes
    """
    def receive(self):
        try:
            input = retrieve_input(self.socket)
            if input == SEND_HTML:
                self.__sendHTML()
                return

            self.disconnected = input == ""

            if self.disconnected:
                return
            split = input.split(SEPARATOR)

            length = len(split)
            if length == 0:
                raise MessagingError("No values passed to the request")
            elif length > 2:
                raise MessagingError("You can only provide a command and arguments")

            if length == 1:
                self.command = split[0].strip()
            else:
                self.command = split[0].strip()
                self.args = {}
                parse_key_value_pairs(split[1].strip(), self.args)
        except socket.timeout:
            raise MessagingError(TIMEOUT_ERROR_MESSAGE)
        except (BrokenPipeError, ConnectionResetError) as e:
            self.error = True
            self.error_message = f"{e}"
            self.disconnected = True

"""
    This class represents a Response that can be made from a server to a client.
    It is usually a response to a request.
    It provides the means of providing a True/False success value and a message and optionally response data as key=value pairs.

    The sending and receiving of a response is also handled by this class using the send and receive methods
    respectively. The client is expected to use the receive method and server is to use the send method
"""
class Response:
    """
        Create a Response with the socket that has been returned from a socket.accept() call (usually the same socket that has been passed into the Request
        so that you can respond to the request on the same socket),
        the True/False value, response message and optionally, the response data to provide with it. A server using send is expected
        to provide a success value and success message (and optionally data). However, a client using receive does not since the receive
        method will parse these parameters from a sent response sent using the send() method
    """
    def __init__(self, socket, success=None, message=None, data={}):
        self.socket = socket
        self.success = success
        self.message = message
        self.data = data
        self.disconnected = False
        self.error = False
        self.error_message = False

    """
        This method sends a response to a client that may have sent a request
    """
    def send(self):
        response = f"{self.success}{SEPARATOR}{self.message}"

        if (len(self.data) > 0):
            response += f"{SEPARATOR}"
            args = parse_args_to_request(self.data)

            response += f"{args}"

        response += END_OF_LINE
        try:
            self.socket.sendall(bytes(response, 'utf-8'))
        except (BrokenPipeError, ConnectionResetError) as e:
            self.error = True
            self.error_message = f"{e}"
            self.disconnected = True


    """
        This method receives a response that has been sent by a server using send()
        After this call returns, the values can be accessed using the success, message and data attributes of this class
    """
    def receive(self):
        try:
            input = retrieve_input(self.socket)
            if input == "":
                self.disconnected = True

            if self.disconnected:
                return
            split = input.split(SEPARATOR)

            length = len(split)
            if length < 2:
                raise MessagingError("A success variable and message needs to be provided")
            elif length > 3:
                raise MessagingError("Only success and message and optional data are the 3 parameters allowed in a response")

            self.success = split[0]
            self.message = split[1]

            if (length == 3):
                args = split[2].strip()
                self.data = {}
                parse_key_value_pairs(args, self.data)
        except socket.timeout:
            raise MessagingError(TIMEOUT_ERROR_MESSAGE)
        except (BrokenPipeError, ConnectionResetError) as e:
            self.error = True
            self.error_message = f"{e}"
            self.disconnected = True

"""
    This exception is raised by either a request or a response if any error occurs
"""
class MessagingError(Exception):
    pass

"""
    Retrieve a socket that will listen out for connections
"""
def listenerSocket(addr):
    s = socket.socket()
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(addr)
    s.listen()

    return s

"""
    Accepts a socket and returns the accepted socket and the address
"""
def acceptSocket(socket):
    conn, addr = socket.accept()
    return conn, addr

"""
    Retrieve a socket connected to the provided address
"""
def connectedSocket(addr):
    s = socket.socket()
    s.settimeout(const.RESPONSE_TIMEOUT)
    s.connect(addr)

    return s

"""
    Respond to a request with request success, a message to respond with and an
    optional dictionary of response data
"""
def respond(request: Request, success: bool, success_message: str, response_data: dict = {}):
    response = Response(request.socket, success, success_message, response_data)
    response.send()

"""
    This method, sends the provided request, waits for the response object and returns
    the received response. If request.disconnected is true after the request is sent,
    this method will return None
"""
def request(request: Request) -> Response:
    response = Response(request.socket)
    request.send()

    if not request.disconnected:
        response.receive()
        return response
    else:
        return None
