from PyQt5 import QtCore, QtGui, QtWidgets, QGridLayout, QLabel, QLineEdit

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(500, 300)
        MainWindow.setMinimumSize(QtCore.QSize(500, 300))
        MainWindow.setMaximumSize(QtCore.QSize(500, 300))
        self.label_username = QtWidgets.QLabel(Dialog)
        self.label_username.setObjectName("label_username")
        self.label_password = QtWidgets.QLabel(Dialog)
        self.label_password.setObjectName("label_password")
        self.label_username.setGeometry(20, 30, 100, 30)
        self.label_password.setGeometry(20, 90, 100, 30)
        self.lineEdit_username = QtWidgets.QLineEdit(MainWindow)
        self.lineEdit_username.setObjectName("lineEdit_username")
        self.lineEdit_username.setGeometry(140, 30, 100, 30)
        self.lineEdit_password = QtWidgets.QLineEdit(MainWindow)
        self.lineEdit_password.setObjectName("lineEdit_password")
        self.lineEdit_password.setGeometry(140, 90, 100, 30)
        self.pushButton_login = QtWidgets
        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setTitle(_translate("MainWindow", "Handin Login"))
        self.label_username.setText(_translate("MainWindow", "Username"))
        self.label_password.setText(_translate("MainWindow", "Password"))
