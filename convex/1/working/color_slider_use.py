# THIS IS A TEST; NOT MEANT TO BE USED DIRECTLY

import color_slider as cs
import frame_worker as fw
c_v = cs.initSlider()
c = fw.initVideo()
while 1:
    _, f = c.read()
    showSlider(f)
    if waitKey(5) & 0xFF == 27:
        break
cv2.destroyAllWindows()
