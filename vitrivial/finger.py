import cv2
import constants
from algo_class import AlgoClass
#from vit_math import Point
from vit_math import Curve

class Finger(AlgoClass):
    """
        a list of 3 Point objects [defect1, tip, defect2]
        For thumb defect1 is closest to wrist
        For grasping fingers defect1 is closest to thumb
    """

    PTS_LEN = 3

    WRIST = 0
    THUMB = 1
    INDEX = 2
    MAJOR = 3
    RING = 4
    PINKY = 5

    NAMES = ["T", "I", "M", "R", "P"]

    def __init__(self, d1, tip, d2, num):
        self.digit = num

        self.palm_pt1 = d1
        self.tip = tip
        self.palm_pt2 = d2

    def draw(self, image, color):
        Curve.draw_line(image, color, self.palm_pt1, self.tip)
        Curve.draw_line(image, color, self.palm_pt2, self.tip)
        #pass

    #

    @staticmethod
    def get_defect_pts(fingers):
        all_defects = []
        for idx in range(Finger.THUMB, len(fingers)):
            first, second = fingers[idx].palm_pt1, fingers[idx].palm_pt2,
            if first not in all_defects:
                all_defects += [first]
            if second not in all_defects:
                all_defects += [second]

        return Curve(all_defects)

    @staticmethod
    def get_finger_tips(fingers):
        all_tips = []
        for idx in range(Finger.THUMB, len(fingers)):
            all_tips += [fingers[idx].tip]

        return Curve(all_tips)

    @staticmethod
    def draw_all(image, fingers):
        start = 0
        if constants.HAND_DRAW[Finger.WRIST]:
            start = 1

        for idx in xrange(start, len(fingers)):
            fingers[idx].draw(image, constants.COLOR_BLUE)


    @staticmethod
    def create_fingers(ref):


        #ref = self.onion_geometry[constants.GEO_POLY].poly_curve
        idx = 0
        fingers = [Finger(ref[idx], ref[idx+1], ref[idx+2], Finger.WRIST)]

        for idx in xrange(Finger.PTS_LEN, len(ref)-2, Finger.PTS_LEN-1):
            fingers.append(Finger(ref[idx], ref[idx+1], ref[idx+2], idx % Finger.PTS_LEN))

        return fingers


