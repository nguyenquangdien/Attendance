# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'StudentRecognize.ui'
#
# Created by: PyQt5 UI code generator 5.15.4
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QTimer, QPoint, pyqtSignal
from PyQt5.QtGui import QFont, QPainter, QImage, QTextCursor
from PyQt5.QtWidgets import QApplication, QMainWindow, QTextEdit, QLabel, QDialog
from recognize_face import RecognizeFace
from image_widget import ImageWidget
from webcam import WebCamHandler
import queue
import cv2
import face_recognition
import constants

from db_access.student_repository import StudentRepository
from db_access.attendance_repository import AttendanceRepository
from db_access.class_repository import ClassRepository
from db_access.entities import StudentEntity, ClassEntity, AttendanceEntity
from datetime import date, datetime

IMG_FORMAT          = QImage.Format_RGB888

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(632, 686)
        self.imgWidget = ImageWidget(Dialog)
        self.imgWidget.setGeometry(QtCore.QRect(10, 20, 611, 361))
        self.imgWidget.setObjectName("imgWidget")
        self.guideLabel = QtWidgets.QLabel(Dialog)
        self.guideLabel.setGeometry(QtCore.QRect(150, 400, 281, 51))
        font = QtGui.QFont()
        font.setPointSize(14)
        font.setBold(True)
        font.setWeight(75)
        self.guideLabel.setFont(font)
        self.guideLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.guideLabel.setObjectName("guidelabel")
        self.listView = QtWidgets.QListView(Dialog)
        self.listView.setGeometry(QtCore.QRect(10, 480, 611, 192))
        self.listView.setObjectName("listView")

        self.image_queue = queue.Queue()
        self.webcamHandler = WebCamHandler()
        self.recognizeFace = RecognizeFace(self.image_queue)
        self.classRepository = ClassRepository(constants.DATABASE_FILE_PATH)
        self.studentRepository = StudentRepository(constants.DATABASE_FILE_PATH)
        self.attendanceRepository = AttendanceRepository(constants.DATABASE_FILE_PATH)

        self.webcamHandler.startCapture(self.captureImageCallback)
        self.recognizeFace.start(self.recognizeCallback)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        self.guideLabel.setText(_translate("Dialog", "TextLabel"))




    def captureImageCallback(self, image):
        # Display image from webcam
        self.show_image(image, self.imgWidget, 1) 
        
        #convert from BGR to RGB for dlib
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        # detect the (x,y)-coordinates of the bounding boxes
        # corresponding to each face in the input image
        # we are assuming the the boxes of faces are the SAME FACE or SAME PERSON
        boxes = face_recognition.face_locations(rgb_image, model=constants.DETECTION_METHOD_HOG)
        if len(boxes) > 0 :
            X = boxes[0][3] # left 
            Y = boxes[0][0] # top
            H = boxes[0][2] - boxes[0][0]
            W = boxes[0][1] - boxes[0][3]
            #cropped_image = rgb_image[Y:Y+H, X:X+W]

            self.image_queue.put((rgb_image, boxes))

    def recognizeCallback(self, result, student_id):
        result_text = ""
        if result:
            result_text = "Nhận dạng thành công"
        else:
            result_text = "Nhận dạng thất bại, vui lòng thử lại"

        # Get information of student
        students = self.studentRepository.get_by_student_id(student_id)
        if len(students) > 0:
            # get class name
            class_name = ""
            classes = self.classRepository.get_class(students[0].class_id)
            if len(classes) > 0:
                class_name = classes[0].name

            result_text += "\n"
            result_text += students[0].name + " - " + students[0].student_id + " - " + class_name

            # store in attendance table
            today = date.today()
            now = datetime.now()
            attendance = AttendanceEntity(None, today.strftime("%d/%m/%Y"), students[0].student_id, now.strftime("%d/%m/%Y %H:%M:%S"), None)
            self.attendanceRepository.add_attendance(attendance)

            # show to list
        else:
            print("Cannot found student info")    

        self.guideLabel.setText(result_text)
        with self.image_queue.mutex:
            self.image_queue.queue.clear()


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

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Dialog = QtWidgets.QDialog()
    ui = Ui_Dialog()
    ui.setupUi(Dialog)
    Dialog.show()
    sys.exit(app.exec_())
