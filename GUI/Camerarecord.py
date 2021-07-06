import tkinter
import cv2
import PIL.Image, PIL.ImageTk
import time
import threading

class MyVideoCapture:

    def __init__(self, fps=None):
    
        self.video_source = 1
        self.width = 400
        self.height = 300
        self.fps = fps
        self.video_available = False
        
        # Open the video source
        self.vid = cv2.VideoCapture(self.video_source)
        if not self.vid.isOpened():
            self.video_available = False
            #raise ValueError("[MyVideoCapture] Unable to open video source", self.video_source) 
        else:
            self.video_available = True


        # Get video source width and height
        if not self.width:
            self.width = int(self.vid.get(cv2.CAP_PROP_FRAME_WIDTH))    # convert float to int
        if not self.height:
            self.height = int(self.vid.get(cv2.CAP_PROP_FRAME_HEIGHT))  # convert float to int
        if not self.fps:
            self.fps = int(self.vid.get(cv2.CAP_PROP_FPS))  # convert float to int

        # default value at start        
        self.ret = False
        self.frame = None

        # start thread
        self.running = True
        self.thread = threading.Thread(target=self.process)
        self.thread.start()
        
    def process(self):
        while self.running:
            ret, frame = self.vid.read()
            
            if ret:
                # process image
                frame = cv2.resize(frame, (self.width, self.height))
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            else:
                print('[MyVideoCapture] stream end:', self.video_source)
                # TODO: reopen stream
                self.running = False
                break
                
            # assign new frame
            self.ret = ret
            self.frame = frame
            
            # sleep for next frame
            time.sleep(1/self.fps)
        
    def get_frame(self):
        return self.ret, self.frame
    
    def stop(self):
        self.running=False
    
    # Release the video source when the object is destroyed
    def __del__(self):
        # stop thread
        if self.running:
            self.running = False
            self.thread.join()

        # relase stream
        if self.vid.isOpened():
            self.vid.release()
