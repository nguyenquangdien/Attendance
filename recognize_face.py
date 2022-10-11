import threading
import time

from imutils import paths
import face_recognition
import pickle
import cv2
import os
import argparse
import queue
import constants
import common
import numpy
from PyQt5.QtCore import pyqtSignal, QThread

class RecognizeFace(QThread):
    recognizedSignal = pyqtSignal(bool, str)

    def __init__(self, image_queue) -> None:
        QThread.__init__(self)
        self.image_queue = image_queue
        self.running = True
        self.loading_data()
        self.loading_finished = False 

    def loading_data(self):
        # get all endcoding files
        encodingFilePaths = []
        for file in os.listdir(constants.ENCODING_FOLDER_PATH):
            if file.endswith(constants.ENCODING_FILE_EXT):
                encodingFilePaths.append(file)

        # load encoding data
        encoding_in_file = []
        name_in_file = []
        for encodingFile in encodingFilePaths:
            abs_file_path = os.path.join(constants.ENCODING_FOLDER_PATH, encodingFile)
            file_data = open(abs_file_path, "rb").read()
            encoding_data = pickle.loads(bytes(file_data))
            for item in encoding_data[constants.ENCODING_DATA]:
                encoding_in_file.append(item)
            for item in encoding_data[constants.ENCODING_NAME]:
                name_in_file.append(item)  
                     

        self.encoding_data = {constants.ENCODING_DATA : encoding_in_file, constants.ENCODING_NAME : name_in_file}
        self.loading_finished = True
        
    def run(self):
        count = 0
        while self.running:
            if self.image_queue.qsize() > 0:
                count += 1
                # get image from queue and 
                rgb_image = self.image_queue.get()
                names = common.recognize(self.encoding_data, rgb_image)
                result = False
                found_name = ""
                for name in names:
                    if name != "Unknown":
                        # success
                        result = True
                        found_name = name

                if result or count >= constants.NUM_RECOGNIZE_IMG:
                    # don't recognize anymore
                    self.recognizedSignal.emit(result, found_name)
                    count = 0
            else:
                time.sleep(1)
    
    def stop(self):
        self.running = False
            


