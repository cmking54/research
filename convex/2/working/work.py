import cv2
import numpy as np
import imutils

# Notes below:
## frame --shrink?--> f
## f --blur hard--+ bgsub
## f
cam = None
TERM_KEY = 27
bgs = None
low = np.array([0, 48, 80], dtype = "uint8")
high = np.array([20, 255, 255], dtype = "uint8")
minArea = 3000.0
GOLDEN_RATIO = 1
zones = []
canvas = []

def startup():
    global cam, bgs
    cam = cv2.VideoCapture(0)
    bgs = MyBGS()
    while True:
        good, frame = cam.read()
        if good:
            frame = imutils.resize(frame, width = 600) # double check this
            if bgs.apply(frame) != None:
                break
        else:
            print "Bad Cam"
    #bgs = cv2.createBackgroundMOG2(shadows=False) # shadows shoud be detectShadows?
    #end = bgs.getHistory() # not sure if method exist
    #n = 0
    #bad = 0
    #while n < end:
    #    good, frame = cam.read()
    #    if good:
    #        frame = imutils.resize(frame, width = 600) # double check this
    #        bgs.apply(frame)
    #        n += 1
    return cam
def doWork():
    good, frame = cam.read()
    if not good:
        print "Bad Cam"
        return frame # cannot return frame
    frame = imutils.resize(frame, width = 600) # double check this
    mzones = bgs.apply(frame)
    hsv = cv2.cvtColor(frame,cv2.COLOR_BGR2HSV) # investigate feeding hsv frames to bgsub
    mask = cv2.inRange(hsv,low,high)
    ####
    kr = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    ks = np.ones((5,5),np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kr)
    #mask = cv2.erode(mask, kernel, iterations = 2)
    mask = cv2.dilate(mask, kr, iterations = 2)
 
    # blur the mask to help remove noise, then apply the
    # mask to the frame
    #mask = cv2.GaussianBlur(mask, (3, 3), 0)
    #sf = cv2.bitwise_and(f, f, mask = mask)

    # box good zones
    global zones, canvas
    #canvas = [frame.copy()]
    czones = []
    _, cns, _ = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    fc = frame.copy()
    for c in cns:
        a = cv2.contourArea(c)
        if a >= minArea:#scale based on dist of user
            rect = cv2.boundingRect(c)
            czones += [(rect,c)]
    for cz in czones: # make this a funct
        r,c = cz
        cv2.drawContours(fc, c, -1, (122,122,0), 3)
        cv2.rectangle(fc, (r[0], r[1]), (r[0] + r[2], r[1] + r[3]), (0, 255, 0), 2)
    #cv2.imshow("c1",fc)
    #canvas += [fc]

    #if len(czones) == 0: # not needed
    #    return frame
        # find which zones in mzones and czones are important and distill them for analysis ### FIXME
    #for zone in zones:
    for cz in czones:
        cr = cz[0]
        #carea = cr[2] * cr[3]
        for mz in mzones:
            bound_test = [mz[0] > cr[0] and mz[0] < cr[0] + cr[2] 
                          and mz[1] > cr[1] and mz[1] < cr[1] + cr[3], 
                          mz[0] + mz[2] > cr[0] and mz[0] + mz[2] < cr[0] + cr[2] 
                          and mz[1] + mz[3] > cr[1] and mz[1] + mz[3] < cr[1] + cr[3]]
            if True in bound_test:
                del mz
                zones += [cz]
        # use this style below to distill
#            if True not in bound_test: # simple test above, pass distillation out and begin analysis <- referring to the current block
#                continue
#            marea = mz[2] * mz[3]
#            minarea = min(carea,marea)
#            maxarea = max(carea,marea)
#
#            if iarea > minarea and iarea < maxarea:
#                del mz        
#                zones += [cr]
#    for z in zones:
#        r,c = z
#        cv2.drawContours(frame, c, -1, (122,122,0), 3)
#        cv2.rectangle(frame, (r[0], r[1]), (r[0] + r[2], r[1] + r[3]), (0, 255, 0), 2)
    #zones = czones[:]
    fc2 = frame.copy()
    def getDefectInfo(d,c):
        s,e,f,de = d
        return tuple(c[s][0]), tuple(c[e][0]), tuple(c[f][0]), de
    for z in zones: # FUTURE: info = getFingerInfo(z)
        rect, con = z
        # old cog
        M = cv2.moments(con)
        cX = int(M["m10"] / M["m00"])
        cY = int(M["m01"] / M["m00"])
        cv2.circle(fc2, (cX, cY), 7, (0, 0, 255), -1)
        #
        hpts = cv2.convexHull(con,returnPoints = False)
        dfts = cv2.convexityDefects(con,hpts)
        lowd = -1
        saved = []
        dt = 0
        dacc = 0
        lastd = -1
        drange = 2000
        maybe_finger_groups = []
        finger_group = []
        for i in range(dfts.shape[0]):
            s,e,f,d = getDefectInfo(dfts[i,0], con)
            if d > 1000.0 * (1/GOLDEN_RATIO):
                dt += d
                dacc += 1
                if dacc != 1:
                    if d > lastd - drange and d < lastd + drange:
                        lastd = d
                        #finger_group += [
                cv2.circle(fc2,f,7,[0,255,255],-1)
                cv2.circle(fc2,e,7,[0,255,0],-1)
        #cv2.drawContours(fc2, [con], -1, (0, 255, 255), 2)
        cHull = cv2.convexHull(con)
        cv2.drawContours(fc2, [cHull], -1, (255, 0, 0), 2)
        #cv2.line(fc2,tuple(con[s][0]),tuple(con[e][0]),(255,0,255),3)
#        davg = dt / dacc
#        print davg
#        for i in range(dfts.shape[1]):
#            s,e,f,d = dfts[i,0]
#            if d < davg:
#                cv2.line(fc2,tuple(con[s][0]),tuple(con[f][0]),(255,0,255),3)
#                cv2.line(fc2,tuple(con[f][0]),tuple(con[e][0]),(255,0,255),3)
#                #cv2.line(fc2,tuple(con[s][0]),tuple(con[e][0]),(255,0,255),3)
    #canvas += [fc2]
    canvas = [fc2]
    zones = [] # needs some restart
    return frame # will change later
def keyCheck(d=5):
    cv2.imshow("main",np.hstack(canvas))
    if cv2.waitKey(1) & 0xff == ord('s'):
        cv2.imwrite(raw_input("Name: "),np.hstack(canvas))
    return cv2.waitKey(d) & 0xff
def cleanUp():
    cam.release() # fail-safe needed
    cv2.destroyAllWindows()

class MyBGS():
    def __init__(self,history=1,learningRate=0.05): # last default param = 10, 0.0055
        # history neglib, lr directly proportionally to how large a motion we want to keep
        self.acrd = 0
        self.h = history

        self.lr = learningRate

    def apply(self,frame,diffdist=35): #diffdist controls how much latency
        ret = frame.copy()
        ret = cv2.cvtColor(ret, cv2.COLOR_BGR2GRAY) # gray
        ret = cv2.GaussianBlur(ret, (11, 11), 0) # heavy blur
        try:
            self.base
        except AttributeError:
            self.base = np.float32(ret.copy()) # float may be able to be removed
        if self.acrd < self.h:
            cv2.accumulateWeighted(ret,self.base,0.5)
            self.acrd+=1
            return None
        cv2.accumulateWeighted(ret,self.base,self.lr)
        ret = np.uint8(cv2.absdiff(self.base, np.float32(ret)))
        _, ret = cv2.threshold(ret, diffdist, 255, cv2.THRESH_BINARY)
        #ret = cv2.morphologyEx(ret, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (15, 15)))
        #ret = cv2.erode(ret, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3)), iterations=1)
        ret = cv2.dilate(ret, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5)), iterations=5)
        ret = cv2.morphologyEx(ret, cv2.MORPH_OPEN,cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (15, 15)))
        mA = 4000.0 #scale based on dist of user
        mr = np.array([])
        rs = []
        _,cs,_ = cv2.findContours(ret.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        for c in cs:
            a = cv2.contourArea(c)
            if a >= mA:
                rect = cv2.boundingRect(c)
                rs += [rect]
        for r in rs:
            cv2.rectangle(ret, (r[0], r[1]), (r[0] + r[2], r[1] + r[3]), 255, 2)
        cv2.imshow("m3",ret)

        #if mr.size != 0:
            #cv2.drawContours(frame, mr, -1, (122,122,0), 3)
            #rect = cv2.boundingRect(mr)
            #cv2.rectangle(frame, (rect[0], rect[1]), (rect[0] + rect[2], rect[1] + rect[3]), (0, 255, 0), 2)
            #cv2.imshow("t3",frame)
        #ret = cv2.bitwise_and(frame,frame,mask=ret)
        #cv2.imshow("m1",np.uint8(self.base))
        #cv2.imshow("m2",ret)
        return rs


#class Gesture():

## Optional below
#class Hand():
#class Finger():

