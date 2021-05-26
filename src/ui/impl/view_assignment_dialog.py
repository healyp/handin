# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'manage_student_marks_dialog.ui'
#
# Created by: PyQt5 UI code generator 5.14.1
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(700, 500)
        Dialog.setMinimumSize(QtCore.QSize(700, 600))
        Dialog.setMaximumSize(QtCore.QSize(700, 600))
        self.buttonBox = QtWidgets.QDialogButtonBox(Dialog)
        self.buttonBox.setGeometry(QtCore.QRect(320, 550, 341, 32))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.frame = QtWidgets.QFrame(Dialog)
        self.frame.setGeometry(QtCore.QRect(10, 60, 680, 480))
        self.frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame.setObjectName("frame")
        self.comboBox_assignments = QtWidgets.QComboBox(Dialog)
        self.comboBox_assignments.setGeometry(QtCore.QRect(100, 10, 87, 28))
        self.comboBox_assignments.setObjectName("comboBox_assignments")
        self.label = QtWidgets.QLabel(Dialog)
        self.label.setGeometry(QtCore.QRect(20, 10, 90, 28))
        self.label.setObjectName("label")
        self.label_2 = QtWidgets.QLabel(Dialog)
        self.label_2.setGeometry(QtCore.QRect(250, 10, 120, 28))
        self.label_2.setObjectName("label_2")
        self.lineEdit_assName = QtWidgets.QLineEdit(Dialog)
        self.lineEdit_assName.setGeometry(QtCore.QRect(370, 10, 90, 28))
        self.lineEdit_assName.setObjectName("lineEdit_assName")
        self.pushButton_help = QtWidgets.QPushButton(Dialog)
        self.pushButton_help.setGeometry(QtCore.QRect(470, 10, 20, 28))
        self.pushButton_help.setObjectName("pushButton_help")
        self.label_3 = QtWidgets.QLabel(self.frame)
        self.label_3.setGeometry(QtCore.QRect(40, 5, 300, 28))
        self.label_3.setObjectName("label_3")
        self.textEdit_showFileContent = QtWidgets.QTextEdit(self.frame)
        self.textEdit_showFileContent.setGeometry(QtCore.QRect(40, 30, 600, 400))
        self.textEdit_showFileContent.setObjectName("textEdit_showFileContent")
        self.layoutWidget = QtWidgets.QWidget(self.frame)
        self.layoutWidget.setGeometry(QtCore.QRect(300, 10, 100, 31))
        self.layoutWidget.setObjectName("layoutWidget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.layoutWidget)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setSpacing(10)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.pushButton_show = QtWidgets.QPushButton(Dialog)
        self.pushButton_show.setObjectName("pushButton_show")
        self.pushButton_show.setGeometry(QtCore.QRect(600, 10, 90, 28))
        self.checkBox_clone = QtWidgets.QCheckBox(self.frame)
        self.checkBox_clone.setGeometry(QtCore.QRect(40, 430, 300, 19))
        self.checkBox_clone.setObjectName("checkBox_clone")
        self.checkBox_edit = QtWidgets.QCheckBox(self.frame)
        self.checkBox_edit.setGeometry(QtCore.QRect(230, 430, 300, 19))
        self.checkBox_edit.setObjectName("checkBox_edit")
        self.checkBox_delete = QtWidgets.QCheckBox(self.frame)
        self.checkBox_delete.setGeometry(QtCore.QRect(410, 430, 300, 19))
        self.checkBox_delete.setObjectName("checkBox_delete")
        self.pushButton_edit_help = QtWidgets.QPushButton(self.frame)
        self.pushButton_edit_help.setGeometry(QtCore.QRect(600, 430, 20, 19))
        self.pushButton_help.setObjectName("pushButton_edit_help")

        self.retranslateUi(Dialog)
        self.buttonBox.rejected.connect(Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "View Assignment"))
        self.label.setText(_translate("Dialog", "Assignment:"))
        self.label_2.setText(_translate("Dialog", "New Assignment:"))
        self.pushButton_show.setText(_translate("MainWindow", "Show"))
        self.pushButton_help.setText(_translate("Dialog", "?"))
        self.pushButton_edit_help.setText(_translate("Dialog", "?"))
        self.label_3.setText(_translate("Dialog", "Details of assignment:"))
        self.checkBox_clone.setText(_translate("Dialog", "Clone this assignment"))
        self.checkBox_edit.setText(_translate("Dialog", "Edit this assignment"))
        self.checkBox_delete.setText(_translate("Dialog", "Delete this assignment"))
