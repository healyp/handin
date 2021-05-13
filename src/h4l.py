import re
import sys
import logging
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import QDate, QRegExp, QDateTime
from PyQt5.QtGui import QRegExpValidator
from PyQt5.QtWidgets import QMainWindow, QDialog, QMessageBox, QLineEdit, QGroupBox, QTableWidgetItem

from traceback import format_exc

from getmac import get_mac_address as gma

from ui.impl.createOneOffAssignment_dialog import Ui_Dialog as Ui_Dialog_CreateOneOffAssignment
from ui.impl.create_repeat_assignments_dialog import Ui_Dialog as Ui_Dialog_Create_Repeat_Assignments
from ui.impl.handin_lecturer_dialog import Ui_Dialog as Ui_Dialog_main
from ui.impl.manage_student_marks_dialog import Ui_Dialog as Ui_Dialog_Manage_Student_Marks
from ui.impl.create_definitions_dialog import Ui_Dialog as Ui_Dialog_Create_Definitions
from ui.impl.clone_previous_assignment_dialog import Ui_Dialog as Ui_Dialog_Clone_Assignment
from ui.impl.handin_lecturer_login import Ui_MainWindow as Ui_MainWindow_Lecturer_Login
from ui.impl.handin_lecturer_dialog import Ui_Dialog as Ui_Main_Lecturer_Dialog
from ui.impl.pick_module_dialog import Ui_Dialog as Ui_Dialog_pick_module

# from dateutil.parser import parse
from datetime import date

import const
from const import whatAY, containsValidDay

from h4l_requests import *

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(asctime)s %(message)s')

lecturer = ""
module = ""
password = ""
definitions = {}

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
    if(ret == QMessageBox.Yes):
        trustMacAddress(lecturer, "true")
    elif(ret == QMessageBox.No):
        trustMacAddress(lecturer, "false")
    elif(ret == QMessageBox.Close):
        disconnect()
        sys.exit(0)

def isMatchRegex(regex: str, text: str) -> bool:
    return bool(re.match(regex, text, re.IGNORECASE))

def validDefaultDate(given: str):
    if containsValidDay(given) and re.search("%w(\s*[+-]\s*\d+)?", given, re.IGNORECASE):
        return(True)
    else:
        return(False)

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
            if(authenticated):
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
            if(len(modules) == 0):
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
        dialog = MainLecturerDialog()
        dialog.show()


class MainLecturerDialog(QDialog, Ui_Main_Lecturer_Dialog):
    def __init__(self, parent=None):
        super(MainLecturerDialog, self).__init__()
        self.setupUi(self)
        self.pushButton.clicked.connect(lambda: self.manage_student_marks())
        self.pushButton_2.clicked.connect(lambda: self.createOneOffAssignment())
        self.pushButton_3.clicked.connect(lambda: self.create_repeat_assignments())
        self.pushButton_4.clicked.connect(lambda: self.create_definitions())
        self.pushButton_5.clicked.connect(lambda: self.clone_assignment())
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
        dialog = CreateOneOffAssignmentDialog(self)
        dialog.show()

    def create_repeat_assignments(self):
        dialog = CreateRepeatAssignmentsDialog(self)
        dialog.show()

    def create_definitions(self):
        dialog = CreateDefinitionsDialog(self)
        dialog.show()

    def clone_assignment(self):
        dialog = CloneAssignmentDialog(self)
        dialog.show()


class ManageStudentMarksDialog(QDialog, Ui_Dialog_Manage_Student_Marks):
    def __init__(self, parent=None):
        super(ManageStudentMarksDialog, self).__init__(parent)
        self.setupUi(self)
        # self.comboBox_moduleCode.addItems(getModuleCodes())
        self.comboBox_week.addItems(["w01", "w02", "w03", "w04", "w05", "w06", "w07",
                                    "w08", "w09", "w10", "w11", "w12", "w13"])
        self.comboBox_week.currentTextChanged.connect(self.update_table)
        # self.comboBox_moduleCode.currentTextChanged.connect(self.update_table)
        self.tableWidget.setEnabled(False)
        self.update_table()
        self.label_module.setText(module)

    def columnFromLabel(self, label) -> int:
        model = self.tableWidget.horizontalHeader().model()
        for column in range(model.columnCount()):
            if model.headerData(column, QtCore.Qt.Horizontal) == label:
                return column
        return -1

    def update_table(self):
        """update table widget - signal"""
        try:
            horizontal_header_labels = ["Student ID"]
            test_items, error = get_all_test_items(module, self.comboBox_week.currentText())

            if not error:
                horizontal_header_labels += test_items
                horizontal_header_labels += ["Attempts Left", "Total Marks"]
                self.tableWidget.setColumnCount(len(horizontal_header_labels))
                student_ids, error1 = get_all_student_ids(module)

                if not error1:
                    self.tableWidget.setRowCount(len(student_ids))
                    self.tableWidget.setHorizontalHeaderLabels(horizontal_header_labels)

                    # write student ids
                    col = 0
                    for _id in student_ids:
                        self.tableWidget.setItem(col, 0, QTableWidgetItem(_id))
                        col += 1
                    # write attendance, compilation, test1, test2 ....
                    vars = {}
                    try:
                        for row in range(self.tableWidget.rowCount()):
                            student_id = self.tableWidget.item(row, 0).text().strip()
                            week_number = self.comboBox_week.currentText()
                            data, error = get_vars(module, week_number, student_id)
                            if error:
                                return

                            vars[(module, week_number, student_id)] = data
                            for label in horizontal_header_labels[1:-2]:
                                if label in data.keys():
                                    self.tableWidget.setItem(row, self.columnFromLabel(label),
                                                             QTableWidgetItem(str(data[label])))
                    except Exception as e:
                        e = format_exc()
                        print(e)
                    # write attempts left and total marks
                    try:
                        for row in range(self.tableWidget.rowCount()):
                            student_id = self.tableWidget.item(row, 0).text().strip()
                            week_number = self.comboBox_week.currentText()
                            vars_tuple = (module, week_number, student_id)
                            if not vars_tuple in vars:
                                data, error = get_vars(module, week_number, student_id)
                                if error:
                                    return
                                vars[vars_tuple] = data
                            else:
                                data = vars[vars_tuple]
                            if "attemptsLeft" in data.keys():
                                self.tableWidget.setItem(row, self.columnFromLabel("Attempts Left"),
                                                         QTableWidgetItem(str(data["attemptsLeft"])))
                            if "marks" in data.keys():
                                self.tableWidget.setItem(row, self.columnFromLabel("Total Marks"),
                                                         QTableWidgetItem(str(data["marks"])))
                    except Exception as e:
                        e = format_exc()
                        print(e)

        except Exception as e:
            print(e)
            self.tableWidget.clear()


class CreateOneOffAssignmentDialog(QDialog, Ui_Dialog_CreateOneOffAssignment):
    def __init__(self, parent=None):
        super(CreateOneOffAssignmentDialog, self).__init__(parent)
        self.setupUi(self)
        self.label_module.setText(module)
        self.dateTimeEdit_startDay.setDisplayFormat("yyyy-MM-dd HH:mm")
        self.dateTimeEdit_endDay.setDisplayFormat("yyyy-MM-dd HH:mm")
        self.dateTimeEdit_cutoffDay.setDisplayFormat("yyyy-MM-dd HH:mm")
        self.dateTimeEdit_startDay.setDateTime(QDateTime.currentDateTime())
        self.dateTimeEdit_endDay.setDateTime(QDateTime.currentDateTime())
        self.dateTimeEdit_cutoffDay.setDateTime(QDateTime.currentDateTime())
        # only allow Integers for PenaltyPerDay and totalAttempts
        # self.lineEdit_penaltyPerDay.setPlaceholderText('0')
        # self.lineEdit_penaltyPerDay.setValidator(QRegExpValidator(regex))
        # self.lineEdit_totalAttempts.setValidator(QRegExpValidator(regex))
        self.spinBox_penaltyPerDay.setValue(7)
        self.spinBox_totalAttempts.setValue(10)
        regex = QRegExp("\\d+")
        self.lineEdit_attendance_marks.setValidator(QRegExpValidator(regex))
        self.lineEdit_compilation_marks.setValidator(QRegExpValidator(regex))
        self.lineEdit_test1_marks.setValidator(QRegExpValidator(regex))
        self.lineEdit_test2_marks.setValidator(QRegExpValidator(regex))
        self.lineEdit_test3_marks.setValidator(QRegExpValidator(regex))
        self.lineEdit_test4_marks.setValidator(QRegExpValidator(regex))
        self.accepted.connect(lambda: self.createOneOffAssignment())
        self.buttonBox.setEnabled(False)
        # self.comboBox_moduleCode.editTextChanged.connect(self.disable_buttonbox)
        # register listeners for all line edits
        for line_edit in self.findChildren(QLineEdit):
            line_edit.textChanged.connect(self.disable_buttonbox)
        # register listeners for all group boxes
        for group_box in self.findChildren(QGroupBox):
            group_box.toggled.connect(self.disable_buttonbox)
            group_box.toggled.connect(self.update_total_marks)
            group_box.toggled.connect(self.disable_groupbox)
        self.lineEdit_attendance_marks.textChanged.connect(self.update_total_marks)
        self.lineEdit_compilation_marks.textChanged.connect(self.update_total_marks)
        self.lineEdit_test1_marks.textChanged.connect(self.update_total_marks)
        self.lineEdit_test2_marks.textChanged.connect(self.update_total_marks)
        self.lineEdit_test3_marks.textChanged.connect(self.update_total_marks)
        self.lineEdit_test4_marks.textChanged.connect(self.update_total_marks)
        # set up initial available module codes
        # self.comboBox_moduleCode.addItems(getModuleCodes())
        # set up week numbers
        # self.comboBox_weekNumber.addItems(["w01", "w02", "w03", "w04", "w05", "w06",
        #                                 "w07", "w08", "w09", "w10", "w11", "w12", "w13"])
        self.groupBox_customTest1.setCheckable(False)
        self.groupBox_customTest1.setChecked(True)
        self.checkBox_test1_inputDataFile.stateChanged.connect(
            lambda: self.add_file_with_check_box(self.checkBox_test1_inputDataFile, self.label_test1_inputDataFile))
        self.checkBox_test2_inputDataFile.stateChanged.connect(
            lambda: self.add_file_with_check_box(self.checkBox_test2_inputDataFile, self.label_test2_inputDataFile))
        self.checkBox_test3_inputDataFile.stateChanged.connect(
            lambda: self.add_file_with_check_box(self.checkBox_test3_inputDataFile, self.label_test3_inputDataFile))
        self.checkBox_test4_inputDataFile.stateChanged.connect(
            lambda: self.add_file_with_check_box(self.checkBox_test4_inputDataFile, self.label_test4_inputDataFile))

        self.checkBox_test1_answerFile.stateChanged.connect(
            lambda: self.add_file_with_check_box(self.checkBox_test1_answerFile, self.label_test1_answerFile))
        self.checkBox_test2_answerFile.stateChanged.connect(
            lambda: self.add_file_with_check_box(self.checkBox_test2_answerFile, self.label_test2_answerFile))
        self.checkBox_test3_answerFile.stateChanged.connect(
            lambda: self.add_file_with_check_box(self.checkBox_test3_answerFile, self.label_test3_answerFile))
        self.checkBox_test4_answerFile.stateChanged.connect(
            lambda: self.add_file_with_check_box(self.checkBox_test4_answerFile, self.label_test4_answerFile))

        self.checkBox_test1_filterFile.stateChanged.connect(
            lambda: self.add_file_with_check_box(self.checkBox_test1_filterFile, self.label_test1_filterFile,
                                                 is_filter=True, filter_line_edit=self.lineEdit_test1_filterCommand))
        self.checkBox_test2_filterFile.stateChanged.connect(
            lambda: self.add_file_with_check_box(self.checkBox_test2_filterFile, self.label_test2_filterFile,
                                                 is_filter=True, filter_line_edit=self.lineEdit_test2_filterCommand))
        self.checkBox_test3_filterFile.stateChanged.connect(
            lambda: self.add_file_with_check_box(self.checkBox_test3_filterFile, self.label_test3_filterFile,
                                                 is_filter=True, filter_line_edit=self.lineEdit_test3_filterCommand))
        self.checkBox_test4_filterFile.stateChanged.connect(
            lambda: self.add_file_with_check_box(self.checkBox_test4_filterFile, self.label_test4_filterFile,
                                                 is_filter=True, filter_line_edit=self.lineEdit_test4_filterCommand))

        self.lineEdit_test1_filterCommand.setDisabled(True)
        self.lineEdit_test2_filterCommand.setDisabled(True)
        self.lineEdit_test3_filterCommand.setDisabled(True)
        self.lineEdit_test4_filterCommand.setDisabled(True)
        self.checkBox_test1_filterFile.stateChanged.connect(self.disable_buttonbox)
        self.checkBox_test2_filterFile.stateChanged.connect(self.disable_buttonbox)
        self.checkBox_test3_filterFile.stateChanged.connect(self.disable_buttonbox)
        self.checkBox_test4_filterFile.stateChanged.connect(self.disable_buttonbox)

    def add_file_with_check_box(self, check_box, label, is_filter=False, filter_line_edit=None):
        """add data/answer/filter file with check box -- signal"""
        if check_box.isChecked():
            dialog = QtWidgets.QFileDialog()
            dialog.setFileMode(QtWidgets.QFileDialog.AnyFile)
            filename, file_type = QtWidgets.QFileDialog.getOpenFileName(
                self, "Choose file", "./", "All Files (*)")
            label.setText(filename)
            if is_filter and (filter_line_edit is not None):
                filter_line_edit.setEnabled(True)
        else:
            label.setText("")
            if filter_line_edit is not None:
                filter_line_edit.setEnabled(False)

    def disable_buttonbox(self):
        """disable button box -- signal"""
        self.buttonBox.setEnabled(True)
        line_edits: list = [le for le in self.findChildren(QLineEdit)]
        for line_edit in line_edits:
            if line_edit.isEnabled():
                if not len(line_edit.text()) > 0:
                    self.buttonBox.setEnabled(False)
                    return

    def update_total_marks(self):
        """update total marks -- signal"""
        total_marks: int = self.get_total_marks()
        self.label_totalMarks.setText(str(total_marks))

    def disable_groupbox(self):
        """disable group box -- signal,"""
        if not self.groupBox_customTest2.isChecked():
            self.groupBox_customTest3.setChecked(False)
            self.groupBox_customTest4.setChecked(False)
        if not self.groupBox_customTest3.isChecked():
            self.groupBox_customTest4.setChecked(False)

    def get_total_marks(self) -> int:
        attendance = int(self.lineEdit_attendance_marks.text()) if len(self.lineEdit_attendance_marks.text()) > 0 and self.groupBox_attendance.isChecked() else 0
        compilation = int(self.lineEdit_compilation_marks.text()) if len(self.lineEdit_compilation_marks.text()) > 0 and self.groupBox_compilation.isChecked() else 0
        test1 = int(self.lineEdit_test1_marks.text()) if len(self.lineEdit_test1_marks.text()) > 0 else 0
        test2 = int(self.lineEdit_test2_marks.text()) if len(self.lineEdit_test2_marks.text()) > 0 and self.groupBox_customTest2.isChecked() else 0
        test3 = int(self.lineEdit_test3_marks.text()) if len(self.lineEdit_test3_marks.text()) > 0 and self.groupBox_customTest3.isChecked() else 0
        test4 = int(self.lineEdit_test4_marks.text()) if len(self.lineEdit_test4_marks.text()) > 0 and self.groupBox_customTest4.isChecked() else 0
        return attendance + compilation + test1 + test2 + test3 + test4

    def createOneOffAssignment(self):
        # module_code = self.comboBox_moduleCode.currentText().strip()
        module_code = module
        assName = self.lineEdit_assName.text().strip()
        start_day = self.dateTimeEdit_startDay.text().strip()
        end_day = self.dateTimeEdit_startDay.text().strip()
        cutoff_day = self.dateTimeEdit_cutoffDay.text().strip()
        # penalty_per_day = int(self.lineEdit_penaltyPerDay.text().strip())
        # total_attempts = int(self.lineEdit_totalAttempts.text().strip())
        collection_filename = self.lineEdit_collectFilename.text().strip()
        tests = {}
        if self.groupBox_attendance.isChecked():
            tag = self.lineEdit_attendance_tag.text().strip()
            marks = int(self.lineEdit_attendance_marks.text().strip())
            tests["attendance"] = {"tag": tag, "marks": marks}
        if self.groupBox_compilation.isChecked():
            tag = self.lineEdit_compilation_tag.text().strip()
            marks = int(self.lineEdit_compilation_marks.text().strip())
            command = self.lineEdit_compilation_command.text().strip()
            tests["compilation"] = {"tag": tag, "marks": marks, "command": command}
        tag = self.lineEdit_test1_tag.text().strip()
        marks = int(self.lineEdit_test1_marks.text().strip())
        command = self.lineEdit_test1_command.text().strip()
        inputDataFile = self.label_test1_inputDataFile.text().strip()
        answerFile = self.label_test1_answerFile.text().strip()
        filterFile = self.label_test1_filterFile.text().strip()
        filterCommand = self.lineEdit_test1_filterCommand.text().strip()
        tests["test1"] = {"tag": tag, "marks": marks, "command": command, "inputDataFile": inputDataFile,
                          "answerFile": answerFile, "filterFile": filterFile, "filterCommand": filterCommand}
        if self.groupBox_customTest2.isChecked():
            tag = self.lineEdit_test2_tag.text().strip()
            marks = int(self.lineEdit_test2_marks.text().strip())
            command = self.lineEdit_test2_command.text().strip()
            inputDataFile = self.label_test2_inputDataFile.text().strip()
            answerFile = self.label_test2_answerFile.text().strip()
            filterFile = self.label_test2_filterFile.text().strip()
            filterCommand = self.lineEdit_test2_filterCommand.text().strip()
            tests["test2"] = {"tag": tag, "marks": marks, "command": command, "inputDataFile": inputDataFile,
                              "answerFile": answerFile, "filterFile": filterFile, "filterCommand": filterCommand}
        if self.groupBox_customTest3.isChecked():
            tag = self.lineEdit_test3_tag.text().strip()
            marks = int(self.lineEdit_test3_marks.text().strip())
            command = self.lineEdit_test3_command.text().strip()
            inputDataFile = self.label_test3_inputDataFile.text().strip()
            answerFile = self.label_test3_answerFile.text().strip()
            filterFile = self.label_test3_filterFile.text().strip()
            filterCommand = self.lineEdit_test3_filterCommand.text().strip()
            tests["test3"] = {"tag": tag, "marks": marks, "command": command, "inputDataFile": inputDataFile,
                              "answerFile": answerFile, "filterFile": filterFile, "filterCommand": filterCommand}
        if self.groupBox_customTest4.isChecked():
            tag = self.lineEdit_test4_tag.text().strip()
            marks = int(self.lineEdit_test4_marks.text().strip())
            command = self.lineEdit_test4_command.text().strip()
            inputDataFile = self.label_test4_inputDataFile.text().strip()
            answerFile = self.label_test4_answerFile.text().strip()
            filterFile = self.label_test4_filterFile.text().strip()
            filterCommand = self.lineEdit_test4_filterCommand.text().strip()
            tests["test4"] = {"tag": tag, "marks": marks, "command": command, "inputDataFile": inputDataFile,
                              "answerFile": answerFile, "filterFile": filterFile, "filterCommand": filterCommand}

        week_exists, error = checkWeekExists(module_code, week_number)
        if not error:
            if not week_exists:
                if self.create_week_directory(module_code, week_number):
                    self.update_params_file(
                        moduleCode=module_code, weekNumber=week_number, startDay=start_day,
                        endDay=end_day, cutoffDay=cutoff_day, penaltyPerDay=penalty_per_day,
                        totalAttempts=total_attempts, collectionFilename=collection_filename, tests=tests)
            else:
                create_message_box(f"{week_number} for module {module_code} already exists!")

    def create_week_directory(self, module, week_number):
        params_path, error = createWeekDirectory(module, week_number)
        if not error:
            self.params_path = params_path
            return True
        return False

    def update_params_file(self, **kwargs):
        updateParamsFile(self.params_path, kwargs)


class CreateRepeatAssignmentsDialog(QDialog, Ui_Dialog_Create_Repeat_Assignments):
    def __init__(self, parent=None):
        super(CreateRepeatAssignmentsDialog, self).__init__(parent)
        self.setupUi(self)
        self.label_module.setText(module)
        self.dateTimeEdit_startDay.setDisplayFormat("yyyy-MM-dd HH:mm")
        self.dateTimeEdit_endDay.setDisplayFormat("yyyy-MM-dd HH:mm")
        self.dateTimeEdit_cutoffDay.setDisplayFormat("yyyy-MM-dd HH:mm")
        self.dateTimeEdit_startDay.setDateTime(QDateTime.currentDateTime())
        self.dateTimeEdit_endDay.setDateTime(QDateTime.currentDateTime())
        self.dateTimeEdit_cutoffDay.setDateTime(QDateTime.currentDateTime())
        # only allow Integers for PenaltyPerDay and totalAttempts
        # self.lineEdit_penaltyPerDay.setPlaceholderText('0')
        # self.lineEdit_penaltyPerDay.setValidator(QRegExpValidator(regex))
        # self.lineEdit_totalAttempts.setValidator(QRegExpValidator(regex))
        self.spinBox_penaltyPerDay.setValue(7)
        self.spinBox_totalAttempts.setValue(10)
        regex = QRegExp("\\d+")
        self.lineEdit_attendance_marks.setValidator(QRegExpValidator(regex))
        self.lineEdit_compilation_marks.setValidator(QRegExpValidator(regex))
        self.lineEdit_test1_marks.setValidator(QRegExpValidator(regex))
        self.lineEdit_test2_marks.setValidator(QRegExpValidator(regex))
        self.lineEdit_test3_marks.setValidator(QRegExpValidator(regex))
        self.lineEdit_test4_marks.setValidator(QRegExpValidator(regex))
        self.accepted.connect(lambda: self.create_weekly_assignment())
        self.buttonBox.setEnabled(False)
        # self.comboBox_moduleCode.editTextChanged.connect(self.disable_buttonbox)
        # register listeners for all line edits
        for line_edit in self.findChildren(QLineEdit):
            line_edit.textChanged.connect(self.disable_buttonbox)
        # register listeners for all group boxes
        for group_box in self.findChildren(QGroupBox):
            group_box.toggled.connect(self.disable_buttonbox)
            group_box.toggled.connect(self.update_total_marks)
            group_box.toggled.connect(self.disable_groupbox)
        self.lineEdit_attendance_marks.textChanged.connect(self.update_total_marks)
        self.lineEdit_compilation_marks.textChanged.connect(self.update_total_marks)
        self.lineEdit_test1_marks.textChanged.connect(self.update_total_marks)
        self.lineEdit_test2_marks.textChanged.connect(self.update_total_marks)
        self.lineEdit_test3_marks.textChanged.connect(self.update_total_marks)
        self.lineEdit_test4_marks.textChanged.connect(self.update_total_marks)
        # set up initial available module codes
        # self.comboBox_moduleCode.addItems(getModuleCodes())
        # set up week numbers
        self.comboBox_weekNumber.addItems(["w01", "w02", "w03", "w04", "w05", "w06",
                                           "w07", "w08", "w09", "w10", "w11", "w12", "w13"])
        self.groupBox_customTest1.setCheckable(False)
        self.groupBox_customTest1.setChecked(True)
        self.checkBox_test1_inputDataFile.stateChanged.connect(
            lambda: self.add_file_with_check_box(self.checkBox_test1_inputDataFile, self.label_test1_inputDataFile))
        self.checkBox_test2_inputDataFile.stateChanged.connect(
            lambda: self.add_file_with_check_box(self.checkBox_test2_inputDataFile, self.label_test2_inputDataFile))
        self.checkBox_test3_inputDataFile.stateChanged.connect(
            lambda: self.add_file_with_check_box(self.checkBox_test3_inputDataFile, self.label_test3_inputDataFile))
        self.checkBox_test4_inputDataFile.stateChanged.connect(
            lambda: self.add_file_with_check_box(self.checkBox_test4_inputDataFile, self.label_test4_inputDataFile))

        self.checkBox_test1_answerFile.stateChanged.connect(
            lambda: self.add_file_with_check_box(self.checkBox_test1_answerFile, self.label_test1_answerFile))
        self.checkBox_test2_answerFile.stateChanged.connect(
            lambda: self.add_file_with_check_box(self.checkBox_test2_answerFile, self.label_test2_answerFile))
        self.checkBox_test3_answerFile.stateChanged.connect(
            lambda: self.add_file_with_check_box(self.checkBox_test3_answerFile, self.label_test3_answerFile))
        self.checkBox_test4_answerFile.stateChanged.connect(
            lambda: self.add_file_with_check_box(self.checkBox_test4_answerFile, self.label_test4_answerFile))

        self.checkBox_test1_filterFile.stateChanged.connect(
            lambda: self.add_file_with_check_box(self.checkBox_test1_filterFile, self.label_test1_filterFile,
                                                 is_filter=True, filter_line_edit=self.lineEdit_test1_filterCommand))
        self.checkBox_test2_filterFile.stateChanged.connect(
            lambda: self.add_file_with_check_box(self.checkBox_test2_filterFile, self.label_test2_filterFile,
                                                 is_filter=True, filter_line_edit=self.lineEdit_test2_filterCommand))
        self.checkBox_test3_filterFile.stateChanged.connect(
            lambda: self.add_file_with_check_box(self.checkBox_test3_filterFile, self.label_test3_filterFile,
                                                 is_filter=True, filter_line_edit=self.lineEdit_test3_filterCommand))
        self.checkBox_test4_filterFile.stateChanged.connect(
            lambda: self.add_file_with_check_box(self.checkBox_test4_filterFile, self.label_test4_filterFile,
                                                 is_filter=True, filter_line_edit=self.lineEdit_test4_filterCommand))

        self.lineEdit_test1_filterCommand.setDisabled(True)
        self.lineEdit_test2_filterCommand.setDisabled(True)
        self.lineEdit_test3_filterCommand.setDisabled(True)
        self.lineEdit_test4_filterCommand.setDisabled(True)
        self.checkBox_test1_filterFile.stateChanged.connect(self.disable_buttonbox)
        self.checkBox_test2_filterFile.stateChanged.connect(self.disable_buttonbox)
        self.checkBox_test3_filterFile.stateChanged.connect(self.disable_buttonbox)
        self.checkBox_test4_filterFile.stateChanged.connect(self.disable_buttonbox)

    def add_file_with_check_box(self, check_box, label, is_filter=False, filter_line_edit=None):
        """add data/answer/filter file with check box -- signal"""
        if check_box.isChecked():
            dialog = QtWidgets.QFileDialog()
            dialog.setFileMode(QtWidgets.QFileDialog.AnyFile)
            filename, file_type = QtWidgets.QFileDialog.getOpenFileName(
                self, "Choose file", "./", "All Files (*)")
            label.setText(filename)
            if is_filter and (filter_line_edit is not None):
                filter_line_edit.setEnabled(True)
        else:
            label.setText("")
            if filter_line_edit is not None:
                filter_line_edit.setEnabled(False)

    def disable_buttonbox(self):
        """disable button box -- signal"""
        self.buttonBox.setEnabled(True)
        line_edits: list = [le for le in self.findChildren(QLineEdit)]
        for line_edit in line_edits:
            if line_edit.isEnabled():
                if not len(line_edit.text()) > 0:
                    self.buttonBox.setEnabled(False)
                    return

    def update_total_marks(self):
        """update total marks -- signal"""
        total_marks: int = self.get_total_marks()
        self.label_totalMarks.setText(str(total_marks))

    def disable_groupbox(self):
        """disable group box -- signal,"""
        if not self.groupBox_customTest2.isChecked():
            self.groupBox_customTest3.setChecked(False)
            self.groupBox_customTest4.setChecked(False)
        if not self.groupBox_customTest3.isChecked():
            self.groupBox_customTest4.setChecked(False)

    def get_total_marks(self) -> int:
        attendance = int(self.lineEdit_attendance_marks.text()) if len(self.lineEdit_attendance_marks.text()) > 0 and self.groupBox_attendance.isChecked() else 0
        compilation = int(self.lineEdit_compilation_marks.text()) if len(self.lineEdit_compilation_marks.text()) > 0 and self.groupBox_compilation.isChecked() else 0
        test1 = int(self.lineEdit_test1_marks.text()) if len(self.lineEdit_test1_marks.text()) > 0 else 0
        test2 = int(self.lineEdit_test2_marks.text()) if len(self.lineEdit_test2_marks.text()) > 0 and self.groupBox_customTest2.isChecked() else 0
        test3 = int(self.lineEdit_test3_marks.text()) if len(self.lineEdit_test3_marks.text()) > 0 and self.groupBox_customTest3.isChecked() else 0
        test4 = int(self.lineEdit_test4_marks.text()) if len(self.lineEdit_test4_marks.text()) > 0 and self.groupBox_customTest4.isChecked() else 0
        return attendance + compilation + test1 + test2 + test3 + test4

    def create_weekly_assignment(self):
        # module_code = self.comboBox_moduleCode.currentText().strip()
        module_code = module
        week_number = self.comboBox_weekNumber.currentText().strip()
        start_day = self.dateTimeEdit_startDay.text().strip()
        end_day = self.dateTimeEdit_startDay.text().strip()
        cutoff_day = self.dateTimeEdit_cutoffDay.text().strip()
        penalty_per_day = int(self.lineEdit_penaltyPerDay.text().strip())
        total_attempts = int(self.lineEdit_totalAttempts.text().strip())
        collection_filename = self.lineEdit_collectFilename.text().strip()
        tests = {}
        if self.groupBox_attendance.isChecked():
            tag = self.lineEdit_attendance_tag.text().strip()
            marks = int(self.lineEdit_attendance_marks.text().strip())
            tests["attendance"] = {"tag": tag, "marks": marks}
        if self.groupBox_compilation.isChecked():
            tag = self.lineEdit_compilation_tag.text().strip()
            marks = int(self.lineEdit_compilation_marks.text().strip())
            command = self.lineEdit_compilation_command.text().strip()
            tests["compilation"] = {"tag": tag, "marks": marks, "command": command}
        tag = self.lineEdit_test1_tag.text().strip()
        marks = int(self.lineEdit_test1_marks.text().strip())
        command = self.lineEdit_test1_command.text().strip()
        inputDataFile = self.label_test1_inputDataFile.text().strip()
        answerFile = self.label_test1_answerFile.text().strip()
        filterFile = self.label_test1_filterFile.text().strip()
        filterCommand = self.lineEdit_test1_filterCommand.text().strip()
        tests["test1"] = {"tag": tag, "marks": marks, "command": command, "inputDataFile": inputDataFile,
                          "answerFile": answerFile, "filterFile": filterFile, "filterCommand": filterCommand}
        if self.groupBox_customTest2.isChecked():
            tag = self.lineEdit_test2_tag.text().strip()
            marks = int(self.lineEdit_test2_marks.text().strip())
            command = self.lineEdit_test2_command.text().strip()
            inputDataFile = self.label_test2_inputDataFile.text().strip()
            answerFile = self.label_test2_answerFile.text().strip()
            filterFile = self.label_test2_filterFile.text().strip()
            filterCommand = self.lineEdit_test2_filterCommand.text().strip()
            tests["test2"] = {"tag": tag, "marks": marks, "command": command, "inputDataFile": inputDataFile,
                              "answerFile": answerFile, "filterFile": filterFile, "filterCommand": filterCommand}
        if self.groupBox_customTest3.isChecked():
            tag = self.lineEdit_test3_tag.text().strip()
            marks = int(self.lineEdit_test3_marks.text().strip())
            command = self.lineEdit_test3_command.text().strip()
            inputDataFile = self.label_test3_inputDataFile.text().strip()
            answerFile = self.label_test3_answerFile.text().strip()
            filterFile = self.label_test3_filterFile.text().strip()
            filterCommand = self.lineEdit_test3_filterCommand.text().strip()
            tests["test3"] = {"tag": tag, "marks": marks, "command": command, "inputDataFile": inputDataFile,
                              "answerFile": answerFile, "filterFile": filterFile, "filterCommand": filterCommand}
        if self.groupBox_customTest4.isChecked():
            tag = self.lineEdit_test4_tag.text().strip()
            marks = int(self.lineEdit_test4_marks.text().strip())
            command = self.lineEdit_test4_command.text().strip()
            inputDataFile = self.label_test4_inputDataFile.text().strip()
            answerFile = self.label_test4_answerFile.text().strip()
            filterFile = self.label_test4_filterFile.text().strip()
            filterCommand = self.lineEdit_test4_filterCommand.text().strip()
            tests["test4"] = {"tag": tag, "marks": marks, "command": command, "inputDataFile": inputDataFile,
                              "answerFile": answerFile, "filterFile": filterFile, "filterCommand": filterCommand}

        week_exists, error = checkWeekExists(module_code, week_number)
        if not error:
            if not week_exists:
                if self.create_week_directory(module_code, week_number):
                    self.update_params_file(
                        moduleCode=module_code, weekNumber=week_number, startDay=start_day,
                        endDay=end_day, cutoffDay=cutoff_day, penaltyPerDay=penalty_per_day,
                        totalAttempts=total_attempts, collectionFilename=collection_filename, tests=tests)
            else:
                create_message_box(f"{week_number} for module {module_code} already exists!")

    def create_week_directory(self, module, week_number):
        params_path, error = createWeekDirectory(module, week_number)
        if not error:
            self.params_path = params_path
            return True
        return False

    def update_params_file(self, **kwargs):
        updateParamsFile(self.params_path, kwargs)

class CreateDefinitionsDialog(QDialog, Ui_Dialog_Create_Definitions):
    def __init__(self, parent=None):
        super(CreateDefinitionsDialog, self).__init__(parent)
        self.setupUi(self)
        self.dateEdit_startSemester.setDisplayFormat("yyyy-MM-dd")
        self.dateEdit_startSemester.setDate(QDate.currentDate())
        # Academic Year format: 2020-2021-S1
        self.regexAY = "\\d{4}-\\d{4}-S[1,2]"
        # self.lineEdit_academicYear.setPlaceholderText(whatAY())
        self.lineEdit_academicYear.setText(whatAY())
        self.accepted.connect(lambda: self.create_definitions())
        self.buttonBox.setEnabled(False)
        # self.lineEdit.textChanged.connect(self.disable_buttonbox)
        self.label_module.setText(module)
        # self.lineEdit_2.textChanged.connect(self.disable_buttonbox)
        # self.lineEdit_3.textChanged.connect(self.disable_buttonbox)
        # self.lineEdit_4.textChanged.connect(self.disable_buttonbox)
        self.buttonBox.setEnabled(True)
        self.set_existing_definitions()

    # def disable_buttonbox(self):
    #     # len(self.lineEdit.text()) > 0 and \
    #     # goodcode = isMatchRegex(regex=ModCodeRE, text=module)
    #     # self.buttonBox.setEnabled(goodcode)
    #     # print(goodcode)
    #     # check three dates for validity
    #     allValid = validDefaultDate(self.lineEdit_2.text()) and validDefaultDate(self.lineEdit_3.text()) and validDefaultDate(self.lineEdit_4.text())
    #     print(allValid)
    #     self.buttonBox.setEnabled(allValid)

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
            dow = date.fromisoformat(defWeek01).isoweekday()
            if dow != 1:
                create_message_box(f"Given 'Monday, Week01' of {defWeek01} is not a Monday.")
                return

            defOpenDate = self.lineEdit_2.text().strip()
            defDueDate = self.lineEdit_3.text().strip()
            defCutoffDate = self.lineEdit_4.text().strip()

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

class CloneAssignmentDialog(QDialog, Ui_Dialog_Clone_Assignment):
    def __init__(self, parent=None):
        super(CloneAssignmentDialog, self).__init__(parent)
        self.setupUi(self)
        assignments, error = getModuleAssignments(module)
        if not error:
            self.comboBox_assignments.addItems(assignments)
            self.pushButton_show.clicked.connect(self.display)
#        self.comboBox_assignments.currentTextChanged.connect(self.update_table)
            self.textEdit_showFileContent.setReadOnly(False)
            self.checkBox_clone.stateChanged.connect(
            lambda: self.file_save(self))

    def display(self):
        content, filename, error = getParams(module, self.comboBox_assignments.currentText())
        if not error:
            self.textEdit_showFileContent.setText(content)
            self.submit_filepath = filename

    def file_save(self, check_box):
        saveFile(module, self.lineEdit_assName.text().strip())


    # TODO cloning may need to be implemented, doesn't seem to be done here

    # def clone_assignment(self, check_box):
    #     module_code: str = "cs4455"
    #     #self.lineEdit_moduleCode.text().strip()
    #     assName: str = self.lineEdit_assName.text().strip()
    #     assClone: str = self.comboBox_assignments.currentText()
    #     if check_if_ass_exists(module_code, "curr", assName):
    #             create_message_box(f"Assignment {assName} instance in {module_code} in {ay} already exists!")
    #             return

    #     assClonePath = assPath(module_code, "curr", assClone)
    #     newAssPath = os.path.join(ROOTDIR + "/" + module_code + "/curr/assignments/" + assName)

    #     os.mkdir(newAssPath)

    #     copyCommand = "cp " + assClonePath + "/params.yaml " + newAssPath
    #     os.system(copyCommand)

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    exit_code = app.exec_()

    sys.exit(exit_code)
