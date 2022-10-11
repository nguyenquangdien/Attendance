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
from PyQt5.QtCore import pyqtSignal, QThread

class RegisterFace(QThread):
    registerSingal = pyqtSignal(str)

    def __init__(self, image_queue, label) -> None:
        QThread.__init__(self)
        self.label = label
        self.image_queue = image_queue
        self.encoding = True

        
    def run(self):
        # initialize the list of known encodings and known names
        knownEncodings = []
        knownNames = []
        count = 0
        while count < constants.NUM_ENCODE_IMG and self.encoding:
            if self.image_queue.qsize() > 0:
                # get image from queue and 
                rgb_image = self.image_queue.get()

                # detect the (x,y)-coordinates of the bounding boxes
                # corresponding to each face in the input image
                # we are assuming the the boxes of faces are the SAME FACE or SAME PERSON
                boxes = face_recognition.face_locations(rgb_image, model=constants.DETECTION_METHOD_HOG)
                # Only accept 1 face per image
                if len(boxes) != 1:
                    continue

                count += 1

                # compute the facial embedding for the face
                # creates a vector of 128 numbers representing the face
                encodings = face_recognition.face_encodings(rgb_image, boxes)

                # loop over the encodings
                for encoding in encodings:
                    # add each encoding + name to our set of known names and encodings
                    knownEncodings.append(encoding)
                    knownNames.append(self.label)
                
                # write image to file
                #cv2.imwrite(os.path.join(constants.ENCODING_FOLDER_PATH, label + str(count) + ".jpg"), image_item[0])

                # sleep
                # time.sleep(1)
                # with self.image_queue.mutex:
                #     self.image_queue.queue.clear()
            else:
                time.sleep(1)

        # testing data
        data = {constants.ENCODING_DATA : knownEncodings, constants.ENCODING_NAME : knownNames}
        result = self.testing_encoding_data(self.label, data)

        file_path = ""
        if result:
            # dump the facial encodings + names to disk
            print("[INFO] serializing encodings...")
            file_path = os.path.join(constants.ENCODING_FOLDER_PATH, self.label + ".tmp")
            f = open(file_path, "wb")
            f.write(pickle.dumps(data))
            f.close()

        self.registerSingal.emit(file_path)

    def testing_encoding_data(self, target_label, data) -> bool:
        while self.image_queue.qsize() == 0:
            time.sleep(1)    
        
        rgb_image = self.image_queue.get()
        # detect the (x,y)-coordinates of the bounding boxes
        # corresponding to each face in the input image
        # we are assuming the the boxes of faces are the SAME FACE or SAME PERSON
        boxes = face_recognition.face_locations(rgb_image, model=constants.DETECTION_METHOD_HOG)

        encodings = face_recognition.face_encodings(rgb_image, boxes)

        # initialize the list of names for each face detected
        names = []

        # loop over the facial embeddings
        for encoding in encodings:
            # attempt to match each face in the input to our known encodings
            # This function returns a list of True / False  values, one for each image in our dataset.
            # since the dataset has 218 Jurassic Park images, len(matches)=218
            matches = face_recognition.compare_faces(data[constants.ENCODING_DATA], encoding)
            name = "Unknown"

            # check to see if we have found any matches
            if True in matches:
                # find the indexes of all matched faces then initialize a dictionary to count
                # the total number of times each face was matched
                matchedIdxs = [i for (i, b) in enumerate(matches) if b]
                counts = {}

                # loop over the matched indexes and maintain a count for each recognized face face
                for i in matchedIdxs:
                    name = data[constants.ENCODING_NAME][i]
                    counts[name] = counts.get(name, 0) + 1

                # determine the recognized face with the largest number of votes: (notes: in the event of an unlikely
                # tie, Python will select first entry in the dictionary)
                name = max(counts, key=counts.get)
            names.append(name)
        
        print("List of label: " + ', '.join(names))
        return (target_label in names) 
    
    def stop(self):
        self.encoding = False
            


