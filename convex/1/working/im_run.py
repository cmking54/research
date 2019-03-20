import cv2
import sys
import numpy as np
import frame_worker as fw
#import color_slider as cs #color_slider under construction

'''
Will run analysis on any
image given from the command
line and in the same directory
'''

hue_dist = 11
s = np.array([3, 8, 65]), np.array([hue_dist, 255, 255])


for fn in sys.argv[1:]:
    cv2.namedWindow(fn)
    ds = cv2.imread(fn) # color may be an issue
    f = fw.getFrame(ds)
    m = fw.getMask(f,s)
    foc = fw.getFocus(ds,m,verbose=True)
    if foc.size == 0:
        d, c = fw.getFocusInfo(foc,verbose=True) # not finished yet
        #frame = fw.getFingers(d,c)
    cv2.imshow(fn, ds)
cv2.waitKey(0)
cv2.destroyAllWindows()
