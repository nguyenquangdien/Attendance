import face_recognition
import constants

def recognize(encoding_data, image_item):
    encodings = face_recognition.face_encodings(image_item[0], image_item[1])
    # initialize the list of names for each face detected
    names = []

    # loop over the facial embeddings
    for encoding in encodings:
        # attempt to match each face in the input to our known encodings
        # This function returns a list of True / False  values, one for each image in our dataset.
        # since the dataset has 218 Jurassic Park images, len(matches)=218
        matches = face_recognition.compare_faces(encoding_data[constants.ENCODING_DATA], encoding)
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