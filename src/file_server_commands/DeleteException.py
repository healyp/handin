import os.path

import yaml

import const
from const import FileServerCommands, check_if_module_exists, check_if_ass_exists, whatAY
from file_server_commands.AbstractCommand import AbstractCommand
from handin_messaging import *
from handin_file_server import *

class DeleteException(AbstractCommand):
    COMMAND = FileServerCommands.DELETE_EXCEPTION

    def __init__(self):
        super().__init__()

    def get_existing_exceptions(self, exceptions_path):
        if os.path.isfile(exceptions_path):
            with open(exceptions_path, 'r') as file:
                return yaml.safe_load(file)

        return {}

    def write_exceptions(self, exceptions_path, exceptions):
        if len(exceptions) == 0 and os.path.isfile(exceptions_path):
            os.remove(exceptions_path)
        else:
            with open(exceptions_path, 'w+') as file:
                yaml.dump(exceptions, file)

    def updateExceptionsFile(self, request, module, assignment, student_id):
        if not check_if_module_exists(module):
            request_ok("DELETE_EXCEPTION")
            respond(request, False, f"Module {module} doesn't exist")
            return False
        elif not check_if_ass_exists(module, whatAY(), assignment):
            request_ok("DELETE_EXCEPTION")
            respond(request, False, f"Assignment {assignment} doesn't exist")
            return False

        exceptions_path = os.path.join(const.ROOTDIR, module, "curr", "assignments", assignment, "exceptions.yaml")

        current_exceptions = self.get_existing_exceptions(exceptions_path)

        if student_id in current_exceptions:
            current_exceptions.pop(student_id)
            submission_path = os.path.join(const.ROOTDIR, module, "curr", "data", student_id, assignment, "reinit.attempts")
            if os.path.isfile(submission_path):
                os.remove(submission_path)

            self.write_exceptions(exceptions_path, current_exceptions)
            return True
        else:
            request_ok("DELETE_EXCEPTION")
            respond(request, False, f"No exceptions exist for student {student_id}")
            return False

    def handleRequest(self, request: Request):
        if authenticate_lecturer(request, "DELETE_EXCEPTION", False):
            args = request.args

            module = None
            assignment = None
            student_id = None

            if 'module' in args:
                module = args['module']

            if 'assignment' in args:
                assignment = args['assignment']

            if 'student_id' in args:
                student_id = args['student_id']

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

            if showError:
                request_bad("DELETE_EXCEPTION", log_message)
                respond(request, False, error_message)
            else:
                if self.updateExceptionsFile(request, module, assignment, student_id):
                    request_ok("DELETE_EXCEPTION")
                    respond(request, True, "DELETE_EXCEPTION successful")

        else:
            request_unauthorized("DELETE_EXCEPTION")
            send_unauthorized_lecturer_response(request)
