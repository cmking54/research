import cv2
import constants
import numpy as np
from tools import Tools
from silhouette import Silhouette

class Motion:

    # Background subtraction modes
    NONE = 0
    SIMPLE = 1
    MOG = 2

    BGS_MODE = NONE

    # Todo: experiment and get the value for this
    AREA_THRESHOLD = 0.1

    def __init__(self, h, w, image):
        """
        Creates a motion object
        (int, int, image) --> (Motion)

        Instance variables:
            area: the area of the frame i.e frame width * frame height
            cur_frame: the current frame
            prev_frame: the previous frame
            motion_detector: a motion detector object
            motion_region: a mask of the regions of current frame that moved
            motion_boxes: a list of the largest non-overlapping bounding boxes of motion region
        """

        self.w = w
        self.h = h
        self.area = w * h

        self.cur_frame = image.copy()

        self.motion_detector = self.create_motion_detector()

        self.motion_region = None
        self.motion_boxes = None

    def create_motion_detector(self):
        """
        Creates a returns an instance of either a SimpleMotionDetector or a MOG2 Background
        subtractor
        (none) --> (either SimpleMotionDetector or BackGroundSubtractorMOG2)
        """
        motion_detector = None

        if Motion.BGS_MODE == Motion.NONE:
            motion_detector = SimpleMotionDetector(self.cur_frame, dimensions=(self.w, self.h), set_background=True)

        elif Motion.BGS_MODE == Motion.SIMPLE:
            motion_detector = SimpleMotionDetector(self.cur_frame)

        elif Motion.BGS_MODE == Motion.MOG:
            motion_detector = cv2.createBackgroundSubtractorMOG2(detectShadows=False, varThreshold=100)

        return motion_detector

    def detected(self):
        """
        Returns true if motion was detected in the scene based on the criteria of the motion
        detector in use
        (none) --> (boolean)
        """
        if Motion.BGS_MODE == Motion.NONE:
            return self.motion_detector.detect(self.cur_frame)

        if Motion.BGS_MODE == Motion.SIMPLE:
            return self.motion_detector.detect(self.cur_frame)

        elif Motion.BGS_MODE == Motion.MOG:
            self.motion_region, self.motion_boxes = self.compute_motion_region()

            for box in self.motion_boxes:
                x, y, w, h = box
                area = w * h
                area_ratio = area / self.area

                return area_ratio >= Motion.AREA_THRESHOLD

            return False

    def get_motion_region(self):
        """
        Retries a mask of the regions of the scene that are in motion
        (none) --> (binary image)
        """
        if Motion.BGS_MODE == Motion.NONE:
            motion_region, _ = self.compute_motion_region()
            return motion_region

        elif Motion.BGS_MODE == Motion.SIMPLE:
            motion_region, _ = self.compute_motion_region()
            return motion_region

        elif Motion.BGS_MODE == Motion.MOG:
            return self.motion_region

    def update_frame(self, image):
        """
        Updates the the current frame
        (image) --> (none)
        """
        self.cur_frame = image

    def compute_motion_region(self):
        """
        Computes a mask of the regions of the scene that are in motion. Returns the mask and
        a list of the largest non-overlapping bounding boxes of the motion regions
        (none) --> (binary image, list of boxes)
        """
        motion_region = None
        largest_boxes = None

        if Motion.BGS_MODE == Motion.NONE:
            motion_region = self.motion_detector.get_motion_region(self.cur_frame)
            motion_region = cv2.inRange(motion_region, 20, 255)

            motion_region = Tools.dilate(motion_region, Tools.MID_RECT_KERNEL)
            motion_region, largest_boxes = Motion.cleanup_motion_region(motion_region)

        elif Motion.BGS_MODE == Motion.SIMPLE:

            motion_region = self.motion_detector.get_motion_region(self.cur_frame)
            motion_region = cv2.inRange(motion_region, 20, 255)

            # to get less of the face
            # motion_region = cv2.inRange(motion_region, 25, 255)
            motion_region = Tools.dilate(motion_region, Tools.MID_RECT_KERNEL)

            motion_region, largest_boxes = Motion.cleanup_motion_region(motion_region)

        elif Motion.BGS_MODE == Motion.MOG:

            motion_region = self.motion_detector.apply(self.cur_frame, learningRate=1./200)
            motion_region = Tools.dilate(motion_region, Tools.MID_RECT_KERNEL)

            motion_region, largest_boxes = Motion.cleanup_motion_region(motion_region)

        return motion_region, largest_boxes

    @staticmethod
    def cleanup_motion_region(motion_region):
        """
        Performs a series of drawings and image processing to a mask of the motion regions to
        minimize noise. Returns the cleaner mask and a list of the largest non-overlapping bounding
        boxes of the mask.
        (binary image) --> (binary image, list of boxes)
        """
        image = cv2.cvtColor(motion_region, cv2.COLOR_GRAY2BGR)

        motion_contours = Motion.get_all_contours(image)
        motion_region = Motion.draw_all_bounding_boxes(image, motion_contours, filled=True)

        bbox_contours = Motion.get_all_contours(motion_region)
        motion_region = Motion.draw_all_bounding_boxes(image, bbox_contours, filled=True)

        # final touches
        motion_region = Tools.erode(motion_region, Tools.BIG_RECT_KERNEL)
        motion_region = Tools.dilate(motion_region, Tools.BIG_RECT_KERNEL)

        # get largest box here
        largest_boxes = []
        bbox_contours = Motion.get_all_contours(motion_region)
        for box in bbox_contours:
            largest_boxes += [cv2.boundingRect(box)]

        motion_region = cv2.cvtColor(motion_region, cv2.COLOR_BGR2GRAY)

        return motion_region, largest_boxes

    @staticmethod
    def get_all_contours(mask):
        """
        Computes the contours of a mask and return a list of those contours whose area >=
        a predefined threshold
        (binary image) --> (list of contours)
        """
        img_gray = cv2.cvtColor(mask, cv2.COLOR_BGR2GRAY)

        contours = Silhouette.cv_find_contours(img_gray)
        large_contours = []

        for c in contours:
            area = cv2.contourArea(c)

            if area < constants.CONTOURS_MIN_AREA:
                continue
            large_contours += [c]

        return large_contours

    @staticmethod
    def draw_all_bounding_boxes(image, contours, filled=False):
        """
        Draws a bounding box on the input image for each contour. Returns the modified mask
        (binary image, list of contours, boolean) --> (binary image)
        """
        if filled:
            pen_thickness = -1
        else:
            pen_thickness = constants.PEN_THICKNESS

        for c in contours:
            box = cv2.boundingRect(c)
            x, y, w, h = box
            cv2.rectangle(image, (x, y), (x+w, y+h), constants.COLOR_WHITE, pen_thickness)

        return image


class SimpleMotionDetector:

    PIXEL_DIFF_THRESHOLD = 100000
    INITIAL_DIFF_THRESHOLD = 20000

    def __init__(self, initial_frame, dimensions=(640, 480), set_background=False):
        self.motion_region = None

        self.compare_with_background = set_background
        self.prev_frame = Tools.gray_image(initial_frame)

        w = int(dimensions[0])
        h = int(dimensions[1])
        self.white_mask = np.ones((h, w, 1), dtype=np.uint8)*255

    def detect(self, cur_frame):
        """
        Returns true if the pixel difference between current frame and previous frame >=
        a predefined threshold
        (image) --> (boolean)
        """
        self.motion_region = self.get_frame_diff(cur_frame)
        pixel_difference = cv2.countNonZero(self.motion_region)
        #print "....... pixel difference", pixel_difference

        if self.compare_with_background:
            if pixel_difference >= SimpleMotionDetector.INITIAL_DIFF_THRESHOLD:
                self.compare_with_background = False
            self.motion_region = self.white_mask
            return True

        return pixel_difference > SimpleMotionDetector.PIXEL_DIFF_THRESHOLD

    def get_motion_region(self, cur_frame):
        """
        Returns the motion region i.e regions of current frame that are no the same as those
        in previous frame
        (image) --> (image)
        """

        """"
        Note: detect() is always called before get_motion_region() so method should
        return the motion_region that was calculated by detect
        """
        if self.motion_region is not None:
            return self.motion_region
        else:
            return self.get_frame_diff(cur_frame)

    #  should it use the Tool difference_images and do conversion only once?
    def get_frame_diff(self, cur_image):
        """
        Computes and return regions of motion i.e regions of current frame that are not the same
        as those in previous frame
        (image) --> (image)
        """
        cur_image = Tools.gray_image(cur_image)
        difference = Tools.difference_image(cur_image, self.prev_frame)
        self.prev_frame = cur_image

        return difference





