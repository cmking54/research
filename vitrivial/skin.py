import cv2
import constants
import imutils
import numpy as np
#from scipy.stats import itemfreq
from algo_class import AlgoClass

from tools import Tools


class Skin(AlgoClass):

    def __init__(self):
        AlgoClass.__init__(self)
        self.img = None
        self.mask = None
        self.ycr_cb = None

    def get_active_regions(self, image):#, back_mask=None):
        """
        :param image: BGR image
        :param back_mask:
        :return: a copy of the BGR image masked to only show skin regions
        """
        self.img = image.copy()

        # http://www.learnopencv.com/color-spaces-in-opencv-cpp-python/
        self.ycr_cb = cv2.cvtColor(self.img, cv2.COLOR_BGR2YCR_CB)

        # define range for skin color in ycr_cb
        lower_ycr_cb_color = np.array(constants.MIN_SKIN_COLOR)
        upper_ycr_cb_color = np.array(constants.MAX_SKIN_COLOR)

        # threshold the ycr_cb image to get only skin colors
        self.mask = cv2.inRange(self.ycr_cb, lower_ycr_cb_color, upper_ycr_cb_color)

        res = cv2.bitwise_and(self.img, self.img, mask=self.mask)
        # if back_mask is not None:
        #     self.log_text('combined')
        #     #  TO DO: I hope it is AND. Please check
        #     res = cv2.bitwise_and(res, res, mask=back_mask)

        return res


    # def ....
    # True background: no color skin use cluster function to find dominant colors
    # Tools.cluster(img)



# histogram solution in general case
# http://docs.opencv.org/trunk/d1/db7/tutorial_py_histogram_begins.html


