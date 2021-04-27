# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'createOneOffAssignment_dialog.ui'
#
# Created by: PyQt5 UI code generator 5.15.0
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(800, 1000)
        Dialog.setMinimumSize(QtCore.QSize(800, 1000))
        Dialog.setMaximumSize(QtCore.QSize(800, 1000))
        self.buttonBox = QtWidgets.QDialogButtonBox(Dialog)
        self.buttonBox.setGeometry(QtCore.QRect(410, 960, 341, 32))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.label = QtWidgets.QLabel(Dialog)
        self.label.setGeometry(QtCore.QRect(10, 20, 111, 16))
        font = QtGui.QFont()
        font.setBold(True)
        font.setUnderline(True)
        font.setWeight(75)
        font.setKerning(True)
        self.label.setFont(font)
        self.label.setObjectName("label")
        # self.comboBox_moduleCode = QtWidgets.QComboBox(Dialog)
        # self.comboBox_moduleCode.setGeometry(QtCore.QRect(130, 20, 87, 22))
        # self.comboBox_moduleCode.setObjectName("comboBox_moduleCode")
        self.label_module = QtWidgets.QLabel(Dialog)
        self.label_module.setGeometry(QtCore.QRect(130, 20, 87, 16))
        self.label_module.setObjectName("label_module")
        self.dateTimeEdit_startDay = QtWidgets.QDateTimeEdit(Dialog)
        self.dateTimeEdit_startDay.setGeometry(QtCore.QRect(170, 70, 141, 22))
        self.dateTimeEdit_startDay.setObjectName("dateTimeEdit_startDay")
        self.label_2 = QtWidgets.QLabel(Dialog)
        self.label_2.setGeometry(QtCore.QRect(30, 70, 121, 16))
        self.label_2.setObjectName("label_2")
        self.label_3 = QtWidgets.QLabel(Dialog)
        self.label_3.setGeometry(QtCore.QRect(420, 70, 72, 15))
        self.label_3.setObjectName("label_3")
        self.label_4 = QtWidgets.QLabel(Dialog)
        self.label_4.setGeometry(QtCore.QRect(30, 110, 101, 16))
        self.label_4.setObjectName("label_4")
        self.label_5 = QtWidgets.QLabel(Dialog)
        self.label_5.setGeometry(QtCore.QRect(420, 110, 141, 16))
        self.label_5.setObjectName("label_5")
        self.dateTimeEdit_endDay = QtWidgets.QDateTimeEdit(Dialog)
        self.dateTimeEdit_endDay.setGeometry(QtCore.QRect(520, 70, 141, 22))
        self.dateTimeEdit_endDay.setObjectName("dateTimeEdit_endDay")
        self.dateTimeEdit_cutoffDay = QtWidgets.QDateTimeEdit(Dialog)
        self.dateTimeEdit_cutoffDay.setGeometry(QtCore.QRect(170, 110, 141, 22))
        self.dateTimeEdit_cutoffDay.setObjectName("dateTimeEdit_cutoffDay")
        self.label_6 = QtWidgets.QLabel(Dialog)
        self.label_6.setGeometry(QtCore.QRect(240, 20, 41, 16))
        font = QtGui.QFont()
        font.setBold(True)
        font.setUnderline(True)
        font.setWeight(75)
        self.label_6.setFont(font)
        self.label_6.setObjectName("label_6")
        self.label_7 = QtWidgets.QLabel(Dialog)
        self.label_7.setGeometry(QtCore.QRect(30, 150, 121, 16))
        self.label_7.setObjectName("label_7")
        self.label_8 = QtWidgets.QLabel(Dialog)
        self.label_8.setGeometry(QtCore.QRect(10, 190, 72, 15))
        font = QtGui.QFont()
        font.setBold(True)
        font.setUnderline(True)
        font.setWeight(75)
        self.label_8.setFont(font)
        self.label_8.setObjectName("label_8")
        self.label_11 = QtWidgets.QLabel(Dialog)
        self.label_11.setGeometry(QtCore.QRect(490, 190, 108, 17))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.label_11.setFont(font)
        self.label_11.setObjectName("label_11")
        self.label_totalMarks = QtWidgets.QLabel(Dialog)
        self.label_totalMarks.setGeometry(QtCore.QRect(605, 190, 121, 17))
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(True)
        font.setItalic(True)
        font.setWeight(75)
        self.label_totalMarks.setFont(font)
        self.label_totalMarks.setObjectName("label_totalMarks")
        self.groupBox_attendance = QtWidgets.QGroupBox(Dialog)
        self.groupBox_attendance.setGeometry(QtCore.QRect(30, 220, 371, 71))
        font = QtGui.QFont()
        font.setItalic(True)
        self.groupBox_attendance.setFont(font)
        self.groupBox_attendance.setCheckable(True)
        self.groupBox_attendance.setChecked(False)
        self.groupBox_attendance.setObjectName("groupBox_attendance")
        self.label_12 = QtWidgets.QLabel(self.groupBox_attendance)
        self.label_12.setGeometry(QtCore.QRect(20, 30, 41, 16))
        self.label_12.setObjectName("label_12")
        self.lineEdit_attendance_tag = QtWidgets.QLineEdit(self.groupBox_attendance)
        self.lineEdit_attendance_tag.setGeometry(QtCore.QRect(60, 30, 113, 21))
        self.lineEdit_attendance_tag.setObjectName("lineEdit_attendance_tag")
        self.label_10 = QtWidgets.QLabel(self.groupBox_attendance)
        self.label_10.setGeometry(QtCore.QRect(220, 30, 72, 15))
        self.label_10.setObjectName("label_10")
        self.lineEdit_attendance_marks = QtWidgets.QLineEdit(self.groupBox_attendance)
        self.lineEdit_attendance_marks.setGeometry(QtCore.QRect(290, 30, 51, 21))
        self.lineEdit_attendance_marks.setObjectName("lineEdit_attendance_marks")
        self.groupBox_compilation = QtWidgets.QGroupBox(Dialog)
        self.groupBox_compilation.setGeometry(QtCore.QRect(30, 300, 741, 81))
        font = QtGui.QFont()
        font.setItalic(True)
        self.groupBox_compilation.setFont(font)
        self.groupBox_compilation.setCheckable(True)
        self.groupBox_compilation.setChecked(False)
        self.groupBox_compilation.setObjectName("groupBox_compilation")
        self.label_13 = QtWidgets.QLabel(self.groupBox_compilation)
        self.label_13.setGeometry(QtCore.QRect(20, 40, 41, 16))
        self.label_13.setObjectName("label_13")
        self.lineEdit_compilation_tag = QtWidgets.QLineEdit(self.groupBox_compilation)
        self.lineEdit_compilation_tag.setGeometry(QtCore.QRect(60, 40, 113, 21))
        self.lineEdit_compilation_tag.setObjectName("lineEdit_compilation_tag")
        self.label_14 = QtWidgets.QLabel(self.groupBox_compilation)
        self.label_14.setGeometry(QtCore.QRect(220, 40, 72, 15))
        self.label_14.setObjectName("label_14")
        self.lineEdit_compilation_marks = QtWidgets.QLineEdit(self.groupBox_compilation)
        self.lineEdit_compilation_marks.setGeometry(QtCore.QRect(290, 40, 51, 21))
        self.lineEdit_compilation_marks.setObjectName("lineEdit_compilation_marks")
        self.label_15 = QtWidgets.QLabel(self.groupBox_compilation)
        self.label_15.setGeometry(QtCore.QRect(380, 40, 72, 15))
        self.label_15.setObjectName("label_15")
        self.lineEdit_compilation_command = QtWidgets.QLineEdit(self.groupBox_compilation)
        self.lineEdit_compilation_command.setGeometry(QtCore.QRect(460, 40, 211, 21))
        self.lineEdit_compilation_command.setObjectName("lineEdit_compilation_command")
        self.label_9 = QtWidgets.QLabel(Dialog)
        self.label_9.setGeometry(QtCore.QRect(101, 191, 136, 16))
        self.label_9.setObjectName("label_9")
        self.lineEdit_collectFilename = QtWidgets.QLineEdit(Dialog)
        self.lineEdit_collectFilename.setGeometry(QtCore.QRect(250, 190, 171, 24))
        self.lineEdit_collectFilename.setObjectName("lineEdit_collectFilename")
        self.groupBox_customTest1 = QtWidgets.QGroupBox(Dialog)
        self.groupBox_customTest1.setGeometry(QtCore.QRect(30, 390, 741, 151))
        font = QtGui.QFont()
        font.setItalic(True)
        self.groupBox_customTest1.setFont(font)
        self.groupBox_customTest1.setCheckable(True)
        self.groupBox_customTest1.setChecked(False)
        self.groupBox_customTest1.setObjectName("groupBox_customTest1")
        self.label_16 = QtWidgets.QLabel(self.groupBox_customTest1)
        self.label_16.setGeometry(QtCore.QRect(20, 40, 41, 16))
        self.label_16.setObjectName("label_16")
        self.lineEdit_test1_tag = QtWidgets.QLineEdit(self.groupBox_customTest1)
        self.lineEdit_test1_tag.setGeometry(QtCore.QRect(60, 40, 111, 21))
        self.lineEdit_test1_tag.setText("")
        self.lineEdit_test1_tag.setObjectName("lineEdit_test1_tag")
        self.label_17 = QtWidgets.QLabel(self.groupBox_customTest1)
        self.label_17.setGeometry(QtCore.QRect(220, 40, 72, 15))
        self.label_17.setObjectName("label_17")
        self.lineEdit_test1_marks = QtWidgets.QLineEdit(self.groupBox_customTest1)
        self.lineEdit_test1_marks.setGeometry(QtCore.QRect(290, 40, 51, 21))
        self.lineEdit_test1_marks.setObjectName("lineEdit_test1_marks")
        self.label_18 = QtWidgets.QLabel(self.groupBox_customTest1)
        self.label_18.setGeometry(QtCore.QRect(380, 40, 72, 15))
        self.label_18.setObjectName("label_18")
        self.lineEdit_test1_command = QtWidgets.QLineEdit(self.groupBox_customTest1)
        self.lineEdit_test1_command.setGeometry(QtCore.QRect(460, 40, 211, 21))
        self.lineEdit_test1_command.setObjectName("lineEdit_test1_command")
        self.checkBox_test1_inputDataFile = QtWidgets.QCheckBox(self.groupBox_customTest1)
        self.checkBox_test1_inputDataFile.setGeometry(QtCore.QRect(20, 70, 161, 19))
        self.checkBox_test1_inputDataFile.setObjectName("checkBox_test1_inputDataFile")
        self.label_test1_inputDataFile = QtWidgets.QLabel(self.groupBox_customTest1)
        self.label_test1_inputDataFile.setGeometry(QtCore.QRect(180, 70, 511, 16))
        self.label_test1_inputDataFile.setText("")
        self.label_test1_inputDataFile.setObjectName("label_test1_inputDataFile")
        self.checkBox_test1_answerFile = QtWidgets.QCheckBox(self.groupBox_customTest1)
        self.checkBox_test1_answerFile.setGeometry(QtCore.QRect(20, 100, 131, 19))
        self.checkBox_test1_answerFile.setObjectName("checkBox_test1_answerFile")
        self.checkBox_test1_filterFile = QtWidgets.QCheckBox(self.groupBox_customTest1)
        self.checkBox_test1_filterFile.setGeometry(QtCore.QRect(20, 130, 121, 19))
        self.checkBox_test1_filterFile.setObjectName("checkBox_test1_filterFile")
        self.label_test1_answerFile = QtWidgets.QLabel(self.groupBox_customTest1)
        self.label_test1_answerFile.setGeometry(QtCore.QRect(170, 100, 521, 16))
        self.label_test1_answerFile.setText("")
        self.label_test1_answerFile.setObjectName("label_test1_answerFile")
        self.label_test1_filterFile = QtWidgets.QLabel(self.groupBox_customTest1)
        self.label_test1_filterFile.setGeometry(QtCore.QRect(140, 130, 331, 16))
        self.label_test1_filterFile.setText("")
        self.label_test1_filterFile.setObjectName("label_test1_filterFile")
        self.label_28 = QtWidgets.QLabel(self.groupBox_customTest1)
        self.label_28.setGeometry(QtCore.QRect(451, 130, 101, 20))
        self.label_28.setObjectName("label_28")
        self.lineEdit_test1_filterCommand = QtWidgets.QLineEdit(self.groupBox_customTest1)
        self.lineEdit_test1_filterCommand.setGeometry(QtCore.QRect(560, 130, 171, 21))
        self.lineEdit_test1_filterCommand.setObjectName("lineEdit_test1_filterCommand")
        self.groupBox_customTest2 = QtWidgets.QGroupBox(Dialog)
        self.groupBox_customTest2.setGeometry(QtCore.QRect(30, 540, 741, 141))
        font = QtGui.QFont()
        font.setItalic(True)
        self.groupBox_customTest2.setFont(font)
        self.groupBox_customTest2.setCheckable(True)
        self.groupBox_customTest2.setChecked(False)
        self.groupBox_customTest2.setObjectName("groupBox_customTest2")
        self.label_19 = QtWidgets.QLabel(self.groupBox_customTest2)
        self.label_19.setGeometry(QtCore.QRect(20, 40, 41, 16))
        self.label_19.setObjectName("label_19")
        self.lineEdit_test2_tag = QtWidgets.QLineEdit(self.groupBox_customTest2)
        self.lineEdit_test2_tag.setGeometry(QtCore.QRect(60, 40, 113, 21))
        self.lineEdit_test2_tag.setText("")
        self.lineEdit_test2_tag.setObjectName("lineEdit_test2_tag")
        self.label_20 = QtWidgets.QLabel(self.groupBox_customTest2)
        self.label_20.setGeometry(QtCore.QRect(220, 40, 72, 15))
        self.label_20.setObjectName("label_20")
        self.lineEdit_test2_marks = QtWidgets.QLineEdit(self.groupBox_customTest2)
        self.lineEdit_test2_marks.setGeometry(QtCore.QRect(290, 40, 51, 21))
        self.lineEdit_test2_marks.setObjectName("lineEdit_test2_marks")
        self.label_21 = QtWidgets.QLabel(self.groupBox_customTest2)
        self.label_21.setGeometry(QtCore.QRect(380, 40, 72, 15))
        self.label_21.setObjectName("label_21")
        self.lineEdit_test2_command = QtWidgets.QLineEdit(self.groupBox_customTest2)
        self.lineEdit_test2_command.setGeometry(QtCore.QRect(460, 40, 211, 21))
        self.lineEdit_test2_command.setObjectName("lineEdit_test2_command")
        self.checkBox_test2_inputDataFile = QtWidgets.QCheckBox(self.groupBox_customTest2)
        self.checkBox_test2_inputDataFile.setGeometry(QtCore.QRect(20, 60, 151, 19))
        self.checkBox_test2_inputDataFile.setObjectName("checkBox_test2_inputDataFile")
        self.label_test2_inputDataFile = QtWidgets.QLabel(self.groupBox_customTest2)
        self.label_test2_inputDataFile.setGeometry(QtCore.QRect(180, 60, 511, 16))
        self.label_test2_inputDataFile.setText("")
        self.label_test2_inputDataFile.setObjectName("label_test2_inputDataFile")
        self.label_test2_answerFile = QtWidgets.QLabel(self.groupBox_customTest2)
        self.label_test2_answerFile.setGeometry(QtCore.QRect(170, 90, 521, 16))
        self.label_test2_answerFile.setText("")
        self.label_test2_answerFile.setObjectName("label_test2_answerFile")
        self.checkBox_test2_filterFile = QtWidgets.QCheckBox(self.groupBox_customTest2)
        self.checkBox_test2_filterFile.setGeometry(QtCore.QRect(20, 120, 121, 19))
        self.checkBox_test2_filterFile.setObjectName("checkBox_test2_filterFile")
        self.checkBox_test2_answerFile = QtWidgets.QCheckBox(self.groupBox_customTest2)
        self.checkBox_test2_answerFile.setGeometry(QtCore.QRect(20, 90, 131, 19))
        self.checkBox_test2_answerFile.setObjectName("checkBox_test2_answerFile")
        self.label_test2_filterFile = QtWidgets.QLabel(self.groupBox_customTest2)
        self.label_test2_filterFile.setGeometry(QtCore.QRect(170, 120, 281, 16))
        self.label_test2_filterFile.setText("")
        self.label_test2_filterFile.setObjectName("label_test2_filterFile")
        self.lineEdit_test2_filterCommand = QtWidgets.QLineEdit(self.groupBox_customTest2)
        self.lineEdit_test2_filterCommand.setGeometry(QtCore.QRect(560, 120, 171, 21))
        self.lineEdit_test2_filterCommand.setObjectName("lineEdit_test2_filterCommand")
        self.label_29 = QtWidgets.QLabel(self.groupBox_customTest2)
        self.label_29.setGeometry(QtCore.QRect(450, 120, 101, 20))
        self.label_29.setObjectName("label_29")
        self.groupBox_customTest3 = QtWidgets.QGroupBox(Dialog)
        self.groupBox_customTest3.setGeometry(QtCore.QRect(30, 680, 741, 141))
        font = QtGui.QFont()
        font.setItalic(True)
        self.groupBox_customTest3.setFont(font)
        self.groupBox_customTest3.setCheckable(True)
        self.groupBox_customTest3.setChecked(False)
        self.groupBox_customTest3.setObjectName("groupBox_customTest3")
        self.label_22 = QtWidgets.QLabel(self.groupBox_customTest3)
        self.label_22.setGeometry(QtCore.QRect(20, 40, 41, 16))
        self.label_22.setObjectName("label_22")
        self.lineEdit_test3_tag = QtWidgets.QLineEdit(self.groupBox_customTest3)
        self.lineEdit_test3_tag.setGeometry(QtCore.QRect(60, 40, 113, 21))
        self.lineEdit_test3_tag.setText("")
        self.lineEdit_test3_tag.setObjectName("lineEdit_test3_tag")
        self.label_23 = QtWidgets.QLabel(self.groupBox_customTest3)
        self.label_23.setGeometry(QtCore.QRect(220, 40, 72, 15))
        self.label_23.setObjectName("label_23")
        self.lineEdit_test3_marks = QtWidgets.QLineEdit(self.groupBox_customTest3)
        self.lineEdit_test3_marks.setGeometry(QtCore.QRect(290, 40, 51, 21))
        self.lineEdit_test3_marks.setObjectName("lineEdit_test3_marks")
        self.label_24 = QtWidgets.QLabel(self.groupBox_customTest3)
        self.label_24.setGeometry(QtCore.QRect(380, 40, 72, 15))
        self.label_24.setObjectName("label_24")
        self.lineEdit_test3_command = QtWidgets.QLineEdit(self.groupBox_customTest3)
        self.lineEdit_test3_command.setGeometry(QtCore.QRect(460, 40, 211, 21))
        self.lineEdit_test3_command.setObjectName("lineEdit_test3_command")
        self.checkBox_test3_inputDataFile = QtWidgets.QCheckBox(self.groupBox_customTest3)
        self.checkBox_test3_inputDataFile.setGeometry(QtCore.QRect(20, 60, 151, 19))
        self.checkBox_test3_inputDataFile.setObjectName("checkBox_test3_inputDataFile")
        self.label_test3_inputDataFile = QtWidgets.QLabel(self.groupBox_customTest3)
        self.label_test3_inputDataFile.setGeometry(QtCore.QRect(190, 60, 511, 16))
        self.label_test3_inputDataFile.setText("")
        self.label_test3_inputDataFile.setObjectName("label_test3_inputDataFile")
        self.label_test3_answerFile = QtWidgets.QLabel(self.groupBox_customTest3)
        self.label_test3_answerFile.setGeometry(QtCore.QRect(170, 90, 521, 16))
        self.label_test3_answerFile.setText("")
        self.label_test3_answerFile.setObjectName("label_test3_answerFile")
        self.checkBox_test3_filterFile = QtWidgets.QCheckBox(self.groupBox_customTest3)
        self.checkBox_test3_filterFile.setGeometry(QtCore.QRect(20, 120, 121, 19))
        self.checkBox_test3_filterFile.setObjectName("checkBox_test3_filterFile")
        self.checkBox_test3_answerFile = QtWidgets.QCheckBox(self.groupBox_customTest3)
        self.checkBox_test3_answerFile.setGeometry(QtCore.QRect(20, 90, 131, 19))
        self.checkBox_test3_answerFile.setObjectName("checkBox_test3_answerFile")
        self.label_test3_filterFile = QtWidgets.QLabel(self.groupBox_customTest3)
        self.label_test3_filterFile.setGeometry(QtCore.QRect(170, 120, 271, 16))
        self.label_test3_filterFile.setText("")
        self.label_test3_filterFile.setObjectName("label_test3_filterFile")
        self.lineEdit_test3_filterCommand = QtWidgets.QLineEdit(self.groupBox_customTest3)
        self.lineEdit_test3_filterCommand.setGeometry(QtCore.QRect(560, 120, 171, 21))
        self.lineEdit_test3_filterCommand.setObjectName("lineEdit_test3_filterCommand")
        self.label_30 = QtWidgets.QLabel(self.groupBox_customTest3)
        self.label_30.setGeometry(QtCore.QRect(450, 120, 101, 20))
        self.label_30.setObjectName("label_30")
        self.groupBox_customTest4 = QtWidgets.QGroupBox(Dialog)
        self.groupBox_customTest4.setGeometry(QtCore.QRect(30, 820, 741, 141))
        font = QtGui.QFont()
        font.setItalic(True)
        self.groupBox_customTest4.setFont(font)
        self.groupBox_customTest4.setCheckable(True)
        self.groupBox_customTest4.setChecked(False)
        self.groupBox_customTest4.setObjectName("groupBox_customTest4")
        self.label_25 = QtWidgets.QLabel(self.groupBox_customTest4)
        self.label_25.setGeometry(QtCore.QRect(20, 40, 41, 16))
        self.label_25.setObjectName("label_25")
        self.lineEdit_test4_tag = QtWidgets.QLineEdit(self.groupBox_customTest4)
        self.lineEdit_test4_tag.setGeometry(QtCore.QRect(60, 40, 113, 21))
        self.lineEdit_test4_tag.setText("")
        self.lineEdit_test4_tag.setObjectName("lineEdit_test4_tag")
        self.label_26 = QtWidgets.QLabel(self.groupBox_customTest4)
        self.label_26.setGeometry(QtCore.QRect(220, 40, 72, 15))
        self.label_26.setObjectName("label_26")
        self.lineEdit_test4_marks = QtWidgets.QLineEdit(self.groupBox_customTest4)
        self.lineEdit_test4_marks.setGeometry(QtCore.QRect(290, 40, 51, 21))
        self.lineEdit_test4_marks.setObjectName("lineEdit_test4_marks")
        self.label_27 = QtWidgets.QLabel(self.groupBox_customTest4)
        self.label_27.setGeometry(QtCore.QRect(380, 40, 72, 15))
        self.label_27.setObjectName("label_27")
        self.lineEdit_test4_command = QtWidgets.QLineEdit(self.groupBox_customTest4)
        self.lineEdit_test4_command.setGeometry(QtCore.QRect(460, 40, 211, 21))
        self.lineEdit_test4_command.setObjectName("lineEdit_test4_command")
        self.checkBox_test4_inputDataFile = QtWidgets.QCheckBox(self.groupBox_customTest4)
        self.checkBox_test4_inputDataFile.setGeometry(QtCore.QRect(20, 60, 151, 19))
        self.checkBox_test4_inputDataFile.setObjectName("checkBox_test4_inputDataFile")
        self.label_test4_inputDataFile = QtWidgets.QLabel(self.groupBox_customTest4)
        self.label_test4_inputDataFile.setGeometry(QtCore.QRect(180, 60, 521, 16))
        self.label_test4_inputDataFile.setText("")
        self.label_test4_inputDataFile.setObjectName("label_test4_inputDataFile")
        self.label_test4_filterFile = QtWidgets.QLabel(self.groupBox_customTest4)
        self.label_test4_filterFile.setGeometry(QtCore.QRect(170, 120, 271, 16))
        self.label_test4_filterFile.setText("")
        self.label_test4_filterFile.setObjectName("label_test4_filterFile")
        self.checkBox_test4_filterFile = QtWidgets.QCheckBox(self.groupBox_customTest4)
        self.checkBox_test4_filterFile.setGeometry(QtCore.QRect(20, 120, 121, 19))
        self.checkBox_test4_filterFile.setObjectName("checkBox_test4_filterFile")
        self.checkBox_test4_answerFile = QtWidgets.QCheckBox(self.groupBox_customTest4)
        self.checkBox_test4_answerFile.setGeometry(QtCore.QRect(20, 90, 131, 19))
        self.checkBox_test4_answerFile.setObjectName("checkBox_test4_answerFile")
        self.label_test4_answerFile = QtWidgets.QLabel(self.groupBox_customTest4)
        self.label_test4_answerFile.setGeometry(QtCore.QRect(170, 90, 521, 16))
        self.label_test4_answerFile.setText("")
        self.label_test4_answerFile.setObjectName("label_test4_answerFile")
        self.lineEdit_test4_filterCommand = QtWidgets.QLineEdit(self.groupBox_customTest4)
        self.lineEdit_test4_filterCommand.setGeometry(QtCore.QRect(559, 110, 171, 21))
        self.lineEdit_test4_filterCommand.setObjectName("lineEdit_test4_filterCommand")
        self.label_31 = QtWidgets.QLabel(self.groupBox_customTest4)
        self.label_31.setGeometry(QtCore.QRect(450, 110, 101, 20))
        self.label_31.setObjectName("label_31")
        self.lineEdit_assName = QtWidgets.QLineEdit(Dialog)
        self.lineEdit_assName.setGeometry(QtCore.QRect(290, 20, 71, 21))
        self.lineEdit_assName.setObjectName("lineEdit_assName")
        self.spinBox_totalAttempts = QtWidgets.QSpinBox(Dialog)
        self.spinBox_totalAttempts.setGeometry(QtCore.QRect(170, 150, 43, 26))
        self.spinBox_totalAttempts.setObjectName("spinBox_totalAttempts")
        self.spinBox_penaltyPerDay = QtWidgets.QSpinBox(Dialog)
        self.spinBox_penaltyPerDay.setGeometry(QtCore.QRect(620, 100, 43, 26))
        self.spinBox_penaltyPerDay.setObjectName("spinBox_penaltyPerDay")

        self.retranslateUi(Dialog)
        self.buttonBox.accepted.connect(Dialog.accept)
        self.buttonBox.rejected.connect(Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Create a One-Off Assignment"))
        self.label.setText(_translate("Dialog", "Module Code:"))
        self.label_2.setText(_translate("Dialog", "Start Day:"))
        self.label_3.setText(_translate("Dialog", "End Day:"))
        self.label_4.setText(_translate("Dialog", "Cutoff Day:"))
        self.label_5.setText(_translate("Dialog", "Penalty per day (%):"))
        self.label_6.setText(_translate("Dialog", "Name:"))
        self.label_7.setText(_translate("Dialog", "Total Attempts:"))
        self.label_8.setText(_translate("Dialog", "Tests:"))
        self.label_11.setText(_translate("Dialog", "Total Marks:"))
        self.label_totalMarks.setText(_translate("Dialog", "0"))
        self.groupBox_attendance.setTitle(_translate("Dialog", "Attendance"))
        self.label_12.setText(_translate("Dialog", "Tag:"))
        self.lineEdit_attendance_tag.setText(_translate("Dialog", "attendance"))
        self.label_10.setText(_translate("Dialog", "Marks:"))
        self.groupBox_compilation.setTitle(_translate("Dialog", "Compilation"))
        self.label_13.setText(_translate("Dialog", "Tag:"))
        self.lineEdit_compilation_tag.setText(_translate("Dialog", "compilation"))
        self.label_14.setText(_translate("Dialog", "Marks:"))
        self.label_15.setText(_translate("Dialog", "Command:"))
        self.label_9.setText(_translate("Dialog", "Collect Filename:"))
        self.lineEdit_collectFilename.setPlaceholderText(_translate("Dialog", "spin.cc"))
        self.groupBox_customTest1.setTitle(_translate("Dialog", "Custom Test 1"))
        self.label_16.setText(_translate("Dialog", "Tag:"))
        self.label_17.setText(_translate("Dialog", "Marks:"))
        self.label_18.setText(_translate("Dialog", "Command:"))
        self.checkBox_test1_inputDataFile.setText(_translate("Dialog", "Input Data File"))
        self.checkBox_test1_answerFile.setText(_translate("Dialog", "Answer File"))
        self.checkBox_test1_filterFile.setText(_translate("Dialog", "Filter File"))
        self.label_28.setText(_translate("Dialog", "Filter Cmd:"))
        self.groupBox_customTest2.setTitle(_translate("Dialog", "Custom Test 2"))
        self.label_19.setText(_translate("Dialog", "Tag:"))
        self.label_20.setText(_translate("Dialog", "Marks:"))
        self.label_21.setText(_translate("Dialog", "Command:"))
        self.checkBox_test2_inputDataFile.setText(_translate("Dialog", "Input Data File"))
        self.checkBox_test2_filterFile.setText(_translate("Dialog", "Filter File"))
        self.checkBox_test2_answerFile.setText(_translate("Dialog", "Answer File"))
        self.label_29.setText(_translate("Dialog", "Filter Cmd:"))
        self.groupBox_customTest3.setTitle(_translate("Dialog", "Custom Test 3"))
        self.label_22.setText(_translate("Dialog", "Tag:"))
        self.label_23.setText(_translate("Dialog", "Marks:"))
        self.label_24.setText(_translate("Dialog", "Command:"))
        self.checkBox_test3_inputDataFile.setText(_translate("Dialog", "Input Data File"))
        self.checkBox_test3_filterFile.setText(_translate("Dialog", "Filter File"))
        self.checkBox_test3_answerFile.setText(_translate("Dialog", "Answer File"))
        self.label_30.setText(_translate("Dialog", "Filter Cmd:"))
        self.groupBox_customTest4.setTitle(_translate("Dialog", "Custom Test 4"))
        self.label_25.setText(_translate("Dialog", "Tag:"))
        self.label_26.setText(_translate("Dialog", "Marks:"))
        self.label_27.setText(_translate("Dialog", "Command:"))
        self.checkBox_test4_inputDataFile.setText(_translate("Dialog", "Input Data File"))
        self.checkBox_test4_filterFile.setText(_translate("Dialog", "Filter File"))
        self.checkBox_test4_answerFile.setText(_translate("Dialog", "Answer File"))
        self.label_31.setText(_translate("Dialog", "Filter Cmd:"))
        self.label_module.setText(_translate("Dialog", " "))
