import csv
import datetime
import os
import shutil

import yaml

import const
from file_server_commands.AbstractCommand import AbstractCommand
from handin_messaging import *
from handin_file_server import *

class GenerateAssignmentCsv(AbstractCommand):
    COMMAND = FileServerCommands.GENERATE_ASSIGNMENT_CSV

    def __init__(self):
        super().__init__()

    def write_student_marks(self, data_path, assignment_name, student_id, test_columns, rows: list):
        student_submission_path = os.path.join(data_path, student_id, assignment_name)
        student_submission_vars_path = os.path.join(student_submission_path, "vars.yaml")

        if os.path.isdir(student_submission_path) and os.path.isfile(student_submission_vars_path):
            with open(student_submission_vars_path, 'r') as file:
                vars: dict = yaml.safe_load(file)

            values = [student_id]

            for column in test_columns:
                if column in vars:
                    values.append(int(vars[column]))
                else:
                    values.append(0)


            submission_date = os.path.join(student_submission_path, "submission-date.txt")
            if os.path.isfile(submission_date):
                with open(submission_date, 'r') as file:
                    submission_date = file.readline()
            else:
                submission_date = "N/A"

            values.append(submission_date)

            rows.append(values)

    def generate_assignment_csv(self, module, assignment_path, data_path, students: list, reports_path):
        assignment = os.path.basename(assignment_path)
        params_file_path = const.get_params_file_path(module, assignment)
        report_file_path = os.path.join(reports_path, f"{assignment}-grades.csv")

        if os.path.isfile(report_file_path):
            shutil.move(report_file_path, report_file_path + ".old")

        with open(params_file_path, 'r') as file:
            params: dict = yaml.safe_load(file)

        if "tests" in params and len(students) > 0:
            with open(report_file_path, 'w+') as report_file:
                report_writer = csv.writer(report_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_NONNUMERIC)
                columns = ["Student ID"]

                tests = params["tests"]

                for key in tests.keys():
                    columns.append(key)

                columns.append("marks")
                columns.append("Submission Date")

                report_writer.writerow(columns)

                rows = []
                for student in students:
                    self.write_student_marks(data_path, assignment, student, columns[1:len(columns) - 1], rows)

                if len(rows) == 0:
                    # there were no grades for this assignment, so remove the report file
                    os.remove(report_file_path)
                else:
                    for row in rows:
                        report_writer.writerow(row)

    def generate_csv(self, module, assignment):
        module_path = os.path.join(const.ROOTDIR, module, "curr")
        assignments_path = os.path.join(module_path, "assignments")
        data_path = os.path.join(module_path, "data")
        reports_path = os.path.join(module_path, "reports")

        if not os.path.isdir(reports_path):
            os.makedirs(reports_path)

        if os.path.isdir(assignments_path) and os.path.isdir(data_path):
            if assignment == "all":
                assignments = os.listdir(assignments_path)
            else:
                assignments = [assignment]

            for assignment in assignments:
                self.generate_assignment_csv(module, os.path.join(assignments_path, assignment),
                                             data_path, os.listdir(data_path), reports_path)

    def handleRequest(self, request: Request):
        params = request.args

        module = None
        assignment = "all"

        log_message = ""
        error_message = ""
        showError = False

        if 'module' in params:
            module = params['module']

        if 'assignment' in params:
            assignment = params['assignment']

        if not module:
            log_message = "Mandatory contents parameter not provided"
            error_message = "You need to provide a contents parameter"
            showError = True

        if showError:
            request_bad("GENERATE_ASSIGNMENT_CSV", log_message)
            respond(request, False, error_message)
        else:
            if assignment != "all" and not const.check_if_ass_exists(module, "curr", assignment):
                request_ok("GENERATE_ASSIGNMENT_CSV")
                respond(request, False, "Assignment " + assignment + " does not exist for module " + module)
            else:
                self.generate_csv(module, assignment)
                request_ok("GENERATE_ASSIGNMENT_CSV")
                respond(request, True, "GENERATE_ASSIGNMENT_CSV successful")
