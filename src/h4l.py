import re

import yaml

from PyQt5 import QtCore
from PyQt5.QtCore import QDate, QTime, QRegExp, QDateTime
from PyQt5.QtGui import QRegExpValidator
from PyQt5.QtWidgets import QMainWindow, QDialog, QMessageBox, QLineEdit, QGroupBox, QTableWidgetItem

from traceback import format_exc

from getmac import get_mac_address as gma

from ui.impl.createAssignment_dialog import Ui_Dialog as Ui_Dialog_CreateAssignment
from ui.impl.manage_student_marks_dialog import Ui_Dialog as Ui_Dialog_Manage_Student_Marks
from ui.impl.create_definitions_dialog import Ui_Dialog as Ui_Dialog_Create_Definitions
from ui.impl.view_assignment_dialog import Ui_Dialog as Ui_Dialog_View_Assignment
from ui.impl.handin_lecturer_login import Ui_MainWindow as Ui_MainWindow_Lecturer_Login
from ui.impl.handin_lecturer_dialog import Ui_Dialog as Ui_Main_Lecturer_Dialog
from ui.impl.pick_module_dialog import Ui_Dialog as Ui_Dialog_pick_module

# from dateutil.parser import parse
from datetime import date

from const import whatAY, containsValidDay, getFileNameFromPath

import definitions as _definitions

from h4l_requests import *

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(asctime)s %(message)s')

lecturer = ""
module = ""
password = ""
definitions = {}

def createTableItem(val):
    item = QTableWidgetItem(val)
    item.setFlags(QtCore.Qt.ItemIsEnabled)
    return item

def create_message_box(text):
    msgBox = QMessageBox()
    msgBox.setIcon(QMessageBox.Information)
    msgBox.setText(text)
    msgBox.setWindowTitle("Message")
    msgBox.setStandardButtons(QMessageBox.Ok)
    msgBox.exec()

def create_message_box_mac(lecturer, text):
    msgBox = QMessageBox()
    msgBox.setIcon(QMessageBox.Information)
    msgBox.setText(text)
    msgBox.setWindowTitle("Message")
    msgBox.setStandardButtons(QMessageBox.Close | QMessageBox.Yes | QMessageBox.No)
    ret = msgBox.exec()
    if ret == QMessageBox.Yes:
        trustMacAddress(lecturer, "true")
    elif ret == QMessageBox.No:
        trustMacAddress(lecturer, "false")
    elif ret == QMessageBox.Close:
        disconnect()
        sys.exit(0)

def isMatchRegex(regex: str, text: str) -> bool:
    return bool(re.match(regex, text, re.IGNORECASE))

def validDefaultDate(given: str):
    if containsValidDay(given) and re.search("%w(\s*[+-]\s*\d+)?", given, re.IGNORECASE):
        return True
    else:
        return False

class MainWindow(QMainWindow, Ui_MainWindow_Lecturer_Login):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setupUi(self)
        self.pushButton_login.clicked.connect(lambda: self.pick_module_dialog())
        setSocket(True)

    def pick_module_dialog(self):
        global lecturer, password
        lecturer = self.lineEdit_username.text().strip()
        password = self.lineEdit_password.text().strip()
        if lecturer == "" or password == "":
            self.label_alert.setText("You need to fill in both fields")
        else:
            authenticated, login_error = checkCredentials(lecturer, password)
            if authenticated:
                self.label_alert.setText("")
                alert, error = alertMacAddress(lecturer, gma())
                if not error:
                    if alert:
                        create_message_box_mac(lecturer, "Alert: Your account was accessed from a unrecognized device.\n\nIf this was you or you would like to trust this device click Yes.\n\nIf you would still like to be alerted when your account is accessed from this device click No.")
                    dialog = PickModuleDialog()
                    dialog.show()
            else:
                if not login_error:
                    self.label_alert.setText("Wrong login credentials. Try again.")
                else:
                    self.label_alert.setText("Error occurred. Try again.")

    def closeEvent(self, event):
        disconnect()
        event.accept()
        sys.exit(0)

class PickModuleDialog(QDialog, Ui_Dialog_pick_module):
    def __init__(self, parent=None):
        super(PickModuleDialog, self).__init__()
        self.setupUi(self)
        modules, error = getLecturerModules(lecturer)

        if not error:
            self.comboBox_modules.addItems(modules)
            if len(modules) == 0:
                self.pushButton.setEnabled(False)
                self.label_alert.setGeometry(50, 20, 400, 30)
                self.label_alert.setText("You have no modules. Contact handin admin to add a module.")
            self.pushButton.clicked.connect(lambda: self.main_dialog())
        else:
            self.pushButton.setEnabled(False)
            self.label_alert.setGeometry(50, 20, 400, 30)
            self.label_alert.setText("An error occurred, please try logging in again")

    def main_dialog(self):
        global module
        module = self.comboBox_modules.currentText()
        if module != "":
            dialog = MainLecturerDialog()
            dialog.exec()

class MainLecturerDialog(QDialog, Ui_Main_Lecturer_Dialog):
    def __init__(self, parent=None):
        super(MainLecturerDialog, self).__init__()
        self.setupUi(self)
        self.pushButton.clicked.connect(lambda: self.manage_student_marks())
        self.pushButton_2.clicked.connect(lambda: self.createOneOffAssignment())
        self.pushButton_4.clicked.connect(lambda: self.create_definitions())
        self.pushButton_5.clicked.connect(lambda: self.clone_assignment())
        self.buttonBox.button(QtWidgets.QDialogButtonBox.Cancel).clicked.connect(self.close)
        self.loadDefinitions()

    def loadDefinitions(self):
        global definitions
        academic_year = whatAY()
        definitions_loaded, error = getDefinitions(module, academic_year)

        if not error and len(definitions_loaded) > 0:
            definitions = definitions_loaded
            self.pushButton_4.setText("Update Definitions")
        else:
            definitions = {}

    def manage_student_marks(self):
        dialog = ManageStudentMarksDialog(self)
        dialog.show()

    def createOneOffAssignment(self):
        dialog = CreateAssignmentDialog(self)
        dialog.show()

    def create_definitions(self):
        dialog = CreateDefinitionsDialog(self)
        dialog.show()

    def clone_assignment(self):
        dialog = ViewAssignmentDialog(self)
        dialog.show()


class ManageStudentMarksDialog(QDialog, Ui_Dialog_Manage_Student_Marks):
    def __init__(self, parent=None):
        super(ManageStudentMarksDialog, self).__init__(parent)
        self.setupUi(self)
        self.comboBox_assignment.currentTextChanged.connect(self.update_table)
        self.label_module.setText(module)

        if self.loadAssignments():
            self.update_table()

    def columnFromLabel(self, label) -> int:
        model = self.tableWidget.horizontalHeader().model()
        for column in range(model.columnCount()):
            if model.headerData(column, QtCore.Qt.Horizontal) == label:
                return column
        return -1

    def loadAssignments(self):
        assignments, error = getModuleAssignments(module)
        if not error:
            for assignment in assignments:
                self.comboBox_assignment.addItem(assignment)

        return not error

    def update_table(self):
        """update table widget - signal"""
        try:
            horizontal_header_labels = ["Student ID"]
            assignment = self.comboBox_assignment.currentText()
            if assignment is not None and assignment != "":
                test_items, error = get_all_test_items(module, assignment)

                if not error:
                    horizontal_header_labels += test_items
                    horizontal_header_labels += ["Attempts Left", "Total Marks"]
                    length = len(horizontal_header_labels)
                    self.tableWidget.setColumnCount(length)
                    student_ids, error1 = get_all_student_ids(module)

                    if not error1:
                        self.tableWidget.setRowCount(len(student_ids))
                        self.tableWidget.setHorizontalHeaderLabels(horizontal_header_labels)

                        # write student ids
                        row = 0
                        for _id in student_ids:
                            self.tableWidget.setItem(row, 0, createTableItem(_id))
                            for i in range(1, length):
                                self.tableWidget.setItem(row, i, createTableItem(""))
                            row += 1
                        # write attendance, compilation, test1, test2 ....
                        vars = {}
                        try:
                            for row in range(self.tableWidget.rowCount()):
                                student_id = self.tableWidget.item(row, 0).text().strip()
                                data, error = get_vars(module, assignment, student_id)
                                if error:
                                    return

                                vars[(module, assignment, student_id)] = data
                                for label in horizontal_header_labels[1:-2]:
                                    if label in data.keys():
                                        self.tableWidget.setItem(row, self.columnFromLabel(label),
                                                                 createTableItem(str(data[label])))

                        except Exception as e:
                            e = format_exc()
                            print(e)
                        # write attempts left and total marks
                        try:
                            for row in range(self.tableWidget.rowCount()):
                                student_id = self.tableWidget.item(row, 0).text().strip()
                                vars_tuple = (module, assignment, student_id)
                                if not vars_tuple in vars:
                                    data, error = get_vars(module, assignment, student_id)
                                    if error:
                                        return
                                    vars[vars_tuple] = data
                                else:
                                    data = vars[vars_tuple]
                                if "attemptsLeft" in data.keys():
                                    self.tableWidget.setItem(row, self.columnFromLabel("Attempts Left"),
                                                             createTableItem(str(data["attemptsLeft"])))
                                if "marks" in data.keys():
                                    self.tableWidget.setItem(row, self.columnFromLabel("Total Marks"),
                                                             createTableItem(str(data["marks"])))
                        except Exception as e:
                            e = format_exc()
                            print(e)

        except Exception as e:
            print(e)
            self.tableWidget.clear()

def upload_test_files(params_path, data, editing = False, changed_files = {}):
    """map all tests paths to the path that will be stored on the server and upload the files"""
    fileKeys = ['inputDataFile', 'answerFile', 'filterFile']
    tests = data['tests']
    for key in tests:
        var = tests[key]
        for file in fileKeys:
            if file in var:
                reupload = True
                if editing:
                    if key in changed_files:
                        reupload = changed_files[key][file]
                    else:
                        reupload = False
                file_path = var[file]
                if reupload and file_path != "":
                    server_directory_relative, server_file_name = map_tests_path(params_path, key, file_path, file)
                    upload_path = server_directory_relative + "/" + server_file_name
                    upload_path = upload_path.replace("curr", const.whatAY())
                    var[file] = upload_path
                    if uploadFile(file_path, upload_path):
                        create_message_box(f"An error occurred uploading file {file_path} to server, try again")
                        return False

    return True

def map_tests_path(params_path, test_name, path, file):
    """
        Map path variable to the path of the file that will be stored on the server.
        The directory name of params_path is used as the directory with everything before the module code stripped off.
        The filename is then created as {test_name}-{file}{extension} where file is the key in the yaml storing the path to the file,
        e.g this method would return for an input file /local/path/to/fileinput.txt and for module cs4123 w01 and test1 and inputDataFile:
            server_directory_relative = /cs4123/curr/assignments/w01/ this is used to upload the file relative to .handin
            server_file_name = inputfile.txt
    """
    file_name = getFileNameFromPath(path)
    extension = os.path.splitext(file_name)[1]
    server_directory = os.path.dirname(params_path)
    server_directory_relative = server_directory[server_directory.index("/.handin") + len("/.handin"):]
    server_file_name = f"{test_name}-{file}{extension}"
    return server_directory_relative, server_file_name

class CreateAssignmentDialog(QDialog, Ui_Dialog_CreateAssignment):
    def __init__(self, parent=None, existing_assignment: dict = None, assignment_path: str = None):
        super(CreateAssignmentDialog, self).__init__(parent)
        self.setupUi(self)
        self.label_module.setText(module)
        self.dateTimeEdit_startDay.setDisplayFormat("yyyy-MM-dd HH:mm")
        self.dateTimeEdit_endDay.setDisplayFormat("yyyy-MM-dd HH:mm")
        self.dateTimeEdit_cutoffDay.setDisplayFormat("yyyy-MM-dd HH:mm")
        self.dateTimeEdit_startDay.setDateTime(QDateTime.currentDateTime())
        self.dateTimeEdit_endDay.setDateTime(QDateTime.currentDateTime())
        self.dateTimeEdit_cutoffDay.setDateTime(QDateTime.currentDateTime())
        self.spinBox_penaltyPerDay.setValue(7)
        self.spinBox_totalAttempts.setValue(10)
        regex = QRegExp("\\d+")
        self.lineEdit_assName.setToolTip("Enter the name for this assignment. If blank, the name will be the week number")
        self.lineEdit_attendance_marks.setValidator(QRegExpValidator(regex))
        self.lineEdit_compilation_marks.setValidator(QRegExpValidator(regex))
        self.lineEdit_marks.setValidator(QRegExpValidator(regex))
        self.create.clicked.connect(lambda: self.createOneOffAssignment())
        self.cancel.clicked.connect(lambda: self.cancelClicked())
        self.lineEdit_attendance_marks.textChanged.connect(self.update_total_marks)
        self.lineEdit_compilation_marks.textChanged.connect(self.update_total_marks)
        self.checkBox_inputDataFile.stateChanged.connect(
            lambda: self.add_file_with_check_box(self.checkBox_inputDataFile, self.label_inputDataFile))

        self.checkBox_answerFile.stateChanged.connect(
            lambda: self.add_file_with_check_box(self.checkBox_answerFile, self.label_answerFile))

        self.checkBox_filterFile.stateChanged.connect(
            lambda: self.add_file_with_check_box(self.checkBox_filterFile, self.label_filterFile,
                                                 is_filter=True, filter_line_edit=self.lineEdit_filterCommand))

        self.addTest.clicked.connect(self.addTestPressed)
        self.addTest.setEnabled(False)
        self.editButton.clicked.connect(lambda: self.editTestClicked())
        self.removeButton.clicked.connect(lambda: self.removeTest())

        self.weekNumber_comboBox.addItems(["w01", "w02", "w03", "w04", "w05", "w06", "w07", "w07", "w08", "w09", "w10", "w11", "w12", "w13"])
        self.weekNumber_comboBox.currentTextChanged.connect(self.auto_generate_dates)
        self.lineEdit_filterCommand.setDisabled(True)

        for groupBox in self.findChildren(QGroupBox):
            groupBox.toggled.connect(self.disable_create_button)

        for lineEdit in self.findChildren(QLineEdit):
            lineEdit.textChanged.connect(self.disable_create_button)

        for lineEdit in self.groupBox_customTest1.findChildren(QLineEdit):
            lineEdit.textChanged.connect(self.disable_test_button)

        self.create.setEnabled(False)

        self.unsaved_test = False # a variable to keep track of if there is a test being added/edited and Add/Edit Test was not clicked

        self.tests = {}
        self.test_number = 0

        self.existing_assignment = existing_assignment
        self.assignment_path = assignment_path
        self.changed_files = {} # keeps track of files that have changed since the editing started so that to signal that re-upload needs to occur

        self.setWindowTitle("Create Assignment")

        self.loadFromExisting()
        self.setupAutoDateCheckbox()

    def setupAutoDateCheckbox(self):
        if len(definitions) == 0:
            self.autoGenerate_checkBox.setEnabled(False)
            self.autoGenerate_checkBox.setToolTip("Create definitions to use this feature")
        else:
            self.autoGenerate_checkBox.setEnabled(True)
            self.autoGenerate_checkBox.setToolTip("Generate start, end and cutoff days based on the definitions file and the provided week number")

        self.autoGenerate_checkBox.stateChanged.connect(self.auto_generate_dates)

    def auto_generate_dates(self):
        if self.autoGenerate_checkBox.isChecked() and self.autoGenerate_checkBox.isEnabled():
            week_number = self.weekNumber_comboBox.currentText().strip()
            dates = _definitions.calculate_dates(week_number, definitions)
            if dates is not None:
                startDay = dates[0]
                endDay = dates[1]
                cutoffDay = dates[2]
                if startDay is not None:
                    startDay = startDay.strftime("%Y-%m-%d %H:%M")
                    self.dateTimeEdit_startDay.setDateTime(QDateTime.fromString(startDay, "yyyy-MM-dd HH:mm"))
                if endDay is not None:
                    endDay = endDay.strftime("%Y-%m-%d %H:%M")
                    self.dateTimeEdit_endDay.setDateTime(QDateTime.fromString(endDay, "yyyy-MM-dd HH:mm"))
                if cutoffDay is not None:
                    cutoffDay = cutoffDay.strftime("%Y-%m-%d %H:%M")
                    self.dateTimeEdit_cutoffDay.setDateTime(QDateTime.fromString(cutoffDay, "yyyy-MM-dd HH:mm"))


    def loadExistingTests(self, tests: dict):
        self.tests = tests
        if 'attendance' in tests:
            attendance = tests['attendance']
            self.groupBox_attendance.setChecked(True)
            if 'tag' in attendance:
                self.lineEdit_attendance_tag.setText(attendance['tag'])
            if 'marks' in attendance:
                self.lineEdit_attendance_marks.setText(str(attendance['marks']))

        if 'compilation' in tests:
            compilation = tests['compilation']
            self.groupBox_compilation.setChecked(True)
            if 'tag' in compilation:
                self.lineEdit_compilation_tag.setText(compilation['tag'])
            if 'marks' in compilation:
                self.lineEdit_compilation_marks.setText(str(compilation['marks']))
            if 'command' in compilation:
                self.lineEdit_compilation_command.setText(compilation['command'])

        self.reorderTests()
        self.disable_create_button()

    def loadFromExisting(self):
        if self.existing_assignment is not None and self.assignment_path is not None:
            name = os.path.basename(os.path.dirname(self.assignment_path))
            self.lineEdit_assName.setText(name)
            data = self.existing_assignment
            if 'weekNumber' in data:
                self.weekNumber_comboBox.setCurrentText(data['weekNumber'])
            if 'startDay' in data:
                self.dateTimeEdit_startDay.setDateTime(QDateTime.fromString(data['startDay'], "yyyy-MM-dd HH:mm"))
            if 'endDay' in data:
                self.dateTimeEdit_endDay.setDateTime(QDateTime.fromString(data['endDay'], "yyyy-MM-dd HH:mm"))
            if 'cutoffDay' in data:
                self.dateTimeEdit_cutoffDay.setDateTime(QDateTime.fromString(data['cutoffDay'], "yyyy-MM-dd HH:mm"))
            if 'totalAttempts' in data:
                self.spinBox_totalAttempts.setValue(data['totalAttempts'])
            if 'penaltyPerDay' in data:
                self.spinBox_penaltyPerDay.setValue(data['penaltyPerDay'])
            if 'collectionFilename' in data:
                self.lineEdit_collectFilename.setText(data['collectionFilename'])
            if 'tests' in data:
                self.loadExistingTests(data['tests'])

            self.setWindowTitle("Edit Assignment")
            self.create.setText("Save")
            self.update_total_marks()

    def setFileLabelText(self, label, text):
        label.setText(text)
        label.setToolTip(text)

    def num_tests(self):
        i = 0
        for key, value in self.tests.items():
            if key.startswith("test"):
                i += 1

        return i

    def disable_create_button(self):
        number_tests = self.num_tests()
        disable = number_tests == 0
        if not disable:
            test_lineEdits = self.groupBox_customTest1.findChildren(QLineEdit)

            for lineEdit in self.findChildren(QLineEdit):
                doDisableCheck = lineEdit not in test_lineEdits or number_tests == 0
                if doDisableCheck and lineEdit != self.lineEdit_assName and lineEdit.text().strip() == "" and lineEdit.isEnabled():
                    disable = True
                    break

        self.create.setEnabled(not disable)

    def disable_test_list(self, disable):
        if disable:
            self.testsGroupBox.setEnabled(False)
            self.testsGroupBox.setToolTip("Finish editing the current test")
        else:
            self.testsGroupBox.setEnabled(True)
            self.testsGroupBox.setToolTip(None)

    def disable_test_button(self):
        disable = False
        self.unsaved_test = False
        for lineEdit in self.groupBox_customTest1.findChildren(QLineEdit):
            enabled = lineEdit.isEnabled()
            if lineEdit.text().strip() == "" and enabled:
                disable = disable or True
            elif enabled:
                self.unsaved_test = True

        self.addTest.setEnabled(not disable)

    def add_file_with_check_box(self, check_box, label, is_filter=False, filter_line_edit=None):
        """add data/answer/filter file with check box -- signal"""
        if check_box.isChecked():
            dialog = QtWidgets.QFileDialog()
            dialog.setFileMode(QtWidgets.QFileDialog.AnyFile)
            filename, file_type = QtWidgets.QFileDialog.getOpenFileName(
                self, "Choose file", "./", "All Files (*)")
            self.setFileLabelText(label, filename)
            if is_filter and (filter_line_edit is not None):
                filter_line_edit.setEnabled(True)
                self.disable_test_button()
        else:
            label.setText("")
            if filter_line_edit is not None:
                filter_line_edit.setEnabled(False)
                self.disable_test_button()

    def silentCheckBox(self, checkBox):
        checkBox.blockSignals(True)
        checkBox.setChecked(True)
        checkBox.blockSignals(False)

    def clearTestForm(self):
        self.lineEdit_tag.clear()
        self.lineEdit_marks.clear()
        self.lineEdit_command.clear()
        self.lineEdit_filterCommand.clear()
        self.label_inputDataFile.setText("")
        self.label_answerFile.setText("")
        self.label_filterFile.setText("")
        self.checkBox_answerFile.setChecked(False)
        self.checkBox_inputDataFile.setChecked(False)
        self.checkBox_filterFile.setChecked(False)
        self.unsaved_test = False

    def addTestPressed(self):
        tag = self.lineEdit_tag.text().strip()
        marks = self.lineEdit_marks.text().strip()
        if marks != "":
            marks = int(marks)
        command = self.lineEdit_command.text().strip()
        inputDataFile = self.label_inputDataFile.text().strip()
        answerFile = self.label_answerFile.text().strip()
        filterFile = self.label_filterFile.text().strip()
        filterCommand = self.lineEdit_filterCommand.text().strip()
        self.test_number += 1
        self.tests[f"test{self.test_number}"] = {"tag": tag, "marks": marks, "command": command, "inputDataFile": inputDataFile,
                          "answerFile": answerFile, "filterFile": filterFile, "filterCommand": filterCommand}
        self.testList.addItem(f"{self.test_number}. Tag: {tag}, Marks: {marks}, Command: {command}")
        self.clearTestForm()
        self.update_total_marks()
        self.disable_create_button()

    def checkTestFilesEdited(self, test_key, old_test, edited_test):
        """ check if any test files were edited and need re-uploading to the server """
        keys = ['inputDataFile', 'answerFile', 'filterFile']

        if test_key not in self.changed_files:
            self.changed_files[test_key] = {}

        for key in keys:
            if key in old_test and key in edited_test:
                old = old_test[key]
                new = edited_test[key]
                self.changed_files[test_key][key] = new != "" and old != new
            else:
                self.changed_files[test_key][key] = False

    def editTest(self):
        itemChosenWidget = self.testList.currentItem()

        if itemChosenWidget is not None:
            itemChosen = itemChosenWidget.text()
            dotIndex = itemChosen.index(".")
            test_number = itemChosen[0:dotIndex]
            test_key = f"test{test_number}"
            test = self.tests[test_key]

            tag = self.lineEdit_tag.text().strip()
            marks = self.lineEdit_marks.text().strip()
            if marks != "":
                marks = int(marks)
            command = self.lineEdit_command.text().strip()
            inputDataFile = self.label_inputDataFile.text().strip()
            answerFile = self.label_answerFile.text().strip()
            filterFile = self.label_filterFile.text().strip()
            filterCommand = self.lineEdit_filterCommand.text().strip()
            self.tests[test_key] = {"tag": tag, "marks": marks, "command": command, "inputDataFile": inputDataFile,
                              "answerFile": answerFile, "filterFile": filterFile, "filterCommand": filterCommand}
            if self.existing_assignment is not None:
                self.checkTestFilesEdited(test_key, test, self.tests[test_key])
            itemChosenWidget.setText(f"{test_number}. Tag: {tag}, Marks: {marks}, Command: {command}")
            self.disable_test_list(False)
            self.addTest.setText("Add Test")
            self.label_19.setText("Add Test:")
            self.addTest.clicked.disconnect(self.editTest)
            self.addTest.clicked.connect(self.addTestPressed)
            self.clearTestForm()
            self.update_total_marks()

    def editTestClicked(self):
        itemChosen = self.testList.currentItem()

        if itemChosen is not None:
            self.disable_test_list(True)
            itemChosen = itemChosen.text()
            dotIndex = itemChosen.index(".")
            test_key = f"test{itemChosen[0:dotIndex]}"
            test = self.tests[test_key]
            self.lineEdit_tag.setText(test["tag"])
            self.lineEdit_marks.setText(str(test["marks"]))
            self.lineEdit_command.setText(test["command"])
            filter_command = test["filterCommand"]
            if filter_command != "":
                self.lineEdit_filterCommand.setText(filter_command)

            inputFile = test["inputDataFile"]
            if inputFile != "":
                self.setFileLabelText(self.label_inputDataFile, inputFile)
                self.silentCheckBox(self.checkBox_inputDataFile)

            answerFile = test["answerFile"]
            if answerFile != "":
                self.setFileLabelText(self.label_answerFile, answerFile)
                self.silentCheckBox(self.checkBox_answerFile)

            filterFile = test["filterFile"]
            if filterFile != "":
                self.setFileLabelText(self.label_filterFile, filterFile)
                self.silentCheckBox(self.checkBox_filterFile)

            self.label_19.setText("Edit Test:")
            self.addTest.setText("Edit Test")
            self.addTest.clicked.disconnect(self.addTestPressed)
            self.addTest.clicked.connect(self.editTest)

    def reorderTests(self):
        new_map = {}

        i = 1
        self.testList.clear()
        for key, value in self.tests.items():
            if key.startswith("test"):
                new_key = key[0:len("test")] + str(i)
                new_map[new_key] = value
                self.testList.addItem(f"{i}. Tag: {value['tag']}, Marks: {str(value['marks'])}, Command: {value['command']}")
                i += 1
            else:
                new_map[key] = value # in case the test is compilation or attendance

        self.tests = new_map
        self.test_number = i - 1

    def removeTest(self):
        itemChosenWidget = self.testList.currentItem()

        if itemChosenWidget is not None:
            itemChosen = itemChosenWidget.text()
            dotIndex = itemChosen.index(".")
            test_key = f"test{itemChosen[0:dotIndex]}"
            self.testList.takeItem(self.testList.currentRow())
            self.tests.pop(test_key)
            self.reorderTests()
            self.testList.setEnabled(True)
            self.update_total_marks()
            self.disable_create_button()

    def update_total_marks(self):
        """update total marks -- signal"""
        total_marks: int = self.get_total_marks()
        self.label_totalMarks.setText(str(total_marks))

    def get_total_marks(self) -> int:
        attendance = int(self.lineEdit_attendance_marks.text()) if len(self.lineEdit_attendance_marks.text()) > 0 and self.groupBox_attendance.isChecked() else 0
        compilation = int(self.lineEdit_compilation_marks.text()) if len(self.lineEdit_compilation_marks.text()) > 0 and self.groupBox_compilation.isChecked() else 0
        marks_sum = attendance + compilation

        for key, value in self.tests.items():
            if key.startswith("test"):
                marks_sum += value["marks"]

        return marks_sum

    def createOneOffAssignment(self):
        if self.unsaved_test:
            create_message_box("Save the test being currently edited first")
            return

        # module_code = self.comboBox_moduleCode.currentText().strip()
        module_code = module
        week_number = self.weekNumber_comboBox.currentText().strip()
        assName = self.lineEdit_assName.text().strip()
        if assName == "":
            assName = week_number
        start_day = self.dateTimeEdit_startDay.text().strip()
        end_day = self.dateTimeEdit_endDay.text().strip()
        cutoff_day = self.dateTimeEdit_cutoffDay.text().strip()
        penalty_per_day = int(self.spinBox_penaltyPerDay.value())
        total_attempts = int(self.spinBox_totalAttempts.value())
        collection_filename = self.lineEdit_collectFilename.text().strip()
        if self.groupBox_attendance.isChecked():
            tag = self.lineEdit_attendance_tag.text().strip()
            marks = int(self.lineEdit_attendance_marks.text().strip())
            self.tests["attendance"] = {"tag": tag, "marks": marks}
        if self.groupBox_compilation.isChecked():
            tag = self.lineEdit_compilation_tag.text().strip()
            marks = int(self.lineEdit_compilation_marks.text().strip())
            command = self.lineEdit_compilation_command.text().strip()
            self.tests["compilation"] = {"tag": tag, "marks": marks, "command": command}

        if self.existing_assignment is not None:
            assignment_exists = False
            error = False # fool it into thinking the assignment doesn't exist
            self.params_path = self.assignment_path
        else:
            assignment_exists, error = checkAssignmentExists(module_code, const.whatAY(), assName)
        if not error:
            if not assignment_exists:
                if self.existing_assignment is not None or self.create_assignment_directory(module_code, assName):
                    self.update_params_file(
                        moduleCode=module_code, weekNumber=week_number, startDay=start_day,
                        endDay=end_day, cutoffDay=cutoff_day, penaltyPerDay=penalty_per_day,
                        totalAttempts=total_attempts, collectionFilename=collection_filename, tests=self.tests)
            else:
                create_message_box(f"{assName} for module {module_code} already exists!")

    def create_assignment_directory(self, module, assignment_name):
        params_path, error = createAssignmentDirectory(module, assignment_name)
        if not error:
            self.params_path = params_path
            return True
        return False

    def update_params_file(self, **kwargs):
        editing = self.existing_assignment is not None
        changed_files = {}
        if editing:
            changed_files = self.changed_files
        if upload_test_files(self.params_path, kwargs, editing, changed_files):
            if not updateParamsFile(self.params_path, kwargs):
                # if this returns false, no error occurred
                if self.existing_assignment is None:
                    create_message_box("Assignment created successfully")
                else:
                    create_message_box("Assignment updated successfully")
                self.close()

    def confirm_close(self):
        ret = QMessageBox.question(self,'', "Are you sure you want to cancel? You will lose all changes", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        return ret == QMessageBox.Yes

    def cancelClicked(self):
        if self.confirm_close():
            self.close()

class CreateDefinitionsDialog(QDialog, Ui_Dialog_Create_Definitions):
    def __init__(self, parent=None):
        super(CreateDefinitionsDialog, self).__init__(parent)
        self.setupUi(self)
        self.dateEdit_startSemester.setDisplayFormat("yyyy-MM-dd")
        self.dateEdit_stylesheet = self.dateEdit_startSemester.styleSheet()
        self.dateEdit_startSemester.setDate(QDate.currentDate())
        self.dateEdit_startSemester.dateChanged.connect(self.disable_ok)
        self.timeEdit.setTime(QTime(23, 59, 00))
        # Academic Year format: 2020-2021-S1
        self.regexAY = "\\d{4}-\\d{4}-S[1,2]"
        # self.lineEdit_academicYear.setPlaceholderText(whatAY())
        self.lineEdit_academicYear.setText(whatAY())
        self.accepted.connect(lambda: self.create_definitions())
        self.buttonBox.setEnabled(False)
        # self.lineEdit.textChanged.connect(self.disable_buttonbox)
        self.label_module.setText(module)
        self.lineEdit_2.textChanged.connect(self.disable_ok)
        self.lineEdit_styleSheet = self.lineEdit_2.styleSheet()
        self.lineEdit_3.textChanged.connect(self.disable_ok)
        self.lineEdit_4.textChanged.connect(self.disable_ok)

        self.error_stylesheet = "border: 1px solid red;"

        self.buttonBox.setEnabled(True)
        self.set_existing_definitions()

    def disable_ok(self):
        enable = True
        btn_apply = self.buttonBox.button(QtWidgets.QDialogButtonBox.Ok)

        defWeek01 = self.dateEdit_startSemester.text().strip()
        dow = date.fromisoformat(defWeek01).isoweekday()
        if dow != 1:
            btn_apply.setEnabled(False)
            self.dateEdit_startSemester.setStyleSheet(self.error_stylesheet)
            self.dateEdit_startSemester.setToolTip(f"Given 'Monday, Week01' of {defWeek01} is not a Monday.")
            return
        else:
            self.dateEdit_startSemester.setToolTip(None)
            self.dateEdit_startSemester.setStyleSheet(self.dateEdit_stylesheet)

        line_edits = [self.lineEdit_2, self.lineEdit_3, self.lineEdit_4]

        for line_edit in line_edits:
            text = line_edit.text().strip()
            if text == "" or not _definitions.validate_date_format(text):
                line_edit.setStyleSheet(self.error_stylesheet)
                line_edit.setToolTip(f"Must match {_definitions.FORMAT_REGEX}")
                enable = False
            else:
                line_edit.setStyleSheet(self.lineEdit_styleSheet)
                line_edit.setToolTip(None)
                enable = enable and True

        btn_apply.setEnabled(enable)

    def set_existing_definitions(self):
        global definitions
        if len(definitions) > 0:
            self.setWindowTitle("Update Definitions")
            if 'defWeek01' in definitions:
                self.dateEdit_startSemester.setDate(QDate.fromString(definitions['defWeek01'], "yyyy-MM-dd"))
            if 'defOpenDate' in definitions:
                self.lineEdit_2.setText(definitions['defOpenDate'])
            if 'defDueDate' in definitions:
                self.lineEdit_3.setText(definitions['defDueDate'])
            if 'defCutoffDate' in definitions:
                self.lineEdit_4.setText(definitions['defCutoffDate'])

    def add_time_to_date_format(self, date_format, time):
        if date_format.find("%t") == -1:
            return date_format + " %t" + time
        else:
            return date_format

    def create_definitions(self):
        module_code: str = module
        ay: str = self.lineEdit_academicYear.text().strip()
        # start_semester: str = self.dateEdit_startSemester.text().strip()
        module_exists, error = checkModuleExists(module_code)
        if not error:
            if not module_exists:
                create_message_box(f"Module instance {module_code} in {ay} doesn't exist!")
                return

            defWeek01 = self.dateEdit_startSemester.text().strip()

            time = self.timeEdit.text().strip()
            defOpenDate = self.add_time_to_date_format(self.lineEdit_2.text().strip(), time)
            defDueDate = self.add_time_to_date_format(self.lineEdit_3.text().strip(), time)
            defCutoffDate = self.add_time_to_date_format(self.lineEdit_4.text().strip(), time)

            if self.create_files(module_code, ay):
                self.update_definitions_file(
                    academicYear=ay, # startSemester=start_semester)
                    defWeek01=defWeek01,
                    defOpenDate=defOpenDate,
                    defDueDate=defDueDate,
                    defCutoffDate=defCutoffDate)

    def update_definitions_file(self, **kwargs):
        global definitions
        if not updateDefinitionsFile(self.definitions_path, kwargs): # only give an error message if no error occurred
            update = len(definitions) > 0
            if (update):
                updated = "updated"
            else:
                updated = "created"
            create_message_box(f"Definitions {updated} successfully")
            self.parent().loadDefinitions()

    def create_files(self, module, academic_year):
        definitions_path, error = createDefinitionsFile(module, academic_year)
        if not error:
            self.definitions_path = definitions_path
            return True
        return False

class ViewAssignmentDialog(QDialog, Ui_Dialog_View_Assignment):
    def __init__(self, parent=None):
        super(ViewAssignmentDialog, self).__init__(parent)
        self.setupUi(self)
        assignments, error = getModuleAssignments(module)
        if not error:
            self.comboBox_assignments.addItems(assignments)
            self.pushButton_show.clicked.connect(self.display)
            self.comboBox_assignments.currentTextChanged.connect(self.generate_auto_next_week)
            self.textEdit_showFileContent.setReadOnly(False)
            self.checkBox_delete.clicked.connect(
            lambda: self.delete_assignment())
            self.checkBox_clone.setEnabled(False)
            self.checkBox_edit.setEnabled(False)
            self.checkBox_delete.setEnabled(False)
            self.textEdit_showFileContent.setReadOnly(True)
            self.pushButton_help.clicked.connect(self.print_name_help)
            self.pushButton_edit_help.clicked.connect(self.print_checkbox_help)
            self.pushButton_edit_help.setEnabled(False)
            self.disable_clone()
            self.buttonBox.button(QtWidgets.QDialogButtonBox.Ok).clicked.connect(self.do_ok)
        else:
            create_message_box("An error occurred, please try again")
            self.close()

    def do_ok(self):
        """ handles when ok is clicked """
        clone_checked = self.checkBox_clone.isChecked()
        clone_name = self.lineEdit_assName.text().strip()
        edit_checked = self.checkBox_edit.isChecked()
        edit_cloned = clone_checked and edit_checked
        success = True

        if clone_checked:
            success = self.clone_assignment()

        if success and edit_cloned:
            self.edit_assignment() # if edit_cloned is specified, only edit the cloned one if the clone was successful
        elif not edit_cloned and edit_checked:
            self.edit_assignment()
        elif not clone_checked and not edit_checked:
            self.close()

    def print_name_help(self):
        create_message_box("Enter the name for the new assignment if you want to clone the current one. " +
                "If it is a week number (e.g. w01 or week01), the weekNumber field of the cloned assignment will be updated, "
                + "and start, end and cutoff dates will be populated automatically if a definitions file exists")

    def print_checkbox_help(self):
        create_message_box("For cloning and editing, check the appropriate box and then OK. To delete, just check the delete box. " +
                    "To edit the cloned assignment, check both clone and edit and then OK")

    def disable_clone(self):
        if self.lineEdit_assName.text().strip() == "":
            self.checkBox_clone.setEnabled(False)
            self.checkBox_clone.setToolTip("Enter an assignment name first")
        else:
            self.checkBox_clone.setEnabled(self.textEdit_showFileContent.toPlainText() != "")
            self.checkBox_clone.setToolTip(None)

    """
        If the current assignment is named with a week_number the next assignment name is auto generated to be a week number
    """
    def generate_auto_next_week(self):
        text = self.comboBox_assignments.currentText()
        if _definitions.is_week_number(text):
            new_week = int(text[1:]) + 1
            if new_week < 10:
                new_week = f"0{new_week}"
            else:
                new_week_string = new_week
            new_week = f"w{new_week}"
            self.lineEdit_assName.setText(new_week)
        else:
            self.lineEdit_assName.setText("")

    def display(self):
        self.lineEdit_assName.textChanged.connect(self.disable_clone)
        self.comboBox_assignments.currentTextChanged.connect(self.generate_auto_next_week)
        self.generate_auto_next_week()
        text = self.comboBox_assignments.currentText()
        if not text == "":
            content, filename, error = getParams(module, text)
            if not error:
                self.textEdit_showFileContent.setText(content)
                self.submit_filepath = filename
                self.checkBox_edit.setEnabled(True)
                self.checkBox_delete.setEnabled(True)
                self.pushButton_edit_help.setEnabled(True)
        else:
            create_message_box("Choose an assignment first")

        self.disable_clone()

    def set_file_content(self, contents):
        contents_not_empty = contents != ""
        self.checkBox_clone.setEnabled(self.lineEdit_assName.text().strip() != "" and contents_not_empty)
        self.checkBox_edit.setEnabled(contents_not_empty)
        self.checkBox_delete.setEnabled(contents_not_empty)
        self.pushButton_edit_help.setEnabled(contents_not_empty)
        self.textEdit_showFileContent.setText(contents)

    def clone_assignment(self):
        if self.checkBox_clone.isChecked():
            assignment_name = self.lineEdit_assName.text().strip()

            if assignment_name != "":
                contents = self.validateYaml(self.textEdit_showFileContent.toPlainText())
                if contents is not None:
                    cloned, error = cloneAssignment(module, assignment_name, contents)
                    if not error:
                        create_message_box("Assignment cloned successfully")
                        self.comboBox_assignments.addItem(assignment_name)
                        self.comboBox_assignments.setCurrentText(assignment_name)
                        self.checkBox_clone.setChecked(False)
                        self.set_file_content(cloned['contents'])
                        self.submit_filepath = cloned['path']
                        return True

                return False
            else:
                create_message_box("If cloning this assignment, you must provide a new assignment name")
                return False

    def validateYaml(self, contents):
        try:
            yaml.safe_load(contents)
            # if loaded without throwing exception, it's ok
            return contents
        except yaml.YAMLError as err:
            err = format_exc()
            create_message_box(f"The entered assignment parameters are not valid: {err}")
            return None

    def edit_assignment(self):
        if self.checkBox_edit.isChecked():
            self.checkBox_edit.setChecked(False)
            contents = self.validateYaml(self.textEdit_showFileContent.toPlainText())
            if contents is not None:
                data: dict = yaml.safe_load(contents)
                dialog = CreateAssignmentDialog(self, existing_assignment=data, assignment_path=self.submit_filepath)
                dialog.show()
                return True
            return False

    def confirm_deletion(self):
        ret = QMessageBox.question(self,'', "Are you sure to delete this assignment?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        return ret == QMessageBox.Yes

    def delete_assignment(self):
        if self.checkBox_delete.isChecked():
            if self.confirm_deletion():
                assignment = self.comboBox_assignments.currentText()
                error = deleteAssignment(module, assignment)
                if not error:
                    create_message_box("Assignment deleted successfully")
                    self.comboBox_assignments.removeItem(self.comboBox_assignments.findText(assignment))
                    self.checkBox_delete.setChecked(False)
                    self.set_file_content("")
                    if self.comboBox_assignments.count() == 0:
                        self.close()

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    exit_code = app.exec_()
    sys.exit(exit_code)
