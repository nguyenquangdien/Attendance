import threading
import time

from imutils import paths
import face_recognition
import pickle
import cv2
import os
import argparse
import queue

NUMBER_IMAGE = 10
DETECTION_METHOD = 'hog'
ENCODING_FILE = ".\encodings_file.pkl"



class RegisterFace(object):
    def __init__(self, image_queue) -> None:
        self.image_queue = image_queue
        self.encoding = False
        
    def encoding_face(self, label, result_callback):
        # initialize the list of known encodings and known names
        knownEncodings = []
        knownNames = []
        count = 0
        while count < 10 and self.encoding:
            if self.image_queue.qsize() > 0:
                count += 1
                # get image from queue and 
                image_item = self.image_queue.get()

                # compute the facial embedding for the face
                # creates a vector of 128 numbers representing the face
                encodings = face_recognition.face_encodings(image_item[0], image_item[1])

                # loop over the encodings
                for encoding in encodings:
                    # add each encoding + name to our set of known names and encodings
                    knownEncodings.append(encoding)
                    knownNames.append(label)
            else:
                time.sleep(1)

        # testing data
        data = {"encodings": knownEncodings, "names": knownNames}
        result = self.testing_encoding_data(label, data)
        result_callback(result)

        if result:
            # dump the facial encodings + names to disk
            print("[INFO] serializing encodings...")
            f = open(ENCODING_FILE, "ab+")
            f.write(pickle.dumps(data))
            f.close()

    def testing_encoding_data(self, target_label, data) -> bool:
        while self.image_queue.qsize() == 0:
            time.sleep(1)    
        
        image_item = self.image_queue.get()
        encodings = face_recognition.face_encodings(image_item[0], image_item[1])

        # initialize the list of names for each face detected
        names = []

        # loop over the facial embeddings
        for encoding in encodings:
            # attempt to match each face in the input to our known encodings
            # This function returns a list of True / False  values, one for each image in our dataset.
            # since the dataset has 218 Jurassic Park images, len(matches)=218
            matches = face_recognition.compare_faces(data["encodings"], encoding)
            name = "Unknown"

            # check to see if we have found any matches
            if True in matches:
                # find the indexes of all matched faces then initialize a dictionary to count
                # the total number of times each face was matched
                matchedIdxs = [i for (i, b) in enumerate(matches) if b]
                counts = {}

                # loop over the matched indexes and maintain a count for each recognized face face
                for i in matchedIdxs:
                    name = data['names'][i]
                    counts[name] = counts.get(name, 0) + 1

                # determine the recognized face with the largest number of votes: (notes: in the event of an unlikely
                # tie, Python will select first entry in the dictionary)
                name = max(counts, key=counts.get)
            names.append(name)
        
        print("List of label: " + ', '.join(names))
        return (target_label in names)

    def start(self, label, result_callback):
        self.encoding = True
        self.encoding_thread = threading.Thread(target = self.encoding_face, args = (label, result_callback,))
        self.encoding_thread.start() 
    
    def stop(self):
        self.encoding = False
            


