import face_recognition
import constants
import imutils

def recognize(encoding_data, rgb_image):
    # resize width of 750px (to speedup processing)
    rgb_image = imutils.resize(rgb_image, width=750)
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
        matches = face_recognition.compare_faces(encoding_data[constants.ENCODING_DATA], encoding, tolerance=0.5)
        name = "Unknown"

        # check to see if we have found any matches
        if True in matches:
            # find the indexes of all matched faces then initialize a dictionary to count
            # the total number of times each face was matched
            matchedIdxs = [i for (i, b) in enumerate(matches) if b]
            counts = {}

            # loop over the matched indexes and maintain a count for each recognized face face
            for i in matchedIdxs:
                name = encoding_data[constants.ENCODING_NAME][i]
                counts[name] = counts.get(name, 0) + 1

            # determine the recognized face with the largest number of votes: (notes: in the event of an unlikely
            # tie, Python will select first entry in the dictionary)
            name = max(counts, key=counts.get)
        names.append(name)
    
    print("List of label: " + ', '.join(names))
    return names