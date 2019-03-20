import cv2
import numpy as np
import matplotlib.pyplot as plot
mog2 = cv2.createBackgroundSubtractorMOG2(detectShadows=False) # can also custom make this
k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(3,3))

#def init(): # may want this for other files?

def updateBGSub(f):
    return mog2.apply(f, learningRate=1)

def getRoI(frame,minArea=2500.0,verbose=False):
    fm2 = updateBGSub(frame)
    fm2 = cleanUp(fm2)
    _, cns, _ = cv2.findContours(fm2.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    # this cannibalizes fm2 (or whatever is put there)
    ma = minArea # min area
    mc = np.array([])
    for c in cns:
        a = cv2.contourArea(c)
        if a >= ma:
            mc = c
            ma = a
    if mc.size == 0:
        return RoI((),None)
    (x, y, w, h) = cv2.boundingRect(mc)
    r1 = fm2[y:y+h,x:x+w]
    cv2.imshow("LOok here", r1)
    r2 = frame[y:y+h,x:x+w]
    r2 = cv2.cvtColor(r2,cv2.COLOR_BGR2HSV)
    hues = np.zeros(180)
    for ty in range(h):
        for tx in range(w):
            if r1[ty,tx] == 255:
                #print r2[ty,tx]
                hues[r2[ty,tx,0]]+=1
    #print hues
    print 
    hist,_ = np.histogram(hues,180,[0,179])
    plot.hist(hist,bins='auto')
    plot.show()












    #r1 = fm2[y:y+h,x:x+w]
    #r2 = frame[y:y+h,x:x+w]
    #r3 = frame[y:y+h,x:x+w]
    #r2 = cv2.cvtColor(r2,cv2.COLOR_BGR2HSV)
    #avg_hsv = np.array([0,0,0],np.float32) #2
    #avg_hsv = [0,0,0] #1 # apparently doesn't matter which (<-- || ^^)
    #avg_check = [0,0,0]
    #ps = 0
    #for ty in range(h):
    #    for tx in range(w):
    #        if r1[ty,tx] > 0:
    #            pix = r2[ty,tx]
    #            #avg_hsv[0] += pix[0] #1
    #            #avg_hsv[1] += pix[1] #1
    #            #avg_hsv[2] += pix[2] #1
    #            avg_hsv = np.add(avg_hsv,pix) #2
    #
    #            r3[ty,tx] = [10,0,255]
    #            avg_check = np.add(avg_check,r3[ty,tx]) 
    #            ps += 1
    #avg_hsv[0] /= ps #1
    #avg_hsv[1] /= ps #1
    #avg_hsv[2] /= ps #1
    #avg_hsv = np.divide(avg_hsv, ps) #2
    #avg_hsv = np.uint8(avg_hsv)
    #avg_check = np.divide(avg_check, ps) #2
    #avg_check = np.uint8(avg_check)
    #
    #print avg_check
    #cv2.imshow("T",r1)
    #cv2.imshow("e",np.asarray([[avg_hsv]*100]*100,np.uint8)) # preview window
    #cv2.imshow("r",np.asarray([[avg_check]*100]*100,np.uint8)) # preview window
    #cv2.imshow("s",cv2.cvtColor(np.asarray([[avg_hsv]*100]*100,np.uint8),cv2.COLOR_HSV2BGR)) # preview window
    #cv2.imshow("t",r3)
    
    ##Failed Attepts
    ##r2[ty,tx] = np.array([0,0,0],np.uint8)
    ##cv2.imshow("T",r1[np.where(r1 > 0)])
    if verbose:
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
    return RoI((x,y,w,h),[0,0,0])

def cleanUp(f):
    f = cv2.morphologyEx(f, cv2.MORPH_CLOSE, k)
    return f

class RoI(): # is this needed? ## for organization?
    def __init__(self,t,a):
        if t == ():
            self.null = True #shouldn't be needed
        else:
            self.null = False
            self.x = t[0]
            self.y = t[1]
            self.w = t[2]
            self.h = t[3]
            self.hsv_color = a
    def exists(self):
        return not self.null
    def getX(self):
        return self.x
    def getY(self):
        return self.y
    def getWidth(self):
        return self.w
    def getHeight(self):
        return self.h
    def getTrackingColor(self):
        return self.hsv_color
    def getFromImg(self,im):
        return im[self.y:self.y+self.h,self.x:self.x+self.w]
    def getRelativePoint(self,pt):
        return (pt[0]+self.x,pt[1]+self.y)
    def getPoint(self):
        return (self.x,self.y)
