import os
import grp
import re
import sys

from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QMainWindow, QDialog, QMessageBox

from ui.impl.create_new_module_dialog import Ui_Dialog as Ui_Dialog_Create_New_Module
from ui.impl.handin_admin_main_window import Ui_MainWindow as Ui_MainWindow
from ui.impl.create_user_dialog import Ui_Dialog as Ui_Dialog_Create_User
from ui.impl.access_rights_dialog import Ui_Dialog as Ui_Dialog_Access_Rights

from const import ROOTDIR, ModCodeRE, whatAY, containsValidDay, check_if_module_exists
from password_security import encrypt_password

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
        self.pushButton_user.clicked.connect(lambda: self.create_user())
        self.pushButton_access_rights.clicked.connect(lambda: self.access_rights())

    def create_new_module(self):
        dialog = CreateNewModuleDialog(self)
        dialog.show()

    def create_user(self):
        dialog = CreateUserDialog(self)
        dialog.show()

    def access_rights(self):
        dialog = AccessRightsDialog(self)
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
        module_code = module_code.lower()
        ay: str = self.lineEdit_academicYear.text().strip()
        # start_semester: str = self.dateEdit_startSemester.text().strip()
        if check_if_module_exists(module_code):
            create_message_box(f"Module instance {module_code} in {ay} already exists!")
            return

        moduleDir = os.path.join(ROOTDIR[ROOTDIR.index(".handin"):], module_code, ay)
        self.create_files(moduleDir)
        linkDir = os.path.join(ROOTDIR, module_code, "curr")
        os.symlink(ay, linkDir, True)

        create_message_box(f"Module {module_code} on academic year {ay} created successfully!")

    def create_files(self, module_dir):
        if not os.path.isdir(module_dir):
            os.makedirs(module_dir)

        class_list_path = os.path.join(module_dir, "class-list")
        if not os.path.exists(class_list_path):
            with open(class_list_path, "w+"):
                pass

class CreateUserDialog(QDialog, Ui_Dialog_Create_User):
    def __init__(self, parent=None):
        super(CreateUserDialog, self).__init__(parent)
        self.setupUi(self)
        self.pushButton_create.clicked.connect(lambda: self.create_user())

    def create_user_folder(self, user):
        folder_path = ROOTDIR + "/users/" + user
        if not os.path.isdir(folder_path):
            try:
                os.makedirs(folder_path)
            except OSError as err:
                error_dialog = QtWidgets.QErrorMessage()
                error_dialog.showMessage("Failed to create user directory, please try again. Message: " + err)
                error_dialog.exec()

    def create_user(self):
        user = self.lineEdit_username.text().strip()
        password = self.lineEdit_password.text().strip()
        hashed_password = encrypt_password(password)
        path = ROOTDIR + "/login_credentials.txt"
        with open(path, 'a') as f:
            line = user + " " + hashed_password + "\n"
            f.write(line)
            self.create_user_folder(user)

        create_message_box(f"Lecturer {user} created successfully!")

        self.reject

class AccessRightsDialog(QDialog, Ui_Dialog_Access_Rights):
    CHOOSE_MODULE = "Choose Module"

    def __init__(self, parent=None):
        super(AccessRightsDialog, self).__init__(parent)
        self.setupUi(self)
        self.addButton.clicked.connect(self.add_access_rights)
        self.addButton.setEnabled(False)
        self.userEdit.textChanged.connect(self.disable_add_button)
        self.modulesBox.currentTextChanged.connect(self.disable_add_button)
        self.modulesBox.addItems([AccessRightsDialog.CHOOSE_MODULE])
        self.removeAccess.stateChanged.connect(self.remove_access_rights_combo)
        self.load_modules()

    def remove_access_rights_combo(self):
        checked = self.removeAccess.isChecked()

        if checked:
            self.addButton.clicked.disconnect(self.add_access_rights)
            self.addButton.clicked.connect(self.remove_access_rights)
            self.addButton.setText("Remove Access")
        else:
            self.addButton.clicked.disconnect(self.remove_access_rights)
            self.addButton.clicked.connect(self.add_access_rights)
            self.addButton.setText("Add Access")

    def disable_add_button(self):
        user = self.userEdit.text().strip()
        module = self.modulesBox.currentText().strip()
        self.addButton.setEnabled(user != "" and module != AccessRightsDialog.CHOOSE_MODULE)

    def load_modules(self):
        modules = [f.upper() for f in os.listdir(ROOTDIR) if re.match(ModCodeRE, f)]
        if len(modules) > 0:
            self.modulesBox.addItems(modules)

    def user_exists(self, user):
        path = ROOTDIR + "/users"
        found_users = [f for f in os.listdir(path) if f == user]

        return len(found_users) != 0

    def get_current_access_lines(self):
        path = ROOTDIR + "/access_rights.txt"

        lines = []

        if os.path.isfile(path):
            with open(path, 'r') as f:
                for ln in f:
                    lines.append(ln.strip())

        return lines

    def add_access_rights(self):
        self.user_error.setText("")
        self.error_message.setText("")
        user = self.userEdit.text().strip()
        module = self.modulesBox.currentText().strip().lower()

        if self.user_exists(user):
            path = ROOTDIR + "/access_rights.txt"

            try:
                user_found = False
                error_occurred = False

                lines = self.get_current_access_lines()

                with open(path, 'w+') as f:
                    for ln in lines:
                        if ln.startswith(user):
                            user_found = True
                            data = ln.split()
                            if module not in data[1:]:
                                ln = f"{ln} {module}"
                            else:
                                error_occurred = True
                                self.error_message.setText("The user already has access")
                        else:
                            ln = f"{ln}"
                        f.write(ln + "\n")

                    if not user_found:
                        f.write(f"{user} {module}")

                if not error_occurred:
                    create_message_box(f"User {user} given access to module {module.upper()}")
            except Exception as e:
                print(e)
                self.error_message.setText("An error occurred, try again")
        else:
            self.user_error.setText("User does not exist")

    def remove_access_rights(self):
        self.user_error.setText("")
        self.error_message.setText("")
        user = self.userEdit.text().strip()
        module = self.modulesBox.currentText().strip().lower()

        if self.user_exists(user):
            path = ROOTDIR + "/access_rights.txt"

            try:
                module_found = False
                error_occurred = False

                lines = self.get_current_access_lines()

                with open(path, 'w+') as f:
                    for ln in lines:
                        if ln.startswith(user):
                            data = ln.split()
                            ln = f"{user} "
                            for m in data[1:]:
                                m = m.strip()
                                if m != module:
                                    ln += f"{m} "
                                else:
                                    module_found = True
                            if not module_found:
                                error_occurred = True
                                self.error_message.setText("The user does not have access")
                        else:
                            ln = f"{ln}"
                        f.write(ln + "\n")

                if not error_occurred:
                    create_message_box(f"Access to module {module.upper()} removed from user {user}")
            except Exception as e:
                print(e)
                self.error_message.setText("An error occurred, try again")
        else:
            self.user_error.setText("User does not exist")

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
