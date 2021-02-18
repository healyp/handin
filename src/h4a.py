import os
import re
import sys

import yaml
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import QDate, QRegExp, QDateTime
from PyQt5.QtGui import QRegExpValidator
from PyQt5.QtWidgets import QMainWindow, QDialog, QMessageBox, QLineEdit, QGroupBox, QTableWidgetItem

from ui.impl.create_new_module_dialog import Ui_Dialog as Ui_Dialog_Create_New_Module
from ui.impl.handin_admin_main_window import Ui_MainWindow as Ui_MainWindow

from datetime import date

from const import ROOTDIR, ModCodeRE, whatAY, containsValidDay, check_if_module_exists

def create_message_box(text):
    msgBox = QMessageBox()
    msgBox.setIcon(QMessageBox.Information)
    msgBox.setText(text)
    msgBox.setWindowTitle("Message")
    msgBox.setStandardButtons(QMessageBox.Ok)
    msgBox.exec()
    
def isMatchRegex(regex: str, text: str) -> bool:
    return bool(re.match(regex, text, re.IGNORECASE))

def validDefaultDate(given: str):
    if containsValidDay(given) and re.search("%w(\s*[+-]\s*\d+)?", given, re.IGNORECASE):
        return(True)
    else:
        return(False)

class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setupUi(self)
        self.pushButton.clicked.connect(lambda: self.create_new_module())

    def create_new_module(self):
        dialog = CreateNewModuleDialog(self)
        dialog.show()

class CreateNewModuleDialog(QDialog, Ui_Dialog_Create_New_Module):
    def __init__(self, parent=None):
        super(CreateNewModuleDialog, self).__init__(parent)
        self.setupUi(self)
        # Academic Year format: 2020-2021-S1
        self.regexAY = "\\d{4}-\\d{4}-S[1,2]"
        # self.lineEdit_academicYear.setPlaceholderText(whatAY())
        self.lineEdit_academicYear.setText(whatAY())
        self.accepted.connect(lambda: self.create_module())
        self.buttonBox.setEnabled(False)
        self.lineEdit.textChanged.connect(self.disable_buttonbox)

    def disable_buttonbox(self):
        # len(self.lineEdit.text()) > 0 and \
        goodcode = isMatchRegex(regex=ModCodeRE, text=self.lineEdit.text())
        self.buttonBox.setEnabled(goodcode)


    def create_module(self):
        module_code: str = self.lineEdit.text().strip()
        ay: str = self.lineEdit_academicYear.text().strip()
        # start_semester: str = self.dateEdit_startSemester.text().strip()
        if check_if_module_exists(module_code):
            create_message_box(f"Module instance {module_code} in {ay} already exists!")
            return

        moduleDir = os.path.join(ROOTDIR, module_code, ay)
        self.create_files(moduleDir)
        linkDir = os.path.join(ROOTDIR, module_code, "curr")
        os.symlink(moduleDir, linkDir)

    def create_files(self, module_dir):
        """create tmpdir and definitions file"""
        tmpdir = os.path.join(module_dir, "tmp")
        if not os.path.exists(tmpdir):
            os.makedirs(tmpdir) # hey presto!
        # self.class_list_path = os.path.join(module_dir, "class-list")
        # if not os.path.exists(self.class_list_path):
        #     with open(self.class_list_path, "w"):
        #         pass

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())