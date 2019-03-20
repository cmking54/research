import cv2
import constants
import numpy as np


class Tools:

    SMALL_ROUND_KERNEL = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, constants.SMALL_KERNEL_SIZE)
    MID_ROUND_KERNEL = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, constants.MID_KERNEL_SIZE)
    BIG_ROUND_KERNEL = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, constants.BIG_KERNEL_SIZE)

    SMALL_RECT_KERNEL = cv2.getStructuringElement(cv2.MORPH_RECT, constants.SMALL_KERNEL_SIZE)
    MID_RECT_KERNEL = cv2.getStructuringElement(cv2.MORPH_RECT, constants.MID_KERNEL_SIZE)
    BIG_RECT_KERNEL = cv2.getStructuringElement(cv2.MORPH_RECT, constants.BIG_KERNEL_SIZE)

    """
       Image conversion methods
    """

    def __init__(self):
        pass

    @staticmethod
    def dilate(mask, kernel):
        return cv2.dilate(mask, kernel=kernel, iterations=2)

    @staticmethod
    def erode(mask, kernel):
        return cv2.erode(mask, kernel=kernel, iterations=2)

    @staticmethod
    def close_mask(mask, kernel):
        return cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel=kernel)

    @staticmethod
    def close_mask(mask):
        return cv2.morphologyEx(mask, cv2.MORPH_CLOSE, Tools.SMALL_ROUND_KERNEL)


    @staticmethod
    #https://stackoverflow.com/questions/43111029/how-to-find-the-average-colour-of-an-image-in-python-with-opencv
    def cluster(img):
        arr = np.float32(img)
        pixels = arr.reshape((-1, 3))

        n_colors = 3
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 5)
        flags = cv2.KMEANS_RANDOM_CENTERS
        _, labels, centroids = cv2.kmeans(pixels, n_colors, None, criteria, 10, flags)

        print "centroid ", centroids
        palette = np.uint8(centroids)
        quantized = palette[labels.flatten()]
        quantized = quantized.reshape(img.shape)

        #needed
        #dominant_color = palette[np.argmax(itemfreq(labels)[:, -1])]
        return quantized

    @staticmethod
    def difference_image(f1, f2):
        """(image, image) -> image"""
        #  with videos made of static images: returned image is all black
        #  caveats: some small int
        return cv2.absdiff(f1, f2)

    @staticmethod
    def gray_image(f1):
        return cv2.cvtColor(f1, cv2.COLOR_BGR2GRAY)

    #  bilateral filter: expensive but remove details while keeping edge
    #  consider to do it initially to set color and not later
    @staticmethod
    def pre_process_image(img):
        # recommended 5=d for real-time application
        # work on this magic numbers
        return cv2.bilateralFilter(img, 5, 80, 80)



    @staticmethod
    # #  should it be small size for detecting change?
    # #  should be of size later?
    def threshold_image(gray_img):
        """(gray scale image) -> image"""
        blurred = cv2.GaussianBlur(gray_img, (9, 9), 0, borderType=cv2.BORDER_REPLICATE)
        return cv2.threshold(blurred,
                             constants.THRESHOLD_DIFFERENCE_VALUE, constants.THRESHOLD_COLOR,
                             cv2.THRESH_BINARY_INV)[1]


    # Just a simple function to perform
    # some filtering before any further processing.
    @staticmethod
    def denoise(frame):
        frame = cv2.medianBlur(frame, 5)
        frame = cv2.GaussianBlur(frame, (5, 5), 0)
        return frame

    @staticmethod
    def image_diff_post_processing(img):
        """
        For mask cleaning operation, gray image diff expected;
        Use for background. Should it be used for motion diff
        :return:
        """
        kernel = np.ones((5, 5), np.uint8)
        close_operated_image = cv2.morphologyEx(img, cv2.MORPH_CLOSE, kernel)
        #  Why does it need to be 10 ??
        _, mask = cv2.threshold(close_operated_image, 15, 255, cv2.THRESH_BINARY)
        #  This one is terrible
        #_, mask = cv2.threshold(close_operated_image, 10, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

        #return mask
        return cv2.medianBlur(mask, 5)


    # # unused
    # @staticmethod
    # def convert_BGR2HSV(bgr_color):
    #     color = np.uint8([[bgr_color]])
    #     return cv2.cvtColor(color, cv2.COLOR_BGR2HSV)


        # @staticmethod
        # #http://opencv-python-tutroals.readthedocs.io/en/latest/py_tutorials/py_imgproc/py_morphological_ops/py_morphological_ops.html
        # ## Closing can be done as a Dilation followed by Erosion but is not enough controllable... (kernel is the same size)
        # # Better to do it manually
        # def grow_mask(mask):
        #     # One step = closing  --> grab space between fingers
        #     #return cv2.morphologyEx(mask, cv2.MORPH_CLOSE, Tools.BIG_ROUND_KERNEL)
        #     #  Two steps: dilate and erode (erode makes it worse)
        #
        #     dilated_mask = cv2.dilate(mask, Tools.BIG_ROUND_KERNEL, iterations=2)
        #     # erosion step
        #     #eroded_mask = cv2.erode(dilated_mask, Myframe.BIG_ROUND_KERNEL, iterations=1)
        #     return dilated_mask




#
#
# def extend_mask(self):
#     self.mask = Tools.grow_mask(self.mask)
#     return self.mask

# #should be combined with below
# def __create_mask(self):
#     a_mask = np.zeros((self.height, self.width), np.uint8)
#     a_mask[constants.MASK_BORDER:self.height-constants.MASK_BORDER,
#     constants.MASK_BORDER:self.width-constants.MASK_BORDER] = 255
#     return a_mask
#
# @staticmethod
# def __create_rec_mask(rec):
#     a_mask = np.zeros((rec.height, rec.width), np.uint8)
#     a_mask[rec.y:rec.height, rec.x:rec.width] = 255
#     return a_mask


#img.shape based on image properties  -> num of rows, cols, channels
#http://docs.opencv.org/3.0-beta/doc/py_tutorials/py_core/py_basic_ops/
# py_basic_ops.html#accessing-image-properties
#>>> print img.shape
#(342, 548, 3)


#  Remove detail in an image
# gray = cv2.cvtColor(color_frame, cv2.COLOR_BGR2GRAY)
# gray = cv2.resize(gray, None, fx=0.25, fy=0.25, interpolation=cv2.INTER_AREA)
# gray = cv2.GaussianBlur(gray, (9, 9), 0.0)
