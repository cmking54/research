import cv2
import numpy as np
import frame_worker as fw
import color_slider as cs

cap = fw.initVideo() # Chris fix here -> fw
#toolbox = fw.initToolbox()
initial_color = cs.initSlider()

test_img = "hand1.jpg"
video = True
raw_img = cv2.imread(test_img) # 1 = Normal Color (BGR)
raw_img = cv2.resize(raw_img,(1000,600), interpolation=cv2.INTER_AREA) # change dims to whatever suitable
draw_surface = raw_img[:]
win_name = "End Result"
cv2.namedWindow(win_name)
'''
This is the main loop for Video 
and Image Capture and Process.
'''
while cv2.waitKey(75) & 0xFF != 27:
	if video: # video mode is working fine, but may be stressful for simple cpu to test with; feel free to comment out until it is viable
		_, draw_surface = cap.read()
	else: # image mode is broken ... 
		draw_surface[:] = raw_img[:]
	slider = cs.showSlider(draw_surface)
	frame = fw.getFrame(draw_surface)
	mask = fw.getMask(frame,slider)
	focus = fw.getFocus(draw_surface,mask) # verbose = True
	if focus == None: 
		continue
	#defects, COG = fw.getFocusInfo(focus) # not finished yet
	#frame = fw.getFingers(defects,COG)
	cv2.imshow(win_name, draw_surface) # maybe fix to be like color_slider???

if video:
	cap.release()
cv2.destroyAllWindows
