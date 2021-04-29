from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(500, 300)
        self.label_username = QtWidgets.QLabel(Dialog)
        self.label_username.setObjectName("label_username")
        self.label_password = QtWidgets.QLabel(Dialog)
        self.label_password.setObjectName("label_password")
        self.label_username.setGeometry(110, 30, 100, 30)
        self.label_password.setGeometry(110, 90, 100, 30)
        self.lineEdit_username = QtWidgets.QLineEdit(Dialog)
        self.lineEdit_username.setObjectName("lineEdit_username")
        self.lineEdit_username.setGeometry(200, 30, 150, 30)
        self.lineEdit_password = QtWidgets.QLineEdit(Dialog)
        self.lineEdit_password.setObjectName("lineEdit_password")
        self.lineEdit_password.setGeometry(200, 90, 150, 30)
        self.lineEdit_password.setEchoMode(QtWidgets.QLineEdit.Password)
        self.pushButton_create = QtWidgets.QPushButton(Dialog)
        self.pushButton_create.setObjectName("pushButton_create")
        self.pushButton_create.setGeometry(110, 150, 250, 30)
        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)
    
    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Handin System (Admin) Create User"))
        self.label_username.setText(_translate("Dialog", "Username"))
        self.label_password.setText(_translate("Dialog", "Password"))
        self.pushButton_create.setText(_translate("Dialog", "Create"))