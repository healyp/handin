# -*- coding: utf-8 -*-
import socket
import sys
from datetime import datetime
import struct
import os
import yaml

from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import QFileInfo
from PyQt5.QtWidgets import QMainWindow, QMessageBox

# ****** DYNAMIC CONFIGS ****** #
HOST = "{hostname}"
PORT = "{server_port}"
STUDENT_NAME = "{student_name}"
STUDENT_ID = "{student_id}"
MODULE_CODE = ""
# ****** DYNAMIC CONFIGS ****** #


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(800, 700)
        MainWindow.setMinimumSize(QtCore.QSize(800, 700))
        MainWindow.setMaximumSize(QtCore.QSize(800, 700))
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(20, 40, 100, 25))
        self.label.setObjectName("label")
        self.lineEdit_moduleCode = QtWidgets.QLineEdit(self.centralwidget)
        self.lineEdit_moduleCode.setGeometry(QtCore.QRect(140, 40, 120, 25))
        self.lineEdit_moduleCode.setObjectName("lineEdit_moduleCode")
        self.label_3 = QtWidgets.QLabel(self.centralwidget)
        self.label_3.setGeometry(QtCore.QRect(400, 40, 100, 25))
        self.label_3.setObjectName("label_3")
        self.label_4 = QtWidgets.QLabel(self.centralwidget)
        self.label_4.setGeometry(QtCore.QRect(400, 80, 110, 25))
        self.label_4.setObjectName("label_4")
        self.lineEdit_studentID = QtWidgets.QLineEdit(self.centralwidget)
        self.lineEdit_studentID.setGeometry(QtCore.QRect(520, 40, 120, 25))
        self.lineEdit_studentID.setObjectName("lineEdit_studentID")
        self.lineEdit_studentName = QtWidgets.QLineEdit(self.centralwidget)
        self.lineEdit_studentName.setGeometry(QtCore.QRect(520, 80, 220, 25))
        self.lineEdit_studentName.setText("")
        self.lineEdit_studentName.setObjectName("lineEdit_studentName")
        self.frame = QtWidgets.QFrame(self.centralwidget)
        self.frame.setGeometry(QtCore.QRect(20, 120, 750, 270))
        self.frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame.setObjectName("frame")
        self.textEdit_showFileContent = QtWidgets.QTextEdit(self.frame)
        self.textEdit_showFileContent.setGeometry(QtCore.QRect(20, 50, 700, 210))
        self.textEdit_showFileContent.setObjectName("textEdit_showFileContent")
        self.layoutWidget = QtWidgets.QWidget(self.frame)
        self.layoutWidget.setGeometry(QtCore.QRect(20, 10, 701, 31))
        self.layoutWidget.setObjectName("layoutWidget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.layoutWidget)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setSpacing(16)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label_5 = QtWidgets.QLabel(self.layoutWidget)
        self.label_5.setObjectName("label_5")
        self.horizontalLayout.addWidget(self.label_5)
        self.lineEdit_chooseFile = QtWidgets.QLineEdit(self.layoutWidget)
        self.lineEdit_chooseFile.setObjectName("lineEdit_chooseFile")
        self.horizontalLayout.addWidget(self.lineEdit_chooseFile)
        self.pushButton_browse = QtWidgets.QPushButton(self.layoutWidget)
        self.pushButton_browse.setObjectName("pushButton_browse")
        self.horizontalLayout.addWidget(self.pushButton_browse)
        self.pushButton_handin = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_handin.setGeometry(QtCore.QRect(640, 420, 93, 28))
        self.pushButton_handin.setObjectName("pushButton_handin")
        self.label_6 = QtWidgets.QLabel(self.centralwidget)
        self.label_6.setGeometry(QtCore.QRect(20, 430, 81, 21))
        self.label_6.setObjectName("label_6")
        self.label_7 = QtWidgets.QLabel(self.centralwidget)
        self.label_7.setGeometry(QtCore.QRect(402, 420, 111, 28))
        self.label_7.setObjectName("label_7")
        self.assignmentName = QtWidgets.QLineEdit(self.centralwidget)
        self.assignmentName.setGeometry(QtCore.QRect(520, 420, 93, 28))
        self.textEdit_Output = QtWidgets.QTextEdit(self.centralwidget)
        self.textEdit_Output.setGeometry(QtCore.QRect(20, 470, 750, 200))
        self.textEdit_Output.setStyleSheet("color: rgb(102, 102, 255)")
        self.textEdit_Output.setObjectName("textEdit_Output")
        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Handin System (Student)"))
        self.label.setText(_translate("MainWindow", "Module Code:"))
        self.label_3.setText(_translate("MainWindow", "Student ID:"))
        self.label_4.setText(_translate("MainWindow", "Student Name:"))
        self.label_5.setText(_translate("MainWindow", "File Name:"))
        self.pushButton_browse.setText(_translate("MainWindow", "Browse"))
        self.pushButton_handin.setText(_translate("MainWindow", "Handin"))
        self.label_6.setText(_translate("MainWindow", "Output"))
        self.label_7.setText(_translate("MainWindow", "Assignment:"))
        self.textEdit_Output.setHtml(_translate("MainWindow",
                                                "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
                                                "<html><head><meta name=\"qrichtext\" content=\"1\" />"
                                                "</style></head><body style=\" font-family:\'SimSun\'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
                                                "<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p></body></html>"))


class HandinMainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super(HandinMainWindow, self).__init__()
        self.setupUi(self)
        self.pushButton_browse.clicked.connect(self.browse)
        self.pushButton_handin.clicked.connect(self.check_handin)
        self.lineEdit_studentID.setText(STUDENT_ID)
        self.lineEdit_studentID.setEnabled(False)
        self.lineEdit_studentName.setText(STUDENT_NAME)
        self.lineEdit_studentName.setEnabled(False)
        self.textEdit_Output.setReadOnly(True)
        self.textEdit_showFileContent.setReadOnly(True)
        self.lineEdit_chooseFile.setReadOnly(True)
        self.lineEdit_chooseFile.textChanged.connect(self.disable_handin)
        self.assignmentName.textChanged.connect(self.disable_handin)
        self.lineEdit_moduleCode.textChanged.connect(self.disable_handin)
        self.pushButton_handin.setEnabled(False)

        self.initialise_config_params()

    def closeEvent(self, QCloseEvent):
        home_path = os.path.expanduser("~") + "/.handin/configs.yaml"
        module_code = self.lineEdit_moduleCode.text().strip()

        if os.path.isfile(home_path) and module_code != "":
            with open(home_path, 'r') as file:
                data = yaml.safe_load(file)

            data['last_module'] = module_code
            with open(home_path, 'w') as file:
                yaml.dump(data, file)

        QCloseEvent.accept()

    def initialise_config_params(self):
        global HOST, PORT
        home_path = os.path.expanduser("~") + "/.handin"
        if not os.path.isdir(home_path):
            os.makedirs(home_path)

        config_file = home_path + "/configs.yaml"

        if not os.path.isfile(config_file):
            dictionary = {{
                'host': str(HOST),
                'port': int(PORT)
            }} # need double braces to escape formatting in registration_server


            with open(config_file, 'w+') as file:
                yaml.dump(dictionary, file)
        else:
            with open(config_file, 'r') as file:
                data: dict = yaml.safe_load(file)

            if 'host' in data and 'port' in data:
                HOST = data['host']
                PORT = int(data['port'])

            if 'last_module' in data:
                self.lineEdit_moduleCode.setText(data['last_module'])

        print("Using host: " + str(HOST) + " and port: " + str(PORT) + ". If these are incorrect, change them in " + config_file)

    def disable_handin(self):
        global MODULE_CODE
        module_code_temp = self.lineEdit_moduleCode.text().strip()
        if len(self.lineEdit_chooseFile.text()) > 0 and len(self.assignmentName.text().strip()) > 0 \
                and len(module_code_temp) > 0:
            self.pushButton_handin.setEnabled(True)
            MODULE_CODE = module_code_temp.lower()
        else:
            self.pushButton_handin.setEnabled(False)
            MODULE_CODE = ""

    def browse(self):
        filename, file_type = QtWidgets.QFileDialog.getOpenFileName(
            self, "Choose file", "./", "All Files (*);;C File (*.c);;Cpp File (*.cpp);;"
                                       "Java File (*.java);;Python File (*.py);;Text File (*.txt)")
        self.lineEdit_chooseFile.setText(filename)
        try:
            with open(filename, 'rb') as f:
                content = f.read().decode('utf-8')
        except Exception as e:
            content = ""
            print(e)
        self.textEdit_showFileContent.setText(content)
        self.submit_filepath = filename

    def confirm_submission(self):
        assignment_name = self.assignmentName.text().strip()

        msgBox = QMessageBox(self)
        msgBox.setIcon(QMessageBox.Question)
        msgBox.setText("Are you sure you want to submit assignment %s? The process can take at least a few seconds, please be patient" % assignment_name)
        msgBox.setWindowTitle("Handin Submission")
        msgBox.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)

        returnValue = msgBox.exec()
        if returnValue == QMessageBox.Ok:
            return True
        else:
            return False

    def submitted(self):
        assignment_name = self.assignmentName.text().strip()

        msgBox = QMessageBox(self)
        msgBox.setIcon(QMessageBox.Information)
        msgBox.setText("Assignment %s has been submitted successfully. Look at the bottom of the output for your marks" % assignment_name)
        msgBox.setWindowTitle("Handin Submission")
        msgBox.setStandardButtons(QMessageBox.Ok)

        msgBox.exec()

    def check_handin(self):
        global initVars

        if not self.confirm_submission():
            return

        try:
            s = socket.socket()
            self.output("Started handin...")
            s.connect((HOST, int(PORT)))
            self.output("Connected to handin server...")
            # check if module exists
            if module_exists(MODULE_CODE, s):
                # check if assignment name is valid
                assignment_name = self.assignmentName.text().strip()
                if assignment_name_valid(MODULE_CODE, assignment_name, s):
                    self.output("Submitting code to %s::%s" % (MODULE_CODE, assignment_name))
                    # check student id authentication
                    if check_student_authentication(MODULE_CODE, STUDENT_ID, s):
                        self.output("Student ID: %s has been authenticated" % STUDENT_ID)
                        # create a vars.yaml file to store info of a specific student
                        result = create_vars_file(MODULE_CODE, STUDENT_ID, assignment_name, s)
                        if result == "Success":
                            print("Vars file has been created ...")
                            initVars = True
                        elif result == "Reinit":
                            print("Vars file exists but will be re-initialised to apply your extended attempts")
                            initVars = True
                        elif result == "Failed":
                            print("Vars file already exists")
                            initVars = False
                        self.run_handin(assignment_name, s, initVars)
                    else:
                        self.output("Student ID: %s not authenticated" % STUDENT_ID, flag="ERROR")
                else:
                    self.output("%s not valid for %s" % (assignment_name, MODULE_CODE), flag="ERROR")
            else:
                self.output("%s not exist!" % MODULE_CODE, flag="ERROR")
        except Exception as e:
            self.output(str(e), flag="ERROR")

    def run_handin(self, assignment_name, s: socket.socket, init_vars: bool):
        # initialize vars.yaml file
        if init_vars:
            init_vars_file(MODULE_CODE, STUDENT_ID, assignment_name, s)
        # get attempts left
        attempts_left: int = check_attempts_left(MODULE_CODE, STUDENT_ID, assignment_name, s)

        if attempts_left == 0:
            self.output("You have no more attempts!", flag="ERROR")
            return

        late_penalty_msg = check_late_penalty(MODULE_CODE, assignment_name, s)
        penalty: int = -1
        if isinstance(late_penalty_msg, str):
            self.output(late_penalty_msg, flag="ERROR")
        if isinstance(late_penalty_msg, int):
            self.output("Penalty applied : " + str(late_penalty_msg) + "%")
            penalty = late_penalty_msg
        if penalty != -1:
            # check if the filename matches required filename
            filename = QFileInfo(self.submit_filepath).fileName()
            file_suffix = QFileInfo(self.submit_filepath).suffix()
            msg = check_collection_filename(filename, MODULE_CODE, assignment_name, s)
            if msg == "True":
                # copy file to server side
                send_file_to_server(self.submit_filepath, MODULE_CODE, assignment_name, STUDENT_ID, s)
                # get exec result output
                print('send file to server finished ...')
                result = get_exec_result(MODULE_CODE, assignment_name, STUDENT_ID, s, file_suffix, str(penalty))
                self.output(result)
                self.submitted()
            else:
                self.output(msg, "ERROR")

    def output(self, text: str, flag: str = "INFO"):
        df = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        self.textEdit_Output.append("---" + df + "---")
        if flag.upper() == "INFO":
            blackText = "<span style=\"color:#000000;\" >"
            blackText += text
            blackText += "</span>"
            self.textEdit_Output.append(blackText)
        elif flag.upper() == "ERROR":
            redText = "<span style=\"color:#ff0000;\" >"
            redText += "ERROR: "
            redText += text
            redText += "</span>"
            self.textEdit_Output.append(redText)


def module_exists(module_code, s: socket.socket):
    send_message("Check module exists", s)
    if recv_message(s) == "OK":
        send_message(module_code, s)
        result = recv_message(s)
        if result == "True":
            return True
    return False


def assignment_name_valid(module_code, assignment_name, s: socket.socket):
    send_message("Checking Assignment Name", s)
    if recv_message(s) == "OK":
        send_message(module_code, s)
        send_message(assignment_name, s)
        result = recv_message(s)
        if result == "True":
            return True
    return False


def check_student_authentication(module_code, student_id, s: socket.socket):
    send_message("Authentication", s)
    if recv_message(s) == "OK":
        send_message(module_code, s)
        send_message(student_id, s)
        is_auth = recv_message(s)
        if is_auth == "True":
            return True
    return False


def check_collection_filename(filename, module_code, assignment_name, s: socket.socket):
    """check if the submitted filename matches required filename"""
    send_message("Check collection filename", s)
    if recv_message(s) == "OK":
        send_message(filename, s)
        send_message(module_code, s)
        send_message(assignment_name, s)
        is_collected_filename = recv_message(s)
        return is_collected_filename


def create_vars_file(module_code, student_id, assignment_name, s: socket.socket) -> str:
    """create a vars.yaml file to store info of a specific student"""
    send_message("Create vars file", s)
    if recv_message(s) == "OK":
        send_message(module_code, s)
        send_message(student_id, s)
        send_message(assignment_name, s)
        # Success or Failed
        result = recv_message(s)
        return result


def init_vars_file(module_code, student_id, assignment_name, s: socket.socket):
    send_message("Init vars file", s)
    if recv_message(s) == "OK":
        send_message(module_code, s)
        send_message(student_id, s)
        send_message(assignment_name, s)


def check_attempts_left(module_code, student_id, assignment_name, s: socket.socket) -> int:
    send_message("Check attempts left", s)
    if recv_message(s) == "OK":
        send_message(module_code, s)
        send_message(student_id, s)
        send_message(assignment_name, s)
        attempts_left = recv_message(s)
        if attempts_left != "False":
            attempts = int(attempts_left)
            if attempts > 0:
                return attempts
            else:
                print("you have no attempts left")
                print(attempts_left)
                return 0
        else:
            print("Error when acquiring attemptsLeft value")
            return -1
    return -1


def check_late_penalty(module_code, assignment_name, s):
    send_message("Check late penalty", s)
    if recv_message(s) == "OK":
        send_message(module_code, s)
        send_message(assignment_name, s)
        send_message(STUDENT_ID, s)
        late_penalty = recv_message(s)
        try:
            late_penalty = int(late_penalty)
        except:
            late_penalty = str(late_penalty)
        return late_penalty


def send_file_to_server(submit_filepath, module_code, assignment_name, student_id, s: socket.socket):
    send_message("Send file to server", s)
    if recv_message(s) == "OK":
        send_message(module_code, s)
        send_message(assignment_name, s)
        send_message(student_id, s)
        send_message(str(submit_filepath), s)
        msg = recv_message(s)
        print(msg)
        with open(submit_filepath, 'r') as f:
            contents = f.read()
            contents += "DONE"
            send_message(contents, s)

        msg = recv_message(s)
        print(msg)


def get_exec_result(module_code, assignment_name, student_id, s: socket.socket, file_suffix, penalty: str) -> str:
    send_message("Get exec result", s)
    if recv_message(s) == "OK":
        send_message(module_code, s)
        send_message(assignment_name, s)
        send_message(student_id, s)
        send_message(file_suffix, s)
        send_message(penalty, s)

        result = recv_message(s)
        return result

def send_message(msg, sock):
    msg = struct.pack('>I', len(msg)) + bytes(msg, 'utf-8') # prepend a 4 byte string containing the length of the msg to the start of the string
    sock.sendall(msg)

def recv_message(sock):
    raw_msglen = recvall(sock, 4) # first 4 letters of the string is a struct representation of the message length
    if not raw_msglen:
        return ""
    msglen = struct.unpack('>I', raw_msglen)[0]
    raw_data = recvall(sock, msglen)
    if not raw_data:
        return ""
    else:
        return raw_data.decode()

def recvall(sock, n):
    data = bytearray()
    while len(data) < n:
        byte_size = n - len(data)
        if (byte_size > 1024):
            byte_size = 1024
        packet = sock.recv(n - len(data))
        if not packet:
            return None
        data.extend(packet)
    return data

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = HandinMainWindow()
    window.show()
    sys.exit(app.exec_())
