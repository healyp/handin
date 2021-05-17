import os
from const import *
from file_server_commands.AbstractCommand import AbstractCommand
from handin_messaging import *
import logging
from handin_file_server import *

class ModuleInfo(AbstractCommand):
    COMMAND = FileServerCommands.MODULE_INFO

    def __init__(self):
        super().__init__()

    def getModuleCodes(self, request: Request):
        list = [name for name in os.listdir(ROOTDIR) if re.match(ModCodeRE, name)]
        logging.debug(f"Module Codes found: {list}")
        response_data = {
            'module_codes': list
        }

        request_ok("MODULE_INFO: MODULE_CODES")
        respond(request, True, "MODULE_INFO: MODULE_CODES Successful", response_data)

    def getModuleAssignments(self, request: Request):
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

    def getModuleTestItems(self, request: Request):
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

    def getModuleStudentIds(self, request: Request):
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

    def handleRequest(self, request: Request):
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
                self.getModuleCodes(request)
            elif code == FileServerCommands.ModuleInfoRequestCodes.MODULE_ASSIGNMENTS:
                self.getModuleAssignments(request)
            elif code == FileServerCommands.ModuleInfoRequestCodes.MODULE_TEST_ITEMS:
                self.getModuleTestItems(request)
            elif code == FileServerCommands.ModuleInfoRequestCodes.MODULE_STUDENT_IDS:
                self.getModuleStudentIds(request)
        else:
            request_unauthorized("MODULE_INFO")
            send_unauthorized_lecturer_response(request)
