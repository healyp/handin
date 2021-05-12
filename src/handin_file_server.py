import const
import yaml
import sys
import os
import signal
import logging
import threading
from handin_messaging import Request, listenerSocket, acceptSocket, respond
from traceback import format_exc
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

def checkCredentials(request: Request):
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

def alertMacAddress(request: Request):
    if (authenticate_lecturer(request, "ALERT_MAC_ADDRESS", False)):
        params = request.args
        mac = None
        if "mac" in params:
            mac = params['mac']

        if mac is None:
            request_bad("ALERT_MAC_ADDRESS", "Required mac value not provided")
            respond(request, False, "You need to provide a mac in an ALERT_MAC_ADDRESS request")
            return

        lecturer = params['lecturer']

        response_data = {}
        filepath = ROOTDIR + "/users/" + lecturer + "/mac_addresses.txt"
        logging.debug(f"Reading file {filepath}")
        alert = False
        line_found = False
        if(os.path.exists(filepath)):
            with open(filepath, 'r+') as f:
                lines = f.readlines()

                if(lines[0].startswith(mac)): #first mac address they used
                    line_found = True
                    for i, line in enumerate(lines):
                        data = line.split()
                        temp = data[1]
                        if(temp == "true"):
                            alert = True
                            alertMacAddress = data[0]
                            response_data['alertMacAddress'] = alertMacAddress
                else:
                    for i, line in enumerate(lines):
                        if(line.startswith(mac)):
                            line_found = True
                if(not line_found):
                    newMac = mac + " true\n"
                    lines.append(newMac)
                f.seek(0)
                for line in lines:
                    f.write(line)
        else:
            with open(filepath, 'a') as f:
                line = mac + " false\n"
                f.write(line)

        response_data['alert'] = alert

        request_ok("ALERT_MAC_ADDRESS")
        respond(request, True, "ALERT_MAC_ADDRESS Successful", response_data)
    else:
        request_unauthorized("ALERT_MAC_ADDRESS")
        send_unauthorized_lecturer_response(request)

def trustMacAddress(request: Request):
    if (authenticate_lecturer(request, "TRUST_MAC_ADDRESS", False)):
        params = request.args
        mac = None

        if "mac" in params:
            mac = params['mac']

        if mac is None:
            request_bad("TRUST_MAC_ADDRESS", "Required mac value not provided")
            respond(request, False, "You need to provide a mac in an TRUST_MAC_ADDRESS request")
            return

        trust = "false"

        if "trust" in params:
            trust = params['trust']
        else:
            logging.warning("trust value not provided in TRUST_MAC_ADDRESS request, defaulting to \"false\"")

        lecturer = params['lecturer']

        response_data = {}
        filepath = ROOTDIR + "/users/" + lecturer + "/mac_addresses.txt"
        logging.debug(f"Reading file {filepath}")
        with open(filepath, 'r+') as f:
            lines = f.readlines()
            for i, line in enumerate(lines):
                if line.startswith(mac):
                    if(trust == "true"):
                        data = line.split()
                        lines[i] = data[0] + " false\n"
            f.seek(0)
            if(trust == "false"):
                for line in lines:
                    if(not line.startswith(mac)):
                        f.write(line)
            else:
                for line in lines:
                    f.write(line)
            f.truncate()

        request_ok("TRUST_MAC_ADDRESS")
        respond(request, True, "TRUST_MAC_ADDRESS successful")
    else:
        request_unauthorized("TRUST_MAC_ADDRESS")
        send_unauthorized_lecturer_response(request)

def getLecturerModules(request: Request):
    if (authenticate_lecturer(request, "GET_LECTURER_MODULES", False)):
        params = request.args
        lecturer = params['lecturer']

        filepath = ROOTDIR + "/access_rights.txt"
        logging.debug(f"Reading file {filepath}")
        modules = []
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

def getModuleCodes(request: Request):
    list = [name for name in os.listdir(ROOTDIR) if re.match(ModCodeRE, name)]
    logging.debug(f"Module Codes found: {list}")
    response_data = {
        'module_codes': list
    }

    request_ok("MODULE_INFO: MODULE_CODES")
    respond(request, True, "MODULE_INFO: MODULE_CODES Successful", response_data)

def getModuleAssignments(request: Request):
    params = request.args

    module_code = None
    if 'module_code' in params:
        module_code = params['module_code']

    if not module_code:
        request_bad("MODULE_INFO: MODULE_ASSIGNMENTS", "Mandatory module_code parameter not provided")
        respond(request, False, "You need to provide a module_code parameter")
        return

    path = ROOTDIR + "/" + module_code + "/curr/assignments"
    logging.debug(f"Using path {path}")

    list = []
    if os.path.isdir(path):
        list = [name for name in os.listdir(path)]
        logging.debug(f"Assignments found: {list} for module {module_code}")
    else:
        logging.debug(f"Path {path} does not exist as a directory")

    response_data = {
        'module_assignments': list
    }

    request_ok("MODULE_INFO: MODULE_ASSIGNMENTS")
    respond(request, True, "MODULE_INFO: MODULE_ASSIGNMENTS Successful", response_data)

def getModuleTestItems(request: Request):
    params = request.args

    module_code = None
    week_number = None

    if 'module_code' in params:
        module_code = params['module_code']

    if not module_code:
        request_bad("MODULE_INFO: MODULE_TEST_ITEMS", "Mandatory module_code parameter not provided")
        respond(request, False, "You need to provide a module_code parameter")
        return

    if 'week_number' in params:
        week_number = params['week_number']

    if not week_number:
        request_bad("MODULE_INFO: MODULE_TEST_ITEMS", "Mandatory week_number parameter not provided")
        respond(request, False, "You need to provide a week_number parameter")
        return

    params_filepath = const.get_params_file_path(module_code, week_number)
    logging.debug(f"Using filepath {params_filepath}")

    list = []

    if os.path.isfile(params_filepath):
        with open(params_filepath, 'r') as stream:
            data: dict = yaml.safe_load(stream)

        list = [item for item in data["tests"].keys()]
    else:
        logging.debug(f"File {params_filepath} does not exist")

    logging.debug(f"Found test items: {list} for module {module_code} for week {week_number}")
    response_data = {
        'test_items': list
    }

    request_ok("MODULE_INFO: MODULE_TEST_ITEMS")
    respond(request, True, "MODULE_INFO: MODULE_TEST_ITEMS Successful", response_data)

def getModuleStudentIds(request: Request):
    params = request.args
    module_code = None

    if 'module_code' in params:
        module_code = params['module_code']

    if not module_code:
        request_bad("MODULE_INFO: MODULE_STUDENT_IDS", "Mandatory module_code parameter not provided")
        respond(request, False, "You need to provide a module_code parameter")
        return

    params_filepath = const.get_class_list_file_path(module_code)
    logging.debug(f"Using filepath {params_filepath}")

    if os.path.isfile(params_filepath):
        with open(params_filepath, 'r') as f:
            content = f.readlines()
            content = [x.strip() for x in content]
    else:
        logging.debug(f"File {params_filepath} does not exist")
        content = []

    logging.debug(f"Found student IDs: {content} for module {module_code}")
    response_data = {
        'student_ids': content
    }

    request_ok("MODULE_INFO: MODULE_STUDENT_IDS")
    respond(request, True, "MODULE_INFO: MODULE_STUDENT_IDS Successful", response_data)

def processModuleInfo(request: Request):
    if (authenticate_lecturer(request, "MODULE_INFO", False)):
        params = request.args
        code = None

        if FileServerCommands.ModuleInfoRequestCodes.CODE in params:
            code = params[FileServerCommands.ModuleInfoRequestCodes.CODE]

        if code is None:
            log = f"{FileServerCommands.ModuleInfoRequestCodes.CODE} is mandatory for a MODULE_INFO request but was not provided"
            request_bad("MODULE_INFO", log)
            respond(request, False, log)
            return
        elif not FileServerCommands.ModuleInfoRequestCodes.validateCode(code):
            log = f"The code {code} provided is not valid for MODULE_INFO. {FileServerCommands.ModuleInfoRequestCodes.VALID_CODES} expected"
            request_bad("MODULE_INFO", log)
            respond(request, False, log)
            return

        if code == FileServerCommands.ModuleInfoRequestCodes.MODULE_CODES:
            getModuleCodes(request)
        elif code == FileServerCommands.ModuleInfoRequestCodes.MODULE_ASSIGNMENTS:
            getModuleAssignments(request)
        elif code == FileServerCommands.ModuleInfoRequestCodes.MODULE_TEST_ITEMS:
            getModuleTestItems(request)
        elif code == FileServerCommands.ModuleInfoRequestCodes.MODULE_STUDENT_IDS:
            getModuleStudentIds(request)
    else:
        request_unauthorized("MODULE_INFO")
        send_unauthorized_lecturer_response(request)

def getVarsParameters(request: Request):
    params = request.args

    module = None
    week_number = None
    student_id = None

    if 'module' in params:
        module = params['module']

    if 'week_number' in params:
        week_number = params['week_number']

    if 'student_id' in params:
        student_id = params['student_id']

    log_message = ""
    error_message = ""
    send_error = False

    if not module:
        log_message = "Mandatory module parameter not provided"
        error_message = "You need to provide a module to this request"
        send_error = True
    elif not week_number:
        log_message = "Mandatory week_number parameter not provided"
        error_message = "You need to provide a week_number to this request"
        send_error = True
    elif not student_id:
        log_message = "Mandatory student_id parameter not provided"
        error_message = "You need to provide a student_id to this request"
        send_error = True

    if send_error:
        request_bad("GET_VARS", log_message)
        respond(request, False, error_message)
        return None
    else:
        return module, week_number, student_id

def getVars(request: Request):
    params = getVarsParameters(request)

    if params is not None:
        module, week_number, student_id = params
        vars_filepath = const.get_vars_file_path(module, week_number, student_id)
        logging.debug(f"Using filepath {vars_filepath}")

        vars = {}
        if os.path.isfile(vars_filepath):
            with open(vars_filepath, 'r') as stream:
                vars: dict = yaml.safe_load(stream)
        else:
            logging.debug(f"File {vars_filepath} does not exist")

        response_data = {
            'vars': vars,
            'test': 'succeeded'
        }

        request_ok("GET_VARS")
        respond(request, True, "GET_VARS successful", response_data)

def checkWeekExists(request: Request):
    params = request.args

    module = None
    week_number = None

    if 'module' in params:
        module = params['module']

    if 'week_number' in params:
        week_number = params['week_number']

    log_message = ""
    error_message = ""
    showError = False
    if not module:
        log_message = "Mandatory module parameter not provided"
        error_message = "You need to provide a module parameter"
        showError = True
    elif not week_number:
        log_message = "Mandatory week_number parameter not provided"
        error_message = "You need to provide a week_number parameter"
        showError = True

    if showError:
        request_bad("CHECK_EXISTS: WEEK_EXISTS", log_message)
        respond(request, False, error_message)
    else:
        logging.debug(f"Checking if week {week_number} exists for module {module}")
        exists = const.check_if_week_exists(module, week_number)
        response_data = {
            'exists': exists
        }

        request_ok("CHECK_EXISTS: WEEK_EXISTS")
        respond(request, True, "CHECK_EXISTS: WEEK_EXISTS successful", response_data)

def checkModuleExists(request: Request):
    params = request.args

    module = None

    if 'module' in params:
        module = params['module']

    if not module:
        request_bad("CHECK_EXISTS: MODULE_EXISTS", "Mandatory module parameter not provided")
        respond(request, False, "You need to provide a module parameter")
    else:
        logging.debug(f"Checking if module {module} exists")
        exists = const.check_if_module_exists(module)
        response_data = {
            'exists': exists
        }

        request_ok("CHECK_EXISTS: MODULE_EXISTS")
        respond(request, True, "CHECK_EXISTS: MODULE_EXISTS successful", response_data)

def checkAssignmentExists(request: Request):
    params = request,args

    module = None
    academic_year = None
    assignment = None

    log_message = ""
    error_message = ""
    showError = False

    if 'module' in params:
        module = params['module']

    if 'academic_year' in params:
        academic_year = params['academic_year']

    if 'assignment' in params:
        assignment = params['assignment']

    if not module:
        log_message = "Mandatory module parameter not provided"
        error_message = "You need to provide a module parameter"
        showError = True
    elif not academic_year:
        log_message = "Mandatory academic_year parameter not provided"
        error_message = "You need to provide an academic_year parameter"
        showError = True
    elif not assignment:
        log_message = "Mandatory assignment parameter not provided"
        error_message = "You need to provide an assignment parameter"
        showError = True

    if showError:
        request_bad("CHECK_EXISTS: ASSIGNMENT_EXISTS", log_message)
        respond(request, False, error_message)
    else:
        logging.debug(f"Checking if assignment {assignment} exists for module {module} and academic year {academic_year}")
        exists = const.check_if_ass_exists(module, academic_year, assignment)
        response_data = {
            'exists': exists
        }

        request_ok("CHECK_EXISTS: ASSIGNMENT_EXISTS")
        respond(request, True, "CHECK_EXISTS: ASSIGNMENT_EXISTS successful", response_data)

def checkExistence(request: Request):
    params = request.args
    code = None

    if FileServerCommands.CheckExistsRequestCodes.CODE in params:
        code = params[FileServerCommands.CheckExistsRequestCodes.CODE]

    if code is None:
        log = f"{FileServerCommands.CheckExistsRequestCodes.CODE} is mandatory for a CHECK_EXISTS request but was not provided"
        request_bad("CHECK_EXISTS", log)
        respond(request, False, log)
        return
    elif not FileServerCommands.CheckExistsRequestCodes.validateCode(code):
        log = f"The code {code} provided is not valid for CHECK_EXISTS. {FileServerCommands.CheckExistsRequestCodes.VALID_CODES} expected"
        request_bad("CHECK_EXISTS", log)
        respond(request, False, log)
        return

    if code == FileServerCommands.CheckExistsRequestCodes.WEEK_EXISTS:
        checkWeekExists(request)
    elif code == FileServerCommands.CheckExistsRequestCodes.MODULE_EXISTS:
        checkModuleExists(request)
    elif code == FileServerCommands.CheckExistsRequestCodes.ASSIGNMENT_EXISTS:
        checkAssignmentExists(request)

def createWeekDirectory(request: Request):
    params = request.args

    module = None
    week_number = None

    if 'module' in params:
        module = params['module']

    if 'week_number' in params:
        week_number = params['week_number']

    log_message = ""
    error_message = ""
    showError = False

    if not module:
        log_message = "Mandatory module parameter not provided"
        error_message = "You need to provide a module parameter"
        showError = True
    elif not week_number:
        log_message = "Mandatory week_number parameter not provided"
        error_message = "You need to provide a week_number parameter"
        showError = True

    if showError:
        request_bad("CREATE_WEEK_DIRECTORY", log_message)
        respond(request, False, error_message)
    else:
        path = "/module/" + module + "/" # TODO this doesn't look right, should it be .handin/module
        module_dir = DIR_ROOT + path
        path = module_dir + week_number
        if not os.path.exists(path):
            os.mkdir(path)
            logging.debug(f"Creating directory {path}")
        else:
            logging.debug(f"Path {path} already exists, not creating it")

        params_path = os.path.join(path, "params.yaml")
        if not os.path.exists(params_path):
            with open(params_path, "w"):
                pass # TODO what's whis supposed to do

        response_data = {
            'params_path': params_path
        }

        request_ok("CREATE_WEEK_DIRECTORY")
        respond(request, True, "CREATE_WEEK_DIRECTORY successful", response_data)

def updateParamsFile(request: Request):
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

        with open(params_file, 'a') as file:
            # TODO: any more params to add??
            yaml.dump(params, file, default_flow_style=False)

        request_ok("UPDATE_PARAMS_FILE")
        respond(request, True, "UPDATE_PARAMS_FILE successful")

def createDefinitionsFile(request: Request):
    params = request.args

    module = None
    academic_year = None

    if 'module' in params:
        module = params['module']

    if 'academic_year' in params:
        academic_year = params['academic_year']

    log_message = ""
    error_message = ""
    showError = False

    if not module:
        log_message = "Mandatory module parameter not provided"
        error_message = "You need to provide a module parameter"
        showError = True
    elif not academic_year:
        log_message = "Mandatory academic_year parameter not provided"
        error_message = "You need to provide an academic_year parameter"
        showError = True

    if showError:
        request_bad("CREATE_DEFINITIONS_FILE", log_message)
        respond(request, False, error_message)
    else:
        logging.debug(f"Creating definitions file for module {module} and academic year {academic_year}")
        moduleDir = const.modulePath(module, academic_year)
        """create tmpdir and definitions file"""
        definitions_path = os.path.join(moduleDir, "definitions.yaml")
        if not os.path.exists(definitions_path):
            logging.debug(f"{definitions_path} does not exist, creating it")
            with open(definitions_path, "w"):
                pass
        else:
            logging.debug(f"{definitions_path} already exists, not creating it")

        response_data = {
            'definitions_path': definitions_path
        }

        request_ok("CREATE_DEFINITIONS_FILE")
        respond(request, True, "CREATE_DEFINITIONS_FILE successful", response_data)

def updateDefinitionsFile(request: Request):
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

        with open(definitions_file, 'a') as file:
            # TODO: any more defs to add??
            yaml.dump(definitions, file, default_flow_style=False)

        request_ok("UPDATE_DEFINITIONS_FILE")
        respond(request, True, "UPDATE_DEFINITIONS_FILE successful")

def getParams(request: Request):
    args = requesta.args

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
        request_bad("GET_PARAMS", log_message)
        respond(request, False, error_message)
    else:
        filename = os.path.join(ROOTDIR + module + "/curr/assignments/" + assignment +"/params.yaml")
        logging.debug(f"Reading file {filename}")
        try:
            with open(filename, 'rb') as f:
                content = f.read().decode('utf-8')
        except Exception as e:
            content = ""

        response_data = {
            'content': content,
            'filename': filename
        }

        request_ok("GET_PARAMS")
        respond(request, True, "GET_PARAMS successful", response_data)

def saveFile(request: Request):
    # TODO sending a file in a single request may be too big. Consider changing how large text is sent
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
        os.mkdir(newAssignmentPath)
        filename = os.path.join(newAssignmentPath + "/params.yaml")
        logging.debug(f"Creating file filename")
        file = open(filename, 'w')
        file.write(self.textEdit_showFileContent.toPlainText())
        file.close()

        request_ok("FILE_SAVE")
        respond(request, True, "FILE_SAVE successful")

def processCommand(request: Request, command):
    logging.debug(f"Command {command} received")
    if command == FileServerCommands.AUTHENTICATE_LECTURER:
        checkCredentials(request)
    elif command == FileServerCommands.ALERT_MAC_ADDRESS:
        alertMacAddress(request)
    elif command == FileServerCommands.TRUST_MAC_ADDRESS:
        trustMacAddress(request)
    elif command == FileServerCommands.GET_LECTURER_MODULES:
        getLecturerModules(request)
    elif command == FileServerCommands.MODULE_INFO:
        processModuleInfo(request)
    elif command == FileServerCommands.GET_VARS:
        getVars(request)
    elif command == FileServerCommands.CHECK_EXISTS:
        checkExistence(request)
    elif command == FileServerCommands.CREATE_WEEK_DIRECTORY:
        createWeekDirectory(request)
    elif command == FileServerCommands.UPDATE_PARAMS_FILE:
        updateParamsFile(request)
    elif command == FileServerCommands.CREATE_DEFINITIONS_FILE:
        createDefinitionsFile(request)
    elif command == FileServerCommands.UPDATE_DEFINITIONS_FILE:
        updateDefinitionsFile(request)
    elif command == FileServerCommands.GET_PARAMS:
        getParams(request)
    elif command == FileServerCommands.FILE_SAVE:
        saveFile(request)

def serveRequest(request: Request, addr):
    while True:
        try:
            request.receive()

            if not request.disconnected:
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
