# THIS IS A TEST; NOT MEANT TO BE USED
#cap = fw.initVideo()
##mog = cv2.createBackgroundSubtractorMOG()
#mog2 = cv2.createBackgroundSubtractorMOG2(detectShadows=False)
#k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(5,5))
#k2 = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(7,7))
##gmg = cv2.createBackgroundSubtractorGMG()
#while cv2.waitKey(5) & 0xff != 27:
    #ret, frame = cap.read()
    ##fm = mog.apply(frame)
    #fm2 = mog2.apply(frame)
    #fm2 = cv2.morphologyEx(fm2, cv2.MORPH_OPEN, k)
    ##fm2 = cv2.morphologyEx(fm2, cv2.MORPH_CLOSE, k2)
    ##fg = gmg.apply(frame)
    ##fg = cv2.morphologyEx(fg, cv2.MORPH_OPEN, kernel)
    ##cv2.imshow("mog",fm)
    #cv2.imshow("mog2",fm2)
    ##cv2.imshow("gmg",fg)
    #_, cns, _ = cv2.findContours(fm2, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    #for c in cns:
        #if cv2.contourArea(c) < 5000.0:
            #continue
        #(x, y, w, h) = cv2.boundingRect(c)
        #cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        #cv2.imshow("hand",frame[y:y+h, x:x+w])
        #break
        #cv2.imshow("End", frame)
#cap.release()
#cv2.destroyAllWindows()
