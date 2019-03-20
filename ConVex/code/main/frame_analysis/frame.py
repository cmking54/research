import cv2
import numpy as np
from logger import Logger

''' @author CK
'''


def rects_collide(rect_a, rect_b):
    rect_a_x, rect_a_y, rect_a_width, rect_a_height = rect_a
    rect_b_x, rect_b_y, rect_b_width, rect_b_height = rect_b
    return rect_a_x <= rect_b_x + rect_b_width and \
           rect_b_x <= rect_a_x + rect_a_width and \
           rect_a_y <= rect_b_y + rect_b_height and \
           rect_b_y <= rect_a_y + rect_a_height


class Frame:
    """ The class responsible for detecting regions where
        a hand may be.

        Attributes:
            LOW_BOUND_SKIN_COLOR, HIGH_BOUND_SKIN_COLOR: Bounds on (experimental) skin color range.
            ROUND_KERNEL_[n]: a circular tool with radius n for image
                modification.
            MIN_MOTION_AREA: threshold of area at which a contour can be considered
                for computation
            DIFF_DIST: a heuristic of latency in the BGS

            motion_zones: metadata of regions of relevant motion
            color_zones: metadata of regions of relevant color
            final_zones: metadata of relevant regions
    """

    def __init__(self):
        self.color_zones = \
            self.motion_zones = \
            self.final_zones = None
        self.logger = Logger('Frame_logger', './frame_analysis')
        # PUT CONSTANTS HERE FOR NOW
        self.MIN_SKIN_COLOR = np.array([0, 48, 80], dtype="uint8")  # LOW_BOUND -> MIN
        self.MAX_SKIN_COLOR = np.array([20, 255, 255], dtype="uint8")
        self.ROUND_KERNEL_5 = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        self.ROUND_KERNEL_15 = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (15, 15))
        self.MIN_MOTION_AREA = 3000  # try to eliminate
        self.MIN_COLOR_AREA = 200  # try to eliminate
        self.DIFF_DIST = 35

    def __get_clean_motion_frame(self, motion_detector, debug_frame):
        motion_mask = motion_detector.apply(debug_frame.copy())
        _, threshold_mask = cv2.threshold(motion_mask, self.DIFF_DIST, 255, cv2.THRESH_BINARY)
        constricted_mask = cv2.dilate(threshold_mask, self.ROUND_KERNEL_5, iterations=5)
        opened_mask = cv2.morphologyEx(constricted_mask, cv2.MORPH_OPEN, self.ROUND_KERNEL_15)
        final_cleaned_frame = opened_mask
        return final_cleaned_frame

    @staticmethod
    def __get_area_threshold_zones(mod_frame, debug_frame, bounding_function):
        temp_zones = []
        _, contours, _ = cv2.findContours(mod_frame, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        for contour in contours:
            area = cv2.contourArea(contour)
            if bounding_function(area):
                rect = cv2.boundingRect(contour)
                temp_zones += [(rect, contour)]
                # debugging -> necessary side effect
                cv2.rectangle(debug_frame, (rect[0], rect[1]),
                              (rect[0] + rect[2], rect[1] + rect[3]),
                              255, 2)
        return temp_zones

    def __get_motion_zones(self, motion_detector, debug_frame):
        """Uses BGS to find motion and removes not necessary info"""
        modified_frame = self.__get_clean_motion_frame(motion_detector, debug_frame)
        self.motion_zones = Frame.__get_area_threshold_zones(modified_frame,
                                                             debug_frame,
                                                             lambda area:
                                                             area >= self.MIN_MOTION_AREA)
        self.logger.log('Motion Bounding', debug_frame)

    def __get_clean_color_frame(self, debug_frame):
        frame_copy = cv2.cvtColor(debug_frame.copy(), cv2.COLOR_BGR2HSV)
        threshold_mask = cv2.inRange(frame_copy, self.MIN_SKIN_COLOR, self.MAX_SKIN_COLOR)
        opened_mask = cv2.morphologyEx(threshold_mask, cv2.MORPH_OPEN, self.ROUND_KERNEL_5)
        dilated_mask = cv2.dilate(opened_mask, self.ROUND_KERNEL_5, iterations=2)
        final_cleaned_frame = dilated_mask
        return final_cleaned_frame

    def __get_color_zones(self, debug_frame):
        """Processes the frame for skin color, then find bounding regions"""
        modified_frame = self.__get_clean_color_frame(debug_frame)
        self.color_zones = Frame.__get_area_threshold_zones(modified_frame,
                                                            debug_frame,
                                                            lambda area:
                                                            area >= self.MIN_COLOR_AREA)
        self.logger.log('Color Bounding', debug_frame)

    def __find_motion_color_overlap(self, debug_frame):
        """Returns overlap in the motion_zones and the color_zones"""
        frame_copy = debug_frame.copy()
        self.final_zones = []
        for color_zone in self.color_zones:
            color_rect, color_contour = color_zone
            for motion_zone in self.motion_zones:
                motion_rect, motion_contour = motion_zone
                if rects_collide(color_rect, motion_rect):
                    del motion_zone
                    self.final_zones += [color_zone]
                    cv2.drawContours(frame_copy, color_contour, -1, (122, 122, 0), 3)
                    cv2.rectangle(frame_copy,
                                  (color_rect[0], color_rect[1]),
                                  (color_rect[0] + color_rect[2], color_rect[1] + color_rect[3]),
                                  (0, 255, 0), 2)
        self.logger.log('Color + Motion', frame_copy)
        return self.final_zones

    def get_crucial_zones_of_frame(self, motion_detector, debug_frame):
        """Returns relevant regions on frame"""
        self.__get_motion_zones(motion_detector, debug_frame.copy())
        self.__get_color_zones(debug_frame.copy())
        return self.__find_motion_color_overlap(debug_frame.copy())
