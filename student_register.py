# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'StudentRegister.ui'
#
# Created by: PyQt5 UI code generator 5.15.4
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from email.policy import default
from pydoc import classname
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QTimer, QPoint, pyqtSignal
from PyQt5.QtGui import QFont, QPainter, QImage, QTextCursor
from PyQt5.QtWidgets import QDialog, QMessageBox, QMainWindow
from custom_dialog import CustomDialog
from register_face import RegisterFace
from db_access.student_repository import StudentRepository
from db_access.entities import StudentEntity
from db_access.class_repository import ClassRepository
from PyQt5.QtCore import Qt

from webcam import WebCamHandler
from image_widget import ImageWidget
import constants
from student_register_window_ui import StudentRegisterMainWindowUI
from registered_student_list import RegisteredStudentListDialog

import cv2
import face_recognition
import queue
import os

IMG_FORMAT          = QImage.Format_RGB888
DISP_MSEC           = 50                # Delay between display cycles
DISP_SCALE          = 1                # Scaling factor for display image

GUIDE_GET_SAMPLE_START      = "Đưa mặt vào chính giữa camera"
GUIDE_GET_SAMPLE_SUCCESS    = "Lấy mẫu thành công"
GUIDE_GET_SAMPLE_FAILURE    = "Lấy mẫu thất bại, vui lòng thử lại"
GUIDE_SAVE_SUCCESS          = "Lưu dữ liệu thành công"

class StudentRegisterMainWindow(QMainWindow, StudentRegisterMainWindowUI):
    def __init__(self) -> None:
        super().__init__(None)
        self.setupUi(self)
        self.getSampleButton.clicked.connect(self.onClickedStartBtn)
        self.saveButton.clicked.connect(self.onClickedSaveBtn)
        self.cancelButton.clicked.connect(self.onClickedCancelBtn)
        self.registeredStudentAction.triggered.connect(self.onClickedRegisteredStudent)

        self.image_queue = queue.Queue()
        self.webcamHandler = WebCamHandler()
        self.registerFace = RegisterFace(self.image_queue)

        self.classRepository = ClassRepository(constants.DATABASE_FILE_PATH)
        self.studentRepository = StudentRepository(constants.DATABASE_FILE_PATH)

        self.cur_encoding_path = ""

        self.loadingData()

    def loadingData(self):
        # Get data of class
        self.classEntities = self.classRepository.get_all_classes()
        classNames = []
        for entity in self.classEntities:
            classNames.append(entity.name)
        # Set data for combobox class
        self.classComboBox.addItems(classNames) 
        # get image and display
        default_img_path = os.path.join(constants.RESOURCE_FOLDER, "facercg.png")
        self.default_img = QImage(default_img_path)
        self.imgWidget.setImage(self.default_img)

    def resetUI(self):
        self.nameLineEdit.text("")
        studentId = self.studentIdLineEdit.text()
        studentClass = self.classComboBox.currentText()

    def onClickedStartBtn(self):
        print("startBtn clicked")
        self.guideLabel.setText(GUIDE_GET_SAMPLE_START)
        studentName = self.nameLineEdit.text()
        studentId = self.studentIdLineEdit.text()
        studentClass = self.classComboBox.currentText()
        studentBirthday = self.birthdayDateEdit.date()

        if (studentId is None or studentId == "" or
            studentName is None or studentName == "" or
            studentClass is None or studentClass == ""):
            # Missing information
            # Show warning message
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setText("Bạn chưa nhập đủ thông tin")
            msg.setWindowTitle("Cảnh bảo")
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec()
            return

        # Start webcam and register face thread
        self.webcamHandler.startCapture(self.captureImageCallback)
        self.registerFace.start(studentId, self.registerCallback)

        # change state of buttons
        self.getSampleButton.setEnabled(False)
        self.saveButton.setEnabled(False)
        self.cancelButton.setEnabled(True)


    def captureImageCallback(self, image):
        #convert from BGR to RGB for dlib
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        # detect the (x,y)-coordinates of the bounding boxes
        # corresponding to each face in the input image
        # we are assuming the the boxes of faces are the SAME FACE or SAME PERSON
        boxes = face_recognition.face_locations(rgb_image, model=constants.DETECTION_METHOD_HOG)
        if len(boxes) == 1 :
            # Only accept 1 face per image
            X = boxes[0][3] # left 
            Y = boxes[0][0] # top
            H = boxes[0][2] - boxes[0][0]
            W = boxes[0][1] - boxes[0][3]
            #cropped_image = rgb_image[Y:Y+H, X:X+W]
            self.image_queue.put((rgb_image, boxes))

            # display image to UI
            self.show_image(image[Y-60:Y+H+60, X-40:X+W+40], self.imgWidget, DISP_SCALE) 

    def registerCallback(self, result, encode_file_path):
        result_text = ""
        if result:
            result_text = GUIDE_GET_SAMPLE_SUCCESS
            self.guideLabel.setText(result_text)
            self.cur_encoding_path = encode_file_path
            self.saveButton.setEnabled(True)
            self.getSampleButton.setEnabled(True)
        else:
            result_text = GUIDE_GET_SAMPLE_FAILURE
            self.guideLabel.setText(result_text)
            self.cur_encoding_path = ""
            self.saveButton.setEnabled(True)
            self.getSampleButton.setEnabled(True)
            self.imgWidget.setImage(self.default_img)
        # stop camera
        self.webcamHandler.stopCapture()

    # Fetch camera image from queue, and display it
    def show_image(self, image, display, scale):
        if image is not None and len(image) > 0:
            img = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            self.display_image(img, display, scale)
            

    # Display an image, reduce size if required
    def display_image(self, img, display, scale=1):
        #disp_size = img.shape[1]//scale, img.shape[0]//scale
        size = self.imgWidget.size()
        disp_size = size.width(), size.height()
        disp_bpl = disp_size[0] * 3
        img = cv2.resize(img, disp_size, interpolation=cv2.INTER_CUBIC)
        qimg = QImage(img.data, disp_size[0], disp_size[1], 
                      disp_bpl, IMG_FORMAT)
        display.setImage(qimg)    

    def onClickedSaveBtn(self):
        print("saveBtn clicked")
        if self.cur_encoding_path == "":
            return

        # store to db   
        studentId = self.studentIdLineEdit.text()
        studentName = self.nameLineEdit.text()
        birthday = self.birthdayDateEdit.text()
        className = self.classComboBox.currentText()
        classId = self.getClassIdFromName(className)
     
        existedStudents = self.studentRepository.get_by_student_id(studentId)
        if len(existedStudents) > 0:
            # Show warning message
            msg = QMessageBox()
            #msg.setIcon(QMessageBox.Warning)
            msg.setText("Mã học sinh này đã tồn tại, bạn có muốn cập nhật thông tin?")
            msg.setWindowTitle("Cảnh bảo")
            msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel)
            returnVal = msg.exec()
            if returnVal:
                # Update student information
                file_path = os.path.join(constants.ENCODING_FOLDER_PATH, studentId + ".pkl")
                if os.path.exists(file_path):
                    os.remove(file_path)
                os.rename(self.cur_encoding_path, file_path)
                self.studentRepository.update_by_student_id(studentId, studentName, birthday, classId, file_path)
                self.cur_encoding_path = ""
                self.saveButton.setEnabled(False)
                self.cancelButton.setEnabled(False)
                self.guideLabel.setText(GUIDE_SAVE_SUCCESS)
                return        
            else:
                # do nothing
                return
        else:
            file_path = os.path.join(constants.ENCODING_FOLDER_PATH, studentId + ".pkl")
            if os.path.exists(file_path):
                os.remove(file_path)
            os.rename(self.cur_encoding_path, file_path)
            student_entity = StudentEntity(None, studentName, studentId, birthday, classId, file_path)
            self.studentRepository.add_student(student_entity)
            self.cur_encoding_path = ""
            self.saveButton.setEnabled(False)
            self.cancelButton.setEnabled(False)
            self.guideLabel.setText(GUIDE_SAVE_SUCCESS)


    def onClickedCancelBtn(self):
        print("cancelBtn clicked")
        self.webcamHandler.stopCapture()
        self.registerFace.stop()
        if (self.cur_encoding_path != "" and os.path.exists(self.cur_encoding_path)):
            os.remove(self.cur_encoding_path)
            self.cur_encoding_path = ""
        # update UI
        self.guideLabel.setText(GUIDE_GET_SAMPLE_START)
        self.imgWidget.setImage(self.default_img)
        self.getSampleButton.setEnabled(True)
        self.saveButton.setEnabled(False)
        self.cancelButton.setEnabled(False)

    def getClassIdFromName(self, name) -> int:
        for entity in self.classEntities:
            if entity.name == name:
                return entity.id
        return -1

    def onClickedRegisteredStudent(self):
        registerStudentList = RegisteredStudentListDialog()
        registerStudentList.exec()

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    mainWindow = StudentRegisterMainWindow()
    mainWindow.show()
    sys.exit(app.exec_())
