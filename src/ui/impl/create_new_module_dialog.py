# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'create_new_module_dialog.ui'
#
# Created by: PyQt5 UI code generator 5.15.0
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(364, 505)
        self.buttonBox = QtWidgets.QDialogButtonBox(Dialog)
        self.buttonBox.setGeometry(QtCore.QRect(10, 460, 341, 32))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.layoutWidget = QtWidgets.QWidget(Dialog)
        self.layoutWidget.setGeometry(QtCore.QRect(50, 60, 294, 127))
        self.layoutWidget.setObjectName("layoutWidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.layoutWidget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.label_4 = QtWidgets.QLabel(self.layoutWidget)
        self.label_4.setObjectName("label_4")
        self.horizontalLayout_4.addWidget(self.label_4)
        self.lineEdit = QtWidgets.QLineEdit(self.layoutWidget)
        self.lineEdit.setObjectName("lineEdit")
        self.horizontalLayout_4.addWidget(self.lineEdit)
        self.verticalLayout.addLayout(self.horizontalLayout_4)
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.label_3 = QtWidgets.QLabel(self.layoutWidget)
        self.label_3.setObjectName("label_3")
        self.horizontalLayout_3.addWidget(self.label_3)
        self.lineEdit_academicYear = QtWidgets.QLineEdit(self.layoutWidget)
        self.lineEdit_academicYear.setEnabled(False)
        self.lineEdit_academicYear.setText("")
        self.lineEdit_academicYear.setObjectName("lineEdit_academicYear")
        self.horizontalLayout_3.addWidget(self.lineEdit_academicYear)
        self.verticalLayout.addLayout(self.horizontalLayout_3)
        self.groupBox_defaults = QtWidgets.QGroupBox(Dialog)
        self.groupBox_defaults.setGeometry(QtCore.QRect(50, 200, 281, 231))
        font = QtGui.QFont()
        font.setItalic(True)
        self.groupBox_defaults.setFont(font)
        self.groupBox_defaults.setCheckable(True)
        self.groupBox_defaults.setChecked(False)
        self.groupBox_defaults.setObjectName("groupBox_defaults")
        self.label = QtWidgets.QLabel(self.groupBox_defaults)
        self.label.setGeometry(QtCore.QRect(10, 20, 121, 31))
        self.label.setObjectName("label")
        self.dateEdit_startSemester = QtWidgets.QDateEdit(self.groupBox_defaults)
        self.dateEdit_startSemester.setGeometry(QtCore.QRect(150, 20, 101, 31))
        self.dateEdit_startSemester.setObjectName("dateEdit_startSemester")
        self.label_2 = QtWidgets.QLabel(self.groupBox_defaults)
        self.label_2.setEnabled(False)
        self.label_2.setGeometry(QtCore.QRect(10, 60, 121, 31))
        self.label_2.setObjectName("label_2")
        self.label_5 = QtWidgets.QLabel(self.groupBox_defaults)
        self.label_5.setGeometry(QtCore.QRect(10, 90, 121, 31))
        self.label_5.setObjectName("label_5")
        self.timeEdit = QtWidgets.QTimeEdit(self.groupBox_defaults)
        self.timeEdit.setGeometry(QtCore.QRect(150, 90, 71, 26))
        self.timeEdit.setObjectName("timeEdit")
        self.label_6 = QtWidgets.QLabel(self.groupBox_defaults)
        self.label_6.setGeometry(QtCore.QRect(10, 120, 91, 31))
        self.label_6.setObjectName("label_6")
        self.label_7 = QtWidgets.QLabel(self.groupBox_defaults)
        self.label_7.setGeometry(QtCore.QRect(10, 150, 91, 31))
        self.label_7.setObjectName("label_7")
        self.lineEdit_2 = QtWidgets.QLineEdit(self.groupBox_defaults)
        self.lineEdit_2.setGeometry(QtCore.QRect(150, 120, 101, 25))
        self.lineEdit_2.setObjectName("lineEdit_2")
        self.lineEdit_3 = QtWidgets.QLineEdit(self.groupBox_defaults)
        self.lineEdit_3.setGeometry(QtCore.QRect(150, 160, 101, 25))
        self.lineEdit_3.setObjectName("lineEdit_3")
        self.label_8 = QtWidgets.QLabel(self.groupBox_defaults)
        self.label_8.setGeometry(QtCore.QRect(10, 190, 91, 31))
        self.label_8.setObjectName("label_8")
        self.lineEdit_4 = QtWidgets.QLineEdit(self.groupBox_defaults)
        self.lineEdit_4.setGeometry(QtCore.QRect(150, 190, 101, 25))
        self.lineEdit_4.setObjectName("lineEdit_4")

        self.retranslateUi(Dialog)
        self.buttonBox.accepted.connect(Dialog.accept)
        self.buttonBox.rejected.connect(Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Create New Module"))
        self.label_4.setText(_translate("Dialog", "Module Code:"))
        self.label_3.setText(_translate("Dialog", "Academic Year:"))
        self.groupBox_defaults.setTitle(_translate("Dialog", "Prefer Week Numbers (Due Dates, etc.)"))
        self.label.setText(_translate("Dialog", "<html><head/><body><p><span style=\" font-style:normal;\">Monday, Week01:</span></p></body></html>"))
        self.label_2.setText(_translate("Dialog", "<html><head/><body><p>Defaults:</p></body></html>"))
        self.label_5.setText(_translate("Dialog", "<html><head/><body><p><span style=\" font-style:normal;\">Time</span></p></body></html>"))
        self.label_6.setText(_translate("Dialog", "<html><head/><body><p><span style=\" font-style:normal;\">OpenDate</span></p></body></html>"))
        self.label_7.setText(_translate("Dialog", "<html><head/><body><p><span style=\" font-style:normal;\">DueDate</span></p></body></html>"))
        self.lineEdit_2.setText(_translate("Dialog", "Monday, %w-1"))
        self.lineEdit_3.setText(_translate("Dialog", "Monday, %w"))
        self.label_8.setText(_translate("Dialog", "<html><head/><body><p><span style=\" font-style:normal;\">CutoffDate</span></p></body></html>"))
        self.lineEdit_4.setText(_translate("Dialog", "Friday, %w+1"))
