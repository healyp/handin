import os
from const import FileServerCommands
from file_server_commands.AbstractCommand import AbstractCommand
from handin_messaging import *
import logging
from handin_file_server import *

class CheckExists(AbstractCommand):
    COMMAND = FileServerCommands.CHECK_EXISTS

    def __init__(self):
        super().__init__()

    def handleRequest(self, request: Request):
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
            self.checkWeekExists(request)
        elif code == FileServerCommands.CheckExistsRequestCodes.MODULE_EXISTS:
            self.checkModuleExists(request)
        elif code == FileServerCommands.CheckExistsRequestCodes.ASSIGNMENT_EXISTS:
            self.checkAssignmentExists(request)

    def checkWeekExists(self, request: Request):
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

    def checkModuleExists(self, request: Request):
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

    def checkAssignmentExists(self, request: Request):
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
