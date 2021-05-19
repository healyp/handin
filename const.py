import os
import re
from datetime import datetime

import yaml
from pathlib import Path

HANDINHOME = os.getcwd()

if "src" in HANDINHOME:
    HANDINHOME = HANDINHOME + "/.."

ROOTDIR = HANDINHOME + "/.handin"
SRCDIR = HANDINHOME + "/src"

CONF = os.path.join(HANDINHOME, "conf.yaml")

with open(CONF, 'r') as stream:
    data: dict = yaml.safe_load(stream)

# Handin System Server Configs
HOST = data['system_host']
PORT = data['system_port']
ADDR = (HOST, PORT)

RESPONSE_TIMEOUT = data['response_timeout'] # timeout for waiting for a response in seconds

REGISTRATION_HOST = data['registration_host']
REGISTRATION_PORT = data['registration_port']
REGISTRATION_ADDR = (REGISTRATION_HOST, REGISTRATION_PORT)

FILE_SERVER_HOST = data['file_server_host']
FILE_SERVER_PORT = data['file_server_port']
FILE_ADDR = (FILE_SERVER_HOST, FILE_SERVER_PORT)
FILE_LOG_LEVEL = data['file_server_log_level']
FILE_HTML_LANDING = data['file_html_landing']

ModCodeRE = r"^cs\d{4}$"          # UL module code re

class FileServerCommands:
    AUTHENTICATE_LECTURER = "authenticate_lecturer"
    ALERT_MAC_ADDRESS = "alert_mac_address"
    TRUST_MAC_ADDRESS = "trust_mac_address"
    GET_LECTURER_MODULES = "get_lecturer_modules"
    MODULE_INFO = "module_info"
    GET_VARS = "get_vars"
    CHECK_EXISTS = "check_exists"
    CREATE_ASSIGNMENT_DIRECTORY = "create_assignment_directory"
    UPDATE_PARAMS_FILE = "update_params_file"
    CREATE_DEFINITIONS_FILE = "create_definitions_file"
    UPDATE_DEFINITIONS_FILE = "update_definitions_file"
    GET_DEFINITIONS_FILE = "get_definitions_file"
    GET_PARAMS = "get_params"
    CLONE_ASSIGNMENT = "clone_assignment"
    UPLOAD_FILE = "upload_file" # The path to the file should be a relative path as the server will prepend ROOTDIR to it
    VALID_COMMANDS = [AUTHENTICATE_LECTURER, ALERT_MAC_ADDRESS, TRUST_MAC_ADDRESS, GET_LECTURER_MODULES, MODULE_INFO
                     , GET_VARS, CHECK_EXISTS, CREATE_ASSIGNMENT_DIRECTORY, UPDATE_PARAMS_FILE, CREATE_DEFINITIONS_FILE
                     , UPDATE_DEFINITIONS_FILE, GET_DEFINITIONS_FILE, GET_PARAMS, CLONE_ASSIGNMENT, UPLOAD_FILE]

    @staticmethod
    def validateCommand(command):
        return command in FileServerCommands.VALID_COMMANDS

    class ModuleInfoRequestCodes:
        CODE = "request_code"

        MODULE_CODES = "module_codes"
        MODULE_ASSIGNMENTS = "module_assignments"
        MODULE_TEST_ITEMS = "module_test_items"
        MODULE_STUDENT_IDS = "module_student_ids"
        VALID_CODES = [MODULE_CODES, MODULE_ASSIGNMENTS, MODULE_TEST_ITEMS, MODULE_STUDENT_IDS]

        @staticmethod
        def validateCode(code):
            return code in FileServerCommands.ModuleInfoRequestCodes.VALID_CODES

    class CheckExistsRequestCodes:
        CODE = "request_code"

        MODULE_EXISTS = "module_exists"
        ASSIGNMENT_EXISTS = "assignment_exists"
        VALID_CODES = [MODULE_EXISTS, ASSIGNMENT_EXISTS]

        @staticmethod
        def validateCode(code):
            return code in FileServerCommands.CheckExistsRequestCodes.VALID_CODES


def get_class_list_file_path(module_code):
    return os.path.join(ROOTDIR, module_code, "curr", "class-list")


def get_definitions_file_path(module_code):
    return os.path.join(ROOTDIR, module_code, "curr", "definitions.yaml")


def get_params_file_path(module_code, week_number):
    return os.path.join(ROOTDIR, module_code, "curr", "assignments", week_number, "params.yaml")


def get_vars_file_path(module_code, week_number, student_id):
    return os.path.join(ROOTDIR, module_code, "curr", "data", student_id, week_number, "vars.yaml")


def get_program_file_path(module_code, week_number, student_id, filename_code):
    return os.path.join(ROOTDIR, module_code, "curr", "data", student_id, week_number, filename_code)

"""
Check if an /instance/ of a module exists; instance=code+"curr"
"""
def check_if_module_exists(mc: str) -> bool:
    path = os.path.join(ROOTDIR, mc, "curr")
    if os.path.exists(path):
        # modules = [name.lower() for name in os.listdir(path)]
        # if module_code.lower() in modules:
        return True
    return False

def findStudentId(stuId: str, filePath: str):
    regex = "\\b{}\\b".format(stuId)
    with open(filePath, 'r') as f:
        for line in f:
            if re.match(regex, line):
                return line
    return ''


def check_if_week_exists(module_code: str, week_number: str) -> bool:
    path = ROOTDIR + module_code + "/assignments/"
    if os.path.exists(path):
        weeks = [name for name in os.listdir(path)]
        if week_number in weeks:
            return True
    return False


def check_if_ass_exists(module_code: str, ay: str, ass: str) -> bool:
    path = assPath(module_code, ay, ass)
    if os.path.exists(path):
        return True
    return False


def containsValidDay(given: str):
    names = [ r"mo(nday)?",
              r"mo|monday",
              r"tu(esday)?",
              r"we(dnesday)?",
              r"th(ursday)?",
              r"fr(iday)?",
              r"sa(turday)?",
              r"su(nday)?" ]
    for dow in names:
        if re.search(dow, given, re.IGNORECASE):
            return True
    return False


def whatAY():
    # datetime.today().strftime('%Y-%m-%d')
    date = datetime.today()
    startAY = date.year
    month = date.month
    sem = 1
    if (1 <= month and month <= 6):
        startAY = startAY - 1
        sem = 2
    endAY = startAY + 1

    return '{}-{}-S{}'.format(startAY, endAY, sem)


def modulePath(module_code: str, ay: str):
    return "{}/{}/{}".format(ROOTDIR, module_code.lower(), ay)


def assPath(module_code: str, ay: str, ass: str):
    return "{}/{}/{}/{}/{}".format(ROOTDIR, module_code.lower(), ay, "assignments", ass)

def getFileNameFromPath(path):
    return Path(path).name
