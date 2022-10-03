import threading
import time
import cv2
import queue


IMG_SIZE    = 1280,720          # 640,480 or 1280,720 or 1920,1080
DISP_SCALE  = 2                # Scaling factor for display image
DISP_MSEC   = 50                # Delay between display cycles
CAP_API     = cv2.CAP_ANY       # API: CAP_ANY or CAP_DSHOW etc...
EXPOSURE    = 0                 # Zero for automatic exposure

class WebCamHandler(object):
    def __init__(self) -> None:
        self.image_queue = queue.Queue()
        self.capturing = False

    # Grab images from the camera (separate thread)
    def grab_images(self):
        cap = cv2.VideoCapture(0)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, IMG_SIZE[0])
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, IMG_SIZE[1])
        if EXPOSURE:
            cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0)
            cap.set(cv2.CAP_PROP_EXPOSURE, EXPOSURE)
        else:
            cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 1)
        while self.capturing:
            if cap.grab():
                retval, image = cap.retrieve(0)
                if image is not None and self.image_queue.qsize() < 2:
                    #self.image_queue.put(image)
                    self.callback(image)
                else:
                    time.sleep(DISP_MSEC / 1000.0)
            else:
                print("Error: can't grab camera image")
                break
        cap.release()
    
    def startCapture(self, callback):
        self.capturing = True
        self.callback = callback
        self.capture_thread = threading.Thread(target=self.grab_images, args=())
        self.capture_thread.start()         # Thread to grab images

    def stopCapture(self):
        self.capturing = False
