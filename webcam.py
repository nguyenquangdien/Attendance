from asyncio import constants
import threading
import time
import cv2
import queue
from PyQt5.QtCore import pyqtSignal, QThread
import numpy
import constants

DISP_MSEC   = 50                # Delay between display cycles
CAP_API     = cv2.CAP_ANY       # API: CAP_ANY or CAP_DSHOW etc...
EXPOSURE    = 0                 # Zero for automatic exposure

class WebCamHandler(QThread):
    imgSignal = pyqtSignal(numpy.ndarray)

    def __init__(self) -> None:
        QThread.__init__(self)
        self.capturing = True

    # Grab images from the camera (separate thread)
    def run(self):
        cap = cv2.VideoCapture(0)
        w = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
        h = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
        x = (int)((w - constants.FACE_SIZE[0]) / 2)
        y = (int)((h - constants.FACE_SIZE[1]) / 2)
        if EXPOSURE:
            cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0)
            cap.set(cv2.CAP_PROP_EXPOSURE, EXPOSURE)
        else:
            cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 1)
        while self.capturing:
            if cap.grab():
                retval, image = cap.retrieve(0)
                if image is not None:
                    image = image[y:(y + constants.FACE_SIZE[1]), x:(x + constants.FACE_SIZE[0])]
                    self.imgSignal.emit(image)
                else:
                    time.sleep(DISP_MSEC / 1000.0)
            else:
                print("Error: can't grab camera image")
                break
        cap.release()
    
    # def startCapture(self, callback):
    #     self.capturing = True
    #     self.callback = callback
    #     self.capture_thread = threading.Thread(target=self.grab_images, args=())
    #     self.capture_thread.start()         # Thread to grab images

    def stopCapture(self):
        self.capturing = False
        self.wait()
