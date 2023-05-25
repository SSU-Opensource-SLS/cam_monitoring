import time
import cv2
import imutils
import platform
from pathlib import Path

import numpy as np
from threading import Thread
from queue import Queue

# # MPII에서 각 파트 번호, 선으로 연결될 POSE_PAIRS
# BODY_PARTS = { "Head": 0, "Neck": 1, "RShoulder": 2, "RElbow": 3, "RWrist": 4,
#                 "LShoulder": 5, "LElbow": 6, "LWrist": 7, "RHip": 8, "RKnee": 9,
#                 "RAnkle": 10, "LHip": 11, "LKnee": 12, "LAnkle": 13, "Chest": 14,
#                 "Background": 15 }
# POSE_PAIRS = [ ["Head", "Neck"], ["Neck", "RShoulder"], ["RShoulder", "RElbow"],
#                 ["RElbow", "RWrist"], ["Neck", "LShoulder"], ["LShoulder", "LElbow"],
#                 ["LElbow", "LWrist"], ["Neck", "Chest"], ["Chest", "RHip"], ["RHip", "RKnee"],
#                 ["RKnee", "RAnkle"], ["Chest", "LHip"], ["LHip", "LKnee"], ["LKnee", "LAnkle"] ]
# protoFile = "/home/oslab/openpose/models/pose/mpi/pose_deploy_linevec.prototxt"
# weightsFile = "/home/oslab/openpose/models/pose/mpi/pose_iter_160000.caffemodel"
# net = cv2.dnn.readNetFromCaffe(protoFile, weightsFile)
# capture = cv2.VideoCapture(0) #카메라 정보 받아옴
# inputWidth=320;
# inputHeight=240;
# inputScale=1.0/255;


class Streamer :
    
    def __init__(self ):
        
        if cv2.ocl.haveOpenCL() :
            cv2.ocl.setUseOpenCL(True)
        print('OpenCL : ', cv2.ocl.haveOpenCL())
            
        self.capture = None
        self.thread = None
        self.width = 640
        self.height = 360
        self.stat = False
        self.current_time = time.time()
        self.preview_time = time.time()
        self.sec = 0
        self.Q = Queue(maxsize=128)
        self.started = False
        
    def run(self, src = 0 ) :
        
        self.stop()
    
        if platform.system() == 'Windows' :        
            self.capture = cv2.VideoCapture( src , cv2.CAP_DSHOW )
        
        else :
            self.capture = cv2.VideoCapture( src )
            
        self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
        self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
        
        if self.thread is None :
            self.thread = Thread(target=self.update, args=())
            self.thread.daemon = False
            self.thread.start()
        
        self.started = True
    
    def stop(self):
        
        self.started = False
        
        if self.capture is not None :
            
            self.capture.release()
            self.clear()
            
    def update(self):
                    
        while True:

            if self.started :
                (grabbed, frame) = self.capture.read()
                
                if grabbed : 
                    self.Q.put(frame)
                          
    def clear(self):
        
        with self.Q.mutex:
            self.Q.queue.clear()
            
    def read(self):

        return self.Q.get()

    def blank(self):
        
        return np.ones(shape=[self.height, self.width, 3], dtype=np.uint8)
    
    def bytescode(self):
        
        if not self.capture.isOpened():
            
            frame = self.blank()

        else :
            
            frame = imutils.resize(self.read(), width=int(self.width) )
        
            if self.stat :  
                cv2.rectangle( frame, (0,0), (120,30), (0,0,0), -1)
                fps = 'FPS : ' + str(self.fps())
                cv2.putText  ( frame, fps, (10,20), cv2.FONT_HERSHEY_PLAIN, 1, (0,0,255), 1, cv2.LINE_AA)
            
        # frameWidth = frame.shape[1]
        # frameHeight = frame.shape[0]
        # inpBlob = cv2.dnn.blobFromImage(frame, inputScale, (inputWidth, inputHeight), (0, 0, 0), swapRB=False, crop=False)
        # imgb=cv2.dnn.imagesFromBlob(inpBlob)
        # net.setInput(inpBlob)
        # output = net.forward()
        # points = []
        # for i in range(0,15):
        #     probMap = output[0, i, :, :]
        #     minVal, prob, minLoc, point = cv2.minMaxLoc(probMap)
        #     x = (frameWidth * point[0]) / output.shape[3]
        #     y = (frameHeight * point[1]) / output.shape[2]
        #     if prob > 0.1 :    
        #         cv2.circle(frame, (int(x), int(y)), 3, (0, 255, 255), thickness=-1, lineType=cv2.FILLED) # circle(그릴곳, 원의 중심, 반지름, 색)
        #         cv2.putText(frame, "{}".format(i), (int(x), int(y)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1, lineType=cv2.LINE_AA)
        #         points.append((int(x), int(y)))
        #     else :
        #         points.append(None)
        # for pair in POSE_PAIRS:
        #     partA = pair[0]             # Head
        #     partA = BODY_PARTS[partA]   # 0
        #     partB = pair[1]             # Neck
        #     partB = BODY_PARTS[partB]   # 1
        #     if points[partA] and points[partB]:
        #         cv2.line(frame, points[partA], points[partB], (0, 255, 0), 2)




        return cv2.imencode('.jpg', frame )[1].tobytes()
    
    def fps(self):
        
        self.current_time = time.time()
        self.sec = self.current_time - self.preview_time
        self.preview_time = self.current_time
        
        if self.sec > 0 :
            fps = round(1/(self.sec),1)
            
        else :
            fps = 1
            
        return fps
                   
    def __exit__(self) :
        print( '* streamer class exit')
        self.capture.release()