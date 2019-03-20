import cv2
import numpy as np

toolbox = []
toolbox += [np.ones((11,11),np.uint8)]
toolbox += [cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(8,8))]
toolbox += [cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(5,5))]
toolbox += [cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(3,3))]

def initVideo(width=1000, height=600):
	cap = cv2.VideoCapture(0)
	cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
	cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
	return cap

def getFrame(img):
    '''
	Smoothes immediately,
	and changes it to HSV.
	'''
    #cv2.imshow("Check", img)
    res = cv2.blur(img,(3,3)) # expanded for readablitity
    res = cv2.cvtColor(res,cv2.COLOR_BGR2HSV)
    return res

def getMask(frame,slider_info):
	'''
	Uses a draw_surface to only give whitespace
	for what we desire, skin, and returns it
	'''
	res = cv2.inRange(frame,slider_info[0],slider_info[1]) # should be from slider info (si)
	res = cv2.dilate(res,toolbox[1],iterations = 1)
	res = cv2.erode(res,toolbox[0],iterations = 1)
	res = cv2.dilate(res,toolbox[1],iterations = 1)
	res = cv2.medianBlur(res,5)
	res = cv2.dilate(res,toolbox[2],iterations = 1)
	res = cv2.dilate(res,toolbox[3],iterations = 1)
	res = cv2.medianBlur(res,5)
	_,res = cv2.threshold(res,127,255,0)
	# add bgSub in here, add masks together or use outside to determine region of interest
	return res

def getFocus(frame,mask,verbose=True): # contour with largest area
	'''
	Traces closed areas of whitespace,
	and picks best fit to be investigated
	'''
	tmp, contours, hierarchy = cv2.findContours(mask,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE) # double check this
	max_area = 100
	focus_index = -1
    for i in range(len(contours)):
        contour = contours[i]
        area = cv2.contourArea(contour)
        if(area > max_area):
            max_area = area
            focus_index = i
    if focus_index < 0: # can fail
        return None
    elif verbose:
        cv2.drawContours(frame, contours[focus_index], -1, (122,122,0), 3)
    return contours[focus_index]

def getFocusInfo(focus, verbose=False):
	#hull = cv2.convexHull(focus)
	hull_pts = cv2.convexHull(focus,returnPoints = False)

	# Defects
	defects = cv2.convexityDefects(focus,hull_pts)
	if verbose:
		for i in range(defects.shape[0]):
			s,e,f,d = defects[i,0]
			start = tuple(cnts[s][0])
			end = tuple(cnts[e][0])
			far = tuple(cnts[f][0])
			#cv2.line(draw_surface,start,end,[0,255,0],1)
			#cv2.circle(draw_surface,far,10,[100,y,y],3)

	# COG
	M = cv2.moments(focus)
	COG = (int(M['m10']/M['m00']), int(M['m01']/M['m00']))
	if verbose:
		cv2.circle(draw_surface,COG,7,[100,0,255],2)
		font = cv2.FONT_HERSHEY_SIMPLEX
		cv2.putText(draw_surface,'Center',tuple(COG),cv2.FONT_HERSHEY_SIMPLEX,2,(255,255,255),2)
	return defects, COG

def getFingers(defects,moments,verbose=True,Chris=False):
	#set batch to 3 and get min
	if Chris:
		return
	else:
		for i in range(len(defects)):
			_,_,f,_ = getDefectAt(i,defects,focus)
			PsuedoMath.addToBatch(PsuedoMath.distance(f,COG))
		avg_defect_dist = np.mean(PseudoMath.getBatch())

def getDefectAt(i,defects,focus): #why the tuple
	return tuple(focus[defects[i,0][0]][0]),tuple(focus[defects[i,0][1]][0]),tuple(focus[defects[i,0][2]][0]),focus[defects[i,0][3]][0]

