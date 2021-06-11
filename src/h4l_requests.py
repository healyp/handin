import logging
import sys
import os

from handin_messaging import Request, connectedSocket, MessagingError, request
import const
from const import FileServerCommands
from PyQt5 import QtWidgets

"""
    This module contains methods to help the h4l.py script make requests.

    The methods return in the format:
        param1, param2, .... , paramN, error

    error is a True/False value. If True is returned an error occurred and error dialog displayed. If
    False is returned, it means no error occurred.

    Note that some methods dont return any parameters (or just 1 etc), so if none are returned, just the error
    variable will be returned
"""

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(asctime)s %(message)s')

s = None
lecturer = ""
password = ""

class ErrorDialog(QtWidgets.QErrorMessage):
    def __init__(self, closeOnOk = False):
        super().__init__()
        self.closeOnOk = closeOnOk

    def show(self):
        self.exec()
        if self.closeOnOk:
            sys.exit(0)

    def closeEvent(self, event):
        if self.closeOnOk:
            sys.exit(0)

def doError(message, closeOnOk = False):
    error_dialog = ErrorDialog(closeOnOk)
    error_dialog.showMessage(message)
    error_dialog.show()

def setSocket(initialLaunch = False):
    global s
    try:
        if s is None:
            s = connectedSocket(const.FILE_ADDR)
            logging.info(f"Connected to handin_file_server on {const.FILE_ADDR}")

        return True
    except Exception as e:
        logging.error(f"Failed to connect to handin_file_server with error: {e}")
        doError(f"Failed to connect to Handin File Server, please try again later. (Is handin_file_server running on the following machine: Host: {const.FILE_SERVER_HOST} Port: {const.FILE_SERVER_PORT}?) Error: {e}", initialLaunch)
        return False

def disconnect():
    global s

    if s is not None:
        s.close()
        logging.info("Disconnected from handin_file_server")

def getModuleCodes() -> tuple[list, bool]:
    global s
    try:
        if setSocket():
            args = {}
            addLecturerAuthDetails(args)
            args[FileServerCommands.ModuleInfoRequestCodes.CODE] = FileServerCommands.ModuleInfoRequestCodes.MODULE_CODES

            response = request(Request(s, FileServerCommands.MODULE_INFO, args))

            if response is not None:
                if not response.disconnected:
                    if response.success == "True":
                        return response.data['module_codes'], False
                    else:
                        error = True
                        doError(f"A server error occurred retrieving module codes: {response.message}")
                else:
                    s = None
                    error = True
                    if response.error:
                        logging.error(f"Response Error: {response.error_message}")
            else:
                s = None
                error = True
                logging.error(f"Request Error")
        else:
            error = True
    except MessagingError as m:
        s = None
        doError(f"{m}")
        error = True

    return [], error

def getModuleAssignments(module_code) -> tuple[list, bool]:
    global s
    try:
        if setSocket():
            args = {}
            addLecturerAuthDetails(args)
            args[FileServerCommands.ModuleInfoRequestCodes.CODE] = FileServerCommands.ModuleInfoRequestCodes.MODULE_ASSIGNMENTS
            args['module_code'] = module_code

            response = request(Request(s, FileServerCommands.MODULE_INFO, args))

            if response is not None:
                if not response.disconnected:
                    if response.success == "True":
                        return response.data['module_assignments'], False
                    else:
                        error = True
                        doError(f"A server error occurred retrieving assignments: {response.message}")
                else:
                    s = None
                    error = True
                    if response.error:
                        logging.error(f"Response Error: {response.error_message}")
            else:
                s = None
                error = True
                logging.error(f"Request Error")
        else:
            error = True
    except MessagingError as m:
        s = None
        doError(f"{m}")
        error = True

    return [], error

def get_all_test_items(module_code, assignment) -> tuple[list, bool]:
    global s
    try:
        if setSocket():
            args = {}
            addLecturerAuthDetails(args)
            args[FileServerCommands.ModuleInfoRequestCodes.CODE] = FileServerCommands.ModuleInfoRequestCodes.MODULE_TEST_ITEMS
            args['module_code'] = module_code
            args['assignment'] = assignment

            response = request(Request(s, FileServerCommands.MODULE_INFO, args))

            if response is not None:
                if not response.disconnected:
                    if response.success == "True":
                        return response.data['test_items'], False
                    else:
                        error = True
                        doError(f"A server error occurred retrieving test items: {response.message}")
                else:
                    s = None
                    error = True
                    if response.error:
                        logging.error(f"Response Error: {response.error_message}")
            else:
                s = None
                error = True
                logging.error(f"Request Error")
        else:
            error = True
    except MessagingError as m:
        s = None
        doError(f"{m}")
        error = True

    return [], error

def get_all_student_ids(module_code) -> tuple[list, bool]:
    global s
    try:
        if setSocket():
            args = {}
            addLecturerAuthDetails(args)
            args[FileServerCommands.ModuleInfoRequestCodes.CODE] = FileServerCommands.ModuleInfoRequestCodes.MODULE_STUDENT_IDS
            args['module_code'] = module_code

            response = request(Request(s, FileServerCommands.MODULE_INFO, args))

            if response is not None:
                if not response.disconnected:
                    if response.success == "True":
                        return response.data['student_ids'], False
                    else:
                        error = True
                        doError(f"A server error occurred retrieving student IDs: {response.message}")
                else:
                    s = None
                    error = True
                    if response.error:
                        logging.error(f"Response Error: {response.error_message}")
            else:
                s = None
                error = True
                logging.error(f"Request Error")
        else:
            error = True
    except MessagingError as m:
        s = None
        doError(f"{m}")
        error = True

    return [], error

def addLecturerAuthDetails(request_data: dict):
    if lecturer != "" and password != "":
        request_data['lecturer'] = lecturer
        request_data['password'] = password

def getLecturerModules(lecturer):
    global s
    try:
        if setSocket():
            args = {}
            addLecturerAuthDetails(args)

            response = request(Request(s, FileServerCommands.GET_LECTURER_MODULES, args))

            if response is not None:
                if not response.disconnected:
                    if response.success == "True":
                        modules = []
                        for value in response.data['modules']:
                            modules.append(value)

                        return modules, False
                    else:
                        error = True
                        doError(f"A server error occurred retrieving lecturer modules: {response.message}")
                else:
                    s = None
                    error = True
                    if response.error:
                        logging.error(f"Response Error: {response.error_message}")
            else:
                s = None
                error = True
                logging.error(f"Request Error")
        else:
            error = True
    except MessagingError as m:
        s = None
        doError(f"{m}")
        error = True

    return {}, error

def checkCredentials(lect, passw):
    global s, lecturer, password
    try:
        if setSocket():
            args = {
                'lecturer': lect,
                'password': passw
            }

            response = request(Request(s, FileServerCommands.AUTHENTICATE_LECTURER, args))

            if response is not None:
                if not response.disconnected:
                    if response.success == "True":
                        if response.message == "AUTHENTICATED":
                            lecturer = lect
                            password = passw
                            return True, False
                        elif response.message == "NOT_AUTHENTICATED":
                            return False, False # Return false for login_error parameter as this failure is a credential error, not socket error
                        else:
                            login_error = True
                            doError(f"A server error occurred checking credentials: {response.message}")
                    else:
                        login_error = True
                        doError(f"A server error occurred checking credentials: {response.message}")
                else:
                    s = None
                    login_error = True
                    if response.error:
                        logging.error(f"Response Error: {response.error_message}")
            else:
                s = None
                login_error = True
                logging.error(f"Request Error")
        else:
            login_error = True
    except MessagingError as m:
        s = None
        doError(f"{m}")
        login_error = True

    return False, login_error

def alertMacAddress(lecturer, mac):
    global alertMacAddressStr, s
    try:
        if setSocket():
            args = {}
            addLecturerAuthDetails(args)
            args['mac'] = mac

            response = request(Request(s, FileServerCommands.ALERT_MAC_ADDRESS, args))

            if response is not None:
                if not response.disconnected:
                    if response.success == "True":
                        data = response.data

                        if 'alertMacAddress' in data:
                            alertMacAddressStr = data['alertMacAddress']

                        alert = False
                        if 'alert' in data:
                            alert = data['alert']

                        alert = alert.upper()

                        if alert == "TRUE":
                            alert = True
                        else:
                            alert = False

                        return alert, False
                    else:
                        error = True
                        doError(f"A server error occurred checking if MAC address should be alerted: {response.message}")
                else:
                    s = None
                    error = True
                    if response.error:
                        logging.error(f"Response Error: {response.error_message}")
            else:
                s = None
                error = True
                logging.error(f"Request Error")
        else:
            error = True
    except MessagingError as m:
        s = None
        doError(f"{m}")
        error = True

    return False, error

def trustMacAddress(lecturer, trust):
    global s
    try:
        if setSocket():
            args = {}
            addLecturerAuthDetails(args)
            args['mac'] = alertMacAddressStr
            args['trust'] = trust

            response = request(Request(s, FileServerCommands.TRUST_MAC_ADDRESS, args))

            if response is not None:
                if not response.disconnected:
                    if response.success == "True":
                        return False
                    else:
                        error = True
                        doError(f"A server error occurred trusting MAC address: {response.message}")
                else:
                    s = None
                    error = True
                    if response.error:
                        logging.error(f"Response Error: {response.error_message}")
            else:
                s = None
                error = True
                logging.error(f"Request Error")
        else:
            error = True
    except MessagingError as m:
        s = None
        doError(f"{m}")
        error = True

    return error

def get_vars(module, week_number, student_id):
    global s
    try:
        if setSocket():
            args = {
                'module': module,
                'week_number': week_number,
                'student_id': student_id
            }

            response = request(Request(s, FileServerCommands.GET_VARS, args))

            if response is not None:
                if not response.disconnected:
                    if response.success == "True":
                        return response.data['vars'], False
                    else:
                        error = True
                        doError(f"A server error occurred retrieving vars: {response.message}")
                else:
                    s = None
                    error = True
                    if response.error:
                        logging.error(f"Response Error: {response.error_message}")
            else:
                s = None
                error = True
                logging.error(f"Request Error")
        else:
            error = True
    except MessagingError as m:
        s = None
        doError(f"{m}")
        error = True

    return {}, error

def checkModuleExists(module):
    global s
    try:
        if setSocket():
            args = {
                FileServerCommands.CheckExistsRequestCodes.CODE: FileServerCommands.CheckExistsRequestCodes.MODULE_EXISTS,
                'module': module
            }

            response = request(Request(s, FileServerCommands.CHECK_EXISTS, args))

            if response is not None:
                if not response.disconnected:
                    if response.success == "True":
                        exists = response.data['exists']

                        if exists == "True":
                            exists = True
                        else:
                            exists = False

                        return exists, False
                    else:
                        error = True
                        doError(f"A server error occurred checking if module exists: {response.message}")
                else:
                    s = None
                    error = True
                    if response.error:
                        logging.error(f"Response Error: {response.error_message}")
            else:
                s = None
                error = True
                logging.error(f"Request Error")

        else:
            error = True
    except MessagingError as m:
        s = None
        doError(f"{m}")
        error = True

    return False, error

def checkAssignmentExists(module, academic_year, assignment):
    global s
    try:
        if setSocket():
            args = {
                FileServerCommands.CheckExistsRequestCodes.CODE: FileServerCommands.CheckExistsRequestCodes.ASSIGNMENT_EXISTS,
                'module': module,
                'academic_year': academic_year,
                'assignment': assignment
            }

            response = request(Request(s, FileServerCommands.CHECK_EXISTS, args))

            if response is not None:
                if not response.disconnected:
                    if response.success == "True":
                        exists = response.data['exists']

                        if exists == "True":
                            exists = True
                        else:
                            exists = False

                        return exists, False
                    else:
                        error = True
                        doError(f"A server error occurred checking if assignment exists: {response.message}")
                else:
                    s = None
                    error = True
                    if response.error:
                        logging.error(f"Response Error: {response.error_message}")
            else:
                s = None
                error = True
                logging.error(f"Request Error")

        else:
            error = True
    except MessagingError as m:
        s = None
        doError(f"{m}")
        error = True

    return False, error

def createAssignmentDirectory(module, assignment_name):
    global s
    try:
        if setSocket():
            args = {
                'module': module,
                'assignment': assignment_name
            }

            response = request(Request(s, FileServerCommands.CREATE_ASSIGNMENT_DIRECTORY, args))

            if response is not None:
                if not response.disconnected:
                    if response.success == "True":
                        return response.data['params_path'], False
                    else:
                        error = True
                        doError(f"A server error occurred checking if assignment exists: {response.message}")
                else:
                    s = None
                    error = True
                    if response.error:
                        logging.error(f"Response Error: {response.error_message}")
            else:
                s = None
                error = True
                logging.error(f"Request Error")

        else:
            error = True
    except MessagingError as m:
        s = None
        doError(f"{m}")
        error = True

    return "", error

def updateParamsFile(params_file, params):
    global s
    try:
        if setSocket():
            args = {
                'params_file': params_file,
                'params': params
            }

            response = request(Request(s, FileServerCommands.UPDATE_PARAMS_FILE, args))

            if response is not None:
                if not response.disconnected:
                    if response.success == "True":
                        return False
                    else:
                        error = True
                        doError(f"A server error occurred updating params file: {response.message}")
                else:
                    s = None
                    error = True
                    if response.error:
                        logging.error(f"Response Error: {response.error_message}")
            else:
                s = None
                error = True
                logging.error(f"Request Error")
        else:
            error = True
    except MessagingError as m:
        s = None
        doError(f"{m}")
        error = True

    return error

def createDefinitionsFile(module, academic_year):
    global s
    try:
        if setSocket():
            args = {
                'module': module,
                'academic_year': academic_year
            }

            response = request(Request(s, FileServerCommands.CREATE_DEFINITIONS_FILE, args))

            if response is not None:
                if not response.disconnected:
                    if response.success == "True":
                        return response.data['definitions_path'], False
                    else:
                        error = True
                        doError(f"A server error occurred creating definitions file: {response.message}")
                else:
                    s = None
                    error = True
                    if response.error:
                        logging.error(f"Response Error: {response.error_message}")
            else:
                s = None
                error = True
                logging.error(f"Request Error")
        else:
            error = True
    except MessagingError as m:
        s = None
        doError(f"{m}")
        error = True

    return "", error

def updateDefinitionsFile(definitions_file, definitions):
    global s
    try:
        if setSocket():
            args = {
                'definitions_file': definitions_file,
                'definitions': definitions
            }

            response = request(Request(s, FileServerCommands.UPDATE_DEFINITIONS_FILE, args))

            if response is not None:
                if not response.disconnected:
                    if response.success == "True":
                        return False
                    else:
                        error = True
                        doError(f"A server error occurred updating definitions file: {response.message}")
                else:
                    s = None
                    error = True
                    if response.error:
                        logging.error(f"Response Error: {response.error_message}")
            else:
                s = None
                error = True
                logging.error(f"Request Error")
        else:
            error = True
    except MessagingError as m:
        s = None
        doError(f"{m}")
        error = True

    return error

def getDefinitions(module, academic_year):
    global s
    try:
        if setSocket():
            args = {
                'module': module,
                'academic_year': academic_year
            }

            response = request(Request(s, FileServerCommands.GET_DEFINITIONS_FILE, args))

            if response is not None:
                if not response.disconnected:
                    if response.success == "True":
                        return response.data['definitions'], False
                    else:
                        error = True
                        doError(f"A server error occurred retrieving definitions: {response.message}")
                else:
                    s = None
                    error = True
                    if response.error:
                        logging.error(f"Response Error: {response.error_message}")
            else:
                s = None
                error = True
                logging.error(f"Request Error")
        else:
            error = True
    except MessagingError as m:
        s = None
        doError(f"{m}")
        error = True

    return {}, error

def getParams(module, assignment):
    global s
    try:
        if setSocket():
            args = {
                'module': module,
                'assignment': assignment
            }

            response = request(Request(s, FileServerCommands.GET_PARAMS, args))

            if response is not None:
                if not response.disconnected:
                    if response.success == "True":
                        return response.data['content'], response.data['filename'], False
                    else:
                        error = True
                        doError(f"A server error occurred retrieving params: {response.message}")
                else:
                    s = None
                    error = True
                    if response.error:
                        logging.error(f"Response Error: {response.error_message}")
            else:
                s = None
                error = True
                logging.error(f"Request Error")
        else:
            error = True
    except MessagingError as m:
        s = None
        doError(f"{m}")
        error = True

    return "", "", error

def cloneAssignment(module, assignment, content):
    global s
    try:
        if setSocket():
            args = {
                'module': module,
                'assignment': assignment,
                'content': content
            }

            response = request(Request(s, FileServerCommands.CLONE_ASSIGNMENT, args))

            if response is not None:
                if not response.disconnected:
                    if response.success == "True":
                        return response.data, False
                    else:
                        error = True
                        doError(f"Error: {response.message}")
                else:
                    s = None
                    error = True
                    if response.error:
                        logging.error(f"Response Error: {response.error_message}")
            else:
                s = None
                error = True
                logging.error(f"Request Error")
        else:
            error = True
    except MessagingError as m:
        s = None
        doError(f"{m}")
        error = True

    return "", error

def deleteAssignment(module, assignment):
    global s
    try:
        if setSocket():
            args = {
                'module': module,
                'assignment': assignment,
            }

            response = request(Request(s, FileServerCommands.DELETE_ASSIGNMENT, args))

            if response is not None:
                if not response.disconnected:
                    if response.success == "True":
                        return False
                    else:
                        error = True
                        doError(f"Server Error: {response.message}")
                else:
                    s = None
                    error = True
                    if response.error:
                        logging.error(f"Response Error: {response.error_message}")
            else:
                s = None
                error = True
                logging.error(f"Request Error")
        else:
            error = True
    except MessagingError as m:
        s = None
        doError(f"{m}")
        error = True

    return error

def readFileContents(file):
    error = False
    contents = ""

    if os.path.isdir(file):
        doError(f"{file} is a directory")
        error = True
    else:
        try:
            contents = ""
            with open(file, 'r') as file1:
                contents = file1.read()
        except FileNotFoundError:
            doError(f"{file} does not exist")
            error = True

    return contents, error

def uploadFile(file, destination_path):
    global s
    try:
        if setSocket():
            contents, error = readFileContents(file)

            if not error:
                args = {
                    'contents': contents,
                    'destination': destination_path
                }

                response = request(Request(s, FileServerCommands.UPLOAD_FILE, args))

                if response is not None:
                    if not response.disconnected:
                        if response.success == "True":
                            return False
                        else:
                            error = True
                            doError(f"{response.message}")
                    else:
                        s = None
                        error = True
                        if response.error:
                            logging.error(f"Response Error: {response.error_message}")
                else:
                    s = None
                    error = True
                    logging.error(f"Request Error")
        else:
            error = True
    except MessagingError as m:
        s = None
        doError(f"{m}")
        error = True

    return error

def generateAssignmentCSV(module, assignment = 'all') -> bool:
    global s
    try:
        error = False
        if setSocket():
            args = {
                'module': module,
                'assignment': assignment # for now, we only support all
            }

            response = request(Request(s, FileServerCommands.GENERATE_ASSIGNMENT_CSV, args))

            if response is not None:
                if not response.disconnected:
                    if response.success == "True":
                        return False
                    else:
                        error = True
                        doError(f"{response.message}")
                else:
                    s = None
                    error = True
                    if response.error:
                        logging.error(f"Response Error: {response.error_message}")
            else:
                s = None
                error = True
                logging.error(f"Request Error")
    except MessagingError as m:
        s = None
        doError(f"{m}")
        error = True

    return error

def updateExceptionsFile(module, assignment, student_id, exceptions):
    global s
    try:
        if setSocket():
            args = {
                'module': module,
                'assignment': assignment,
                'student_id': student_id,
                'exceptions': exceptions
            }
            addLecturerAuthDetails(args)

            response = request(Request(s, FileServerCommands.UPDATE_EXCEPTIONS_FILE, args))

            if response is not None:
                if not response.disconnected:
                    if response.success == "True":
                        return False
                    else:
                        error = True
                        doError(f"{response.message}")
                else:
                    s = None
                    error = True
                    if response.error:
                        logging.error(f"Response Error: {response.error_message}")
            else:
                s = None
                error = True
                logging.error(f"Request Error")
        else:
            error = True
    except MessagingError as m:
        s = None
        doError(f"{m}")
        error = True

    return error

def getExceptionsFile(module, assignment):
    global s
    try:
        if setSocket():
            args = {
                'module': module,
                'assignment': assignment
            }
            addLecturerAuthDetails(args)

            response = request(Request(s, FileServerCommands.GET_EXCEPTIONS_FILE, args))

            if response is not None:
                if not response.disconnected:
                    if response.success == "True":
                        return response.data['exceptions'], False
                    else:
                        error = True
                        doError(f"{response.message}")
                else:
                    s = None
                    error = True
                    if response.error:
                        logging.error(f"Response Error: {response.error_message}")
            else:
                s = None
                error = True
                logging.error(f"Request Error")
        else:
            error = True
    except MessagingError as m:
        s = None
        doError(f"{m}")
        error = True

    return {}, error

def deleteException(module, assignment, student_id):
    global s
    try:
        if setSocket():
            args = {
                'module': module,
                'assignment': assignment,
                'student_id': student_id
            }
            addLecturerAuthDetails(args)

            response = request(Request(s, FileServerCommands.DELETE_EXCEPTION, args))

            if response is not None:
                if not response.disconnected:
                    if response.success == "True":
                        return False
                    else:
                        error = True
                        doError(f"{response.message}")
                else:
                    s = None
                    error = True
                    if response.error:
                        logging.error(f"Response Error: {response.error_message}")
            else:
                s = None
                error = True
                logging.error(f"Request Error")
        else:
            error = True
    except MessagingError as m:
        s = None
        doError(f"{m}")
        error = True

    return error