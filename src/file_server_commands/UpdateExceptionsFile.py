import os.path

import yaml

import const
from const import FileServerCommands, check_if_module_exists, check_if_ass_exists, whatAY
from file_server_commands.AbstractCommand import AbstractCommand
from handin_messaging import *
from handin_file_server import *

class UpdateExceptionsFile(AbstractCommand):
    COMMAND = FileServerCommands.UPDATE_EXCEPTIONS_FILE

    def __init__(self):
        super().__init__()

    def check_class_list(self, module, student_id):
        class_list_path = os.path.join(const.ROOTDIR, module, 'curr', 'class-list')
        if not os.path.exists(class_list_path):
            return False
        else:
            with open(class_list_path, 'r') as file:
                for line in file:
                    line = line.strip()
                    if line == student_id:
                        return True

            return False

    def get_existing_exceptions(self, exceptions_path):
        if os.path.isfile(exceptions_path):
            with open(exceptions_path, 'r') as file:
                return yaml.safe_load(file)

        return {}

    def write_exceptions(self, exceptions_path, exceptions):
        with open(exceptions_path, 'w+') as file:
            yaml.dump(exceptions, file)

    def signalAttemptsReinit(self, module, assignment, student_id):
        # student already made a submission, so signal an attempts re-init to the server
        student_submission_directory = os.path.join(const.ROOTDIR, module, "curr", "data", student_id, assignment)

        if os.path.isdir(student_submission_directory) and os.path.isfile(student_submission_directory + "/vars.yaml"):
            with open(student_submission_directory + "/reinit.attempts", 'w+') as file:
                pass

    def updateExceptionsFile(self, request, module, assignment, student_id, exceptions):
        if not check_if_module_exists(module):
            request_ok("UPDATE_EXCEPTIONS_FILE")
            respond(request, False, f"Module {module} doesn't exist")
            return False
        elif not check_if_ass_exists(module, whatAY(), assignment):
            request_ok("UPDATE_EXCEPTIONS_FILE")
            respond(request, False, f"Assignment {assignment} doesn't exist")
            return False
        elif not self.check_class_list(module, student_id):
            request_ok("UPDATE_EXCEPTIONS_FILE")
            respond(request, False, f"Student {student_id} is not in this module's class list")
            return False

        exceptions_path = os.path.join(const.ROOTDIR, module, "curr", "assignments", assignment, "exceptions.yaml")

        current_exceptions = self.get_existing_exceptions(exceptions_path)
        current_exceptions[student_id] = exceptions
        self.write_exceptions(exceptions_path, current_exceptions)

        if 'totalAttempts' in exceptions:
            self.signalAttemptsReinit(module, assignment, student_id)

        return True

    def handleRequest(self, request: Request):
        if authenticate_lecturer(request, "UPDATE_EXCEPTIONS_FILE", False):
            args = request.args

            module = None
            assignment = None
            student_id = None
            exceptions = None

            if 'module' in args:
                module = args['module']

            if 'assignment' in args:
                assignment = args['assignment']

            if 'student_id' in args:
                student_id = args['student_id']

            if 'exceptions' in args:
                exceptions = args['exceptions']

            log_message = ""
            error_message = ""
            showError = False

            if not module:
                log_message = "Mandatory module parameter not provided"
                error_message = "You need to provide a module parameter"
                showError = True
            elif not assignment:
                log_message = "Mandatory assignment parameter not provided"
                error_message = "You need to provide an assignment parameter"
                showError = True
            elif not student_id:
                log_message = "Mandatory student_id parameter not provided"
                error_message = "You need to provide a student_id parameter"
                showError = True
            elif not exceptions:
                log_message = "Mandatory exceptions parameter not provided"
                error_message = "You need to provide an exceptions parameter"
                showError = True

            if showError:
                request_bad("UPDATE_EXCEPTIONS_FILE", log_message)
                respond(request, False, error_message)
            else:
                if self.updateExceptionsFile(request, module, assignment, student_id, exceptions):
                    request_ok("UPDATE_EXCEPTIONS_FILE")
                    respond(request, True, "UPDATE_EXCEPTIONS_FILE successful")

        else:
            request_unauthorized("UPDATE_EXCEPTIONS_FILE")
            send_unauthorized_lecturer_response(request)
