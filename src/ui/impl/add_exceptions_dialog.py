# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'add_exceptions_dialog.ui'
#
# Created by: PyQt5 UI code generator 5.14.2
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(418, 458)
        self.label_assignment = QtWidgets.QLabel(Dialog)
        self.label_assignment.setGeometry(QtCore.QRect(50, 20, 101, 21))
        self.label_assignment.setObjectName("label_assignment")
        self.assignment_comboBox = QtWidgets.QComboBox(Dialog)
        self.assignment_comboBox.setGeometry(QtCore.QRect(170, 20, 141, 21))
        self.assignment_comboBox.setObjectName("assignment_comboBox")
        self.label_studentId = QtWidgets.QLabel(Dialog)
        self.label_studentId.setGeometry(QtCore.QRect(50, 70, 81, 16))
        self.label_studentId.setObjectName("label_studentId")
        self.lineEdit_studentId = QtWidgets.QLineEdit(Dialog)
        self.lineEdit_studentId.setGeometry(QtCore.QRect(170, 70, 141, 21))
        self.lineEdit_studentId.setObjectName("lineEdit_studentId")
        self.exceptions_groupBox = QtWidgets.QGroupBox(Dialog)
        self.exceptions_groupBox.setGeometry(QtCore.QRect(40, 130, 331, 241))
        self.exceptions_groupBox.setObjectName("exceptions_groupBox")
        self.dateTime_dueDate = QtWidgets.QDateTimeEdit(self.exceptions_groupBox)
        self.dateTime_dueDate.setGeometry(QtCore.QRect(140, 40, 151, 21))
        self.dateTime_dueDate.setObjectName("dateTime_dueDate")
        self.label_dueDate = QtWidgets.QLabel(self.exceptions_groupBox)
        self.label_dueDate.setGeometry(QtCore.QRect(20, 40, 71, 16))
        self.label_dueDate.setObjectName("label_dueDate")
        self.label_cutOff = QtWidgets.QLabel(self.exceptions_groupBox)
        self.label_cutOff.setGeometry(QtCore.QRect(20, 90, 81, 16))
        self.label_cutOff.setObjectName("label_cutOff")
        self.dateTime_cutoffDate = QtWidgets.QDateTimeEdit(self.exceptions_groupBox)
        self.dateTime_cutoffDate.setGeometry(QtCore.QRect(140, 90, 151, 21))
        self.dateTime_cutoffDate.setObjectName("dateTime_cutoffDate")
        self.label_penalty = QtWidgets.QLabel(self.exceptions_groupBox)
        self.label_penalty.setGeometry(QtCore.QRect(20, 140, 111, 16))
        self.label_penalty.setObjectName("label_penalty")
        self.spinBox_penalty = QtWidgets.QSpinBox(self.exceptions_groupBox)
        self.spinBox_penalty.setGeometry(QtCore.QRect(140, 140, 61, 24))
        self.spinBox_penalty.setObjectName("spinBox_penalty")
        self.label_attempts = QtWidgets.QLabel(self.exceptions_groupBox)
        self.label_attempts.setGeometry(QtCore.QRect(20, 200, 81, 16))
        self.label_attempts.setObjectName("label_attempts")
        self.spinBox_attempts = QtWidgets.QSpinBox(self.exceptions_groupBox)
        self.spinBox_attempts.setGeometry(QtCore.QRect(140, 200, 61, 24))
        self.spinBox_attempts.setObjectName("spinBox_attempts")
        self.pushButton_submit = QtWidgets.QPushButton(Dialog)
        self.pushButton_submit.setGeometry(QtCore.QRect(310, 410, 80, 23))
        self.pushButton_submit.setObjectName("pushButton_submit")
        self.pushButton_cancel = QtWidgets.QPushButton(Dialog)
        self.pushButton_cancel.setGeometry(QtCore.QRect(210, 410, 80, 23))
        self.pushButton_cancel.setObjectName("pushButton_cancel")
        self.checkBox_retrieveExisting = QtWidgets.QCheckBox(Dialog)
        self.checkBox_retrieveExisting.setGeometry(QtCore.QRect(170, 100, 141, 21))
        self.checkBox_retrieveExisting.setObjectName("checkBox_retrieveExisting")
        self.checkBox_delete = QtWidgets.QCheckBox(Dialog)
        self.checkBox_delete.setGeometry(QtCore.QRect(40, 380, 141, 21))
        self.checkBox_delete.setObjectName("checkBox_delete")

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Add Exceptions"))
        self.label_assignment.setText(_translate("Dialog", "Assignment:"))
        self.label_studentId.setText(_translate("Dialog", "Student ID:"))
        self.exceptions_groupBox.setTitle(_translate("Dialog", "Exceptions:"))
        self.dateTime_dueDate.setDisplayFormat(_translate("Dialog", "yyyy-MM-dd HH:mm"))
        self.label_dueDate.setText(_translate("Dialog", "Due Date:"))
        self.label_cutOff.setText(_translate("Dialog", "Cutoff Date:"))
        self.dateTime_cutoffDate.setDisplayFormat(_translate("Dialog", "yyyy-MM-dd HH:mm"))
        self.label_penalty.setText(_translate("Dialog", "Penalty Per Day:"))
        self.label_attempts.setText(_translate("Dialog", "Attempts:"))
        self.pushButton_submit.setText(_translate("Dialog", "Submit"))
        self.pushButton_cancel.setText(_translate("Dialog", "Cancel"))
        self.checkBox_retrieveExisting.setToolTip(_translate("Dialog", "If there are existing exceptions for the provided student, populate the exceptions field"))
        self.checkBox_retrieveExisting.setText(_translate("Dialog", "Retrieve Existing?"))
        self.checkBox_delete.setText(_translate("Dialog", "Delete"))
