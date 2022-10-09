
from pydoc import classname
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QDialog, QMessageBox
from db_access.student_repository import StudentRepository
from db_access.class_repository import ClassRepository

import constants
from registered_student_list_ui import RegisteredStudentListUI
from registered_student_model import TableModel

import cv2
import face_recognition
import queue
import os


class RegisteredStudentListDialog(QDialog, RegisteredStudentListUI):
    def __init__(self) -> None:
        super().__init__(None)
        self.setupUi(self)
        # set data for table
        self.studentTableHeader = ["Họ và tên", "Mã học sinh", "Ngày sinh", "Lớp"]
        self.classComboBox.currentIndexChanged.connect(self.onSelectedClassChanged)
        self.studentRepository = StudentRepository(constants.DATABASE_FILE_PATH)
        self.classRepository = ClassRepository(constants.DATABASE_FILE_PATH)
        self.loadingData()

    def loadingData(self):
        # Get data of class
        self.classEntities = self.classRepository.get_all_classes()
        classNames = ["Tất cả"]
        for entity in self.classEntities:
            classNames.append(entity.name)

        # Set data for combobox class
        self.classComboBox.addItems(classNames) 
        self.classComboBox.setCurrentIndex(0)                

    def onSelectedClassChanged(self):
        className = self.classComboBox.currentText()
        classId = self.getClassIdFromName(className)
        
        self.model = self.studentRepository.get_students_by_class_id(classId)
        self.registeredStudentModel = TableModel(self.model, self.studentTableHeader)
        self.studentTableView.setModel(self.registeredStudentModel)


    def getClassIdFromName(self, name) -> int:
        for entity in self.classEntities:
            if entity.name == name:
                return entity.id
        return -1