# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'CustomerDialog.ui'
#
# Created by: PyQt5 UI code generator 5.15.4
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication, QDialog, QMainWindow, QPushButton, QLabel

class CustomDialog(QDialog):
    def __init__(self, Dialog):
        super().__init__(Dialog)
        Dialog.setObjectName("Dialog")
        Dialog.resize(345, 156)
        self.label = QLabel(Dialog)
        self.label.setGeometry(QtCore.QRect(40, 40, 271, 31))
        self.label.setObjectName("label")
        self.okBtn = QPushButton(Dialog)
        self.okBtn.setGeometry(QtCore.QRect(110, 110, 93, 28))
        self.okBtn.setObjectName("okBtn")

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Đăng ký thông tin học sinh"))
        self.label.setText(_translate("Dialog", "TextLabel"))
        self.okBtn.setText(_translate("Dialog", "OK"))

    def setText(self, text):
        _translate = QtCore.QCoreApplication.translate
        self.label.setText(_translate("Dialog", text))