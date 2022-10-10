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


class RecognizeFace(object):
    def __init__(self, image_queue) -> None:
        self.image_queue = image_queue
        self.running = False
        #self.loading_data_thread = threading.Thread(target = self.loading_data, args = ())
        #self.loading_data_thread.start()
        self.loading_data()
        self.loading_finished = False 

    def loading_data(self):
        # get all endcoding files
        encodingFilePaths = []
        for file in os.listdir(constants.ENCODING_FOLDER_PATH):
            if file.endswith(constants.ENCODING_FILE_EXT):
                encodingFilePaths.append(file)

        # load encoding data
        bytes_data = bytearray()
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
        
    def recognize_face(self, result_callback):
        count = 0
        while self.running:
            if self.image_queue.qsize() > 0:
                count += 1
                # get image from queue and 
                image_item = self.image_queue.get()
                names = common.recognize(self.encoding_data, image_item)
                result = False
                for name in names:
                    if name != "Unknown":
                        # success
                        result = True

                if result or count >= constants.NUM_RECOGNIZE_IMG:
                    # don't recognize anymore
                    result_callback(result, name)
                    count = 0
            else:
                time.sleep(1)

    def start(self, result_callback):
        self.running = True
        self.recognize_face_thread = threading.Thread(target = self.recognize_face, args = (result_callback,))
        self.recognize_face_thread.start() 
    
    def stop(self):
        self.running = False
            


