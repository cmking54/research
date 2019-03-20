#!/usr/bin/python
import cv2
import numpy as np
import frame_worker as fw
#import color_slider as cs #color_slider under construction
import motion_tracker as mt

#hue_dist = 9
cap = fw.initVideo()
slider = np.array([0, 25, 89]), np.array([6, 97, 164])
def cCR(c,hd=20,sd=15,vd=60):# mod me
    lH = max(c[0] - hd, 0)
    hH = min(c[0] + hd, 179)
    lS = max(c[1] - sd, 0)
    hS = min(c[1] + sd / 2, 255)
    lV = max(c[2] - vd, 0)
    hV = min(c[2] + vd / 2, 255)
    small = np.array([lH, lH, lV])
    high = np.array([hH,hS,hV])
    #print "A: ", c,"L: ", small,"H: ", high 
    return small, high


win_name = "End Result"
cv2.namedWindow(win_name)
dbcodes = [] # cmdline argv
key = 0
gotHand = False
fc = 0
TM = -1
warmup = 0

def step(delay=5): #UTIL
    return cv2.waitKey(delay) & 0xFF

while key != 27:
    _, draw_surface = cap.read()
    if 0 in dbcodes:
        cv2.imshow("0: base img", draw_surface)
    if key == ord('s'): #UTIL
        cv2.imwrite(raw_input("Name: "), draw_surface)
    elif key == ord('l'):
        gotHand = False
    ###
    mt.updateBGSub(draw_surface)
    if warmup < 15:
        warmup+=1
        continue
    ###
    if not gotHand: # bgsem needs every frame
        region = mt.getRoI(draw_surface,verbose=1 in dbcodes)
    if region.exists():
        gotHand = True
        if 1 in dbcodes:
            cv2.imshow("1: motion based roi",region.getFromImg(draw_surface))
    ###
    if gotHand:
        frame = fw.getFrame(region.getFromImg(draw_surface))
        if 2 in dbcodes:
            cv2.imshow("2: initial prep", frame)
    ###
        slider = cCR(region.getTrackingColor())
        mask = fw.getMask(frame,slider)
        if 3 in dbcodes:
            cv2.imshow("3: cleaned mask", mask)
    ###
        focus = fw.getFocus(draw_surface,region,mask,verbose=4 in dbcodes)
        if focus.size != 0:
    ###
            defects, COG = fw.getFocusInfo(draw_surface,region,focus,verbose=5 in dbcodes) # not finished yet
    ###     
            #frame = fw.getFingers(defects,COG,verbose=6 in dbcodes) # if not aFingerFound: gotHand = False
    ###
        if fc > TM:
            fc = 0
            #gotHand = False
        else:
            fc+=1
    #print fc
    cv2.imshow(win_name, draw_surface)
    key = step()
cap.release()
cv2.destroyAllWindows()
