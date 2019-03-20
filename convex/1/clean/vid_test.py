import cv2
cap = cv2.VideoCapture(0)
while cv2.waitKey(5) & 0xff != 27:
    _, f = cap.read()
    cv2.imshow("teSt",f)
cap.release()
cv2.destroyAllWindows()
