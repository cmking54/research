#enable this for the cv user or not or both?
import work as w
#import cv2
cam = w.startup() # maybe rename to init()
kc = -1
while kc != w.TERM_KEY:
    #f = 
    w.doWork()
    #cv2.imshow("in run",f)
    kc = w.keyCheck()
w.cleanUp()
#    acts = w.findGestures()
#    for act in acts:
#        if act in name2act:
#            name2act[act]()
#        else:
#            print "Not Known Gesture"
