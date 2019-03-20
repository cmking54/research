#Experimental goal: sliders for selecting a low HSV value
#Camera image is filtered with low, high calues
#Long term goal: used to seed skin color
#for OpenCV 3.0

import cv2
import numpy as np

BLUISH_HUE = 25
HUE_DIST = 15
MAX_HUE = 179

MIN_SAT = 0
MAX_SAT = 255

MIN_VAL = 0
MAX_VAL = 255

IMG_COLOR_DEPTH = 3
IMG_NP_TYPE = np.uint8

win_width = 512
win_height = 200

# chris' vars
slider_name = 'HSV_Tracker'
color_val = [BLUISH_HUE, MIN_SAT, MIN_VAL]
preview = None

def initSlider():
    cv2.namedWindow(slider_name)
    cv2.createTrackbar('h', slider_name, color_val[0], MAX_HUE, None) #fix this lambda
    cv2.createTrackbar('s', slider_name, color_val[1], MAX_SAT, None)
    cv2.createTrackbar('v', slider_name, color_val[2], MAX_VAL, None)
    preview = initImage(win_width,win_height) #has to be a better way...
    return color_val


    def a(fs):
        return cv2.cvtColor(fs[0],cv2.COLOR_BGR2HSV)
    def b(fs):
        return cv2.inRange(fs[1], lower_color, upper_color)
    def c(fs):
        return cv2.bitwise_and(fs[0],fs[0],mask=fs[2])

def showSlider(frame):
    #HSV_win = initOneColorImage(HSV_win_height, HSV_win_width)
    lower_color, upper_color = clampedColorRange()
    makeFourWayWindow(
    cv2.imshow(slider_name, preview)
    return lower_color, upper_color

### 08/03/16 ###
def makeFourWayWindow(img,base,t1=None,t2=None,t3=None,name=""): #util
    #img_width = ## FIX ME
    #img_height = 
    #empty = 
    sc = cv2.resize(base,(0.5*img_width,0.5*img_height),interpolation=cv2.INTER_AREA) #interpolation???
    ## ^^ look in to imutils ^^
    img[0:img_width/2,0:img_height/2] = sc
    img[img_width/2:img_width,0:img_height/2] = empty if t1 == None else t1(sc)
    img[0:img_width/2,img_height/2:img_height] = empty if t2 == None else t2(sc)
    img[img_width/2:img_width,img_height/2:img_height] = empty if t3 == None else t3(sc)

    if name != "":
        cv2.imshow(name,img)
    return img
################

def initImage(twidth, theight): # util (also give saving mechanism in there)
    return np.zeros( shape=(twidth, theight, IMG_COLOR_DEPTH), dtype=IMG_NP_TYPE)

def clampedColorRange():
    lowHue = max(color_val[0] - HUE_DIST, 0)
    highHue = min(color_val[0] + HUE_DIST, MAX_HUE)
    small = np.array([lowHue, color_val[1], color_val[2]])
    high = np.array([highHue, MAX_SAT, MAX_VAL])
    return small, high

#def getTinyImageConverted(color, mode=cv2.COLOR_BGR2HSV):
    #img = np.uint8([[color]])
    #return cv2.cvtColor(img, mode)

#def getSVWindowTrackerValues():
    #th = cv2.getTrackbarPos('h', slider_name)
    #ts = cv2.getTrackbarPos('s', slider_name)
    #tv = cv2.getTrackbarPos('v', slider_name)
    #return th, ts, tv
