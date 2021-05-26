import os
import yaml
import shutil
from const import *
from file_server_commands.AbstractCommand import AbstractCommand
from handin_messaging import *
import logging
from handin_file_server import *
import definitions

class CloneAssignment(AbstractCommand):
    COMMAND = FileServerCommands.CLONE_ASSIGNMENT

    def __init__(self):
        super().__init__()

    def copyTestFiles(self, assignment_path, test: dict, tests: dict, test_key):
        files = ["answerFile", "filterFile", "inputDataFile"]

        for file in files:
            if file in test:
                file_path = test[file]
                if file_path != "" and os.path.isfile(file_path):
                    shutil.copy(file_path, assignment_path)
                    tests[test_key][file] = assignment_path + "/" + getFileNameFromPath(file_path)

    def generateDates(self, module, week_number, assignment):
        definitions_path = const.get_definitions_file_path(module)
        date_format = "%Y-%m-%d %H:%M"
        if os.path.isfile(definitions_path):
            with open(definitions_path, 'r') as stream:
                definitions_loaded = yaml.safe_load(stream)
            dates = definitions.calculate_dates(week_number, definitions_loaded)
            assignment['startDay'] = dates[0].strftime(date_format)
            assignment['endDay'] = dates[1].strftime(date_format)
            assignment['cutoffDay'] = dates[2].strftime(date_format)

    def doClone(self, module, assignment_name, assignment_path, contents):
        data: dict = yaml.safe_load(contents)

        if "tests" in data:
            tests = data["tests"]
            for key, value in tests.items():
                if key != "attendance" and key != "compilation":
                    test = value
                    self.copyTestFiles(assignment_path, test, tests, key)

        filename = os.path.join(assignment_path + "/params.yaml")
        logging.debug(f"Creating file {filename}")

        if definitions.is_week_number(assignment_name):
            assignment_name = definitions.normalize_week_number(assignment_name)
            data['weekNumber'] = assignment_name
            self.generateDates(module, assignment_name, data)

        with open(filename, 'w+') as file:
            yaml.dump(data, file, default_flow_style=False)

        with open(filename, 'r') as file:
            return file.read(), filename

    def handleRequest(self, request: Request):
        # TODO sending a file in a single request may be too big. Consider changing how large text is sent, maybe in handin_messaging check the size of the string and split it into multiple sendall calls with the final call having DONE at the end
        params = request.args

        module = None
        assignment = None
        content = None

        log_message = ""
        error_message = ""
        showError = False

        if 'module' in params:
            module = params['module']

        if 'assignment' in params:
            assignment = params['assignment']

        if 'content' in params:
            content = params['content']

        if not module:
            log_message = "Mandatory module parameter not provided"
            error_message = "You need to provide a module parameter"
            showError = True
        elif not assignment:
            log_message = "Mandatory assignment parameter not provided"
            error_message = "You need to provide an assignment parameter"
            showError = True
        elif not content:
            log_message = "Mandatory content parameter not provided"
            error_message = "You need to provide a content parameter"
            showError = True

        if showError:
            request_bad("CLONE_ASSIGNMENT", log_message)
            respond(request, False, error_message)
        else:
            newAssignmentPath = os.path.join(ROOTDIR + "/" + module + "/curr/assignments/" + assignment)
            if os.path.isdir(newAssignmentPath):
                request_ok("CLONE_ASSIGNMENT")
                respond(request, False, f"An assignment with the name {assignment} already exists")
                return

            logging.debug(f"Creating directory {newAssignmentPath}")
            os.makedirs(newAssignmentPath)

            cloned_tuple = self.doClone(module, assignment, newAssignmentPath, content)
            response_data = {
                'contents': cloned_tuple[0],
                'path': cloned_tuple[1]
            }

            request_ok("CLONE_ASSIGNMENT")
            respond(request, True, "CLONE_ASSIGNMENT successful", response_data)
