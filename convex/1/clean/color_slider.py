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
win_height = 600

# chris' vars
slider_name = 'HSV_Tracker'
color_val = [BLUISH_HUE, MIN_SAT, MIN_VAL]
preview = None

def initSlider():
    '''
    Sets up window
    '''
    cv2.namedWindow(slider_name)
    def cb_0(x):
        color_val[0] = x
    def cb_1(x):
        color_val[1] = x
    def cb_2(x):
        color_val[2] = x
    cv2.createTrackbar('h', slider_name, color_val[0], MAX_HUE, cb_0)
    cv2.createTrackbar('s', slider_name, color_val[1], MAX_SAT, cb_1)
    cv2.createTrackbar('v', slider_name, color_val[2], MAX_VAL, cb_2)
    #preview = initImage(win_width,win_height)
    return color_val

def showSlider(frame):
    '''
    Transforms frame and
    shows in namedwindow;
    returns color bounds
    '''
    lower_color, upper_color = clampedColorRange()
    preview = initImage(win_width,win_height) #has to be a better way...
    scaled_frame = cv2.resize(frame,(win_height/2, win_width/2),interpolation = cv2.INTER_AREA) #interpolation???
    color_trans = cv2.cvtColor(scaled_frame,cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(color_trans, lower_color, upper_color)
    end_res = cv2.bitwise_and(scaled_frame, scaled_frame, mask=mask)
    preview[0:win_width/2,0:win_height/2] = scaled_frame # upper left, clockwise
    preview[win_width/2:win_width,0:win_height/2] = color_trans
    preview[0:win_width/2,win_height/2:win_height] = cv2.cvtColor(mask,cv2.COLOR_GRAY2BGR)
    preview[win_width/2:win_width,win_height/2:win_height] = end_res
    cv2.imshow(slider_name, preview)
    return (lower_color, upper_color)

def initImage(twidth, theight):
    '''
    Makes empty pic
    '''
    return np.zeros( shape=(twidth, theight, IMG_COLOR_DEPTH), dtype=IMG_NP_TYPE)

def clampedColorRange():
    '''
    Gets color bounds
    '''
    lowHue = max(color_val[0] - HUE_DIST, 0)
    highHue = min(color_val[0] + HUE_DIST, MAX_HUE)
    small = np.array([lowHue, color_val[1], color_val[2]])
    high = np.array([highHue, MAX_SAT, MAX_VAL])
    return small, high

# THIS IS A TEST; NOT MEANT TO BE USED
#c_v = initSlider()
#c = cv2.VideoCapture(0)
#while 1:
    #_, f = c.read()
    #showSlider(f)
    #k = cv2.waitKey(5) & 0xFF 
    #if k == 27:
        #break
    #elif k == ord('s'): # UTIL below
        #trkd = raw_input("What are you tracking: ")
        #s = "%s: %d %d %d" % (trkd, color_val[0], color_val[1], color_val[2])
        #f = open("slider_saves.txt", 'a')
        #f.write(s+'\n')
        #f.close()
#cv2.destroyAllWindows()
