import cv2
import numpy as np


class MotionDetector(object):
    def __init__(self, history_count=1, learning_rate=0.05):
        self.frame_count = 0
        self.init_history_count = history_count
        self.history_done = False
        self.learning_rate = learning_rate

    def is_history_done(self):
        return self.history_done

    def apply(self, frame):
        self.__prepare_frame(frame)
        self.__prepare_base()
        return self.__apply_to_base()

    def __prepare_frame(self, frame):
        frame_copy = frame.copy()
        gray_frame = cv2.cvtColor(frame_copy, cv2.COLOR_BGR2GRAY)
        blurred_frame = cv2.GaussianBlur(gray_frame, (11, 11), 0)  # heavy blur
        self.prepped_frame = blurred_frame

    def __prepare_base(self):
        try:
            self.base
        except AttributeError:
            self.base = np.float32(self.prepped_frame.copy())  # is copy needed?

    def __apply_to_base(self):
        cv2.accumulateWeighted(self.prepped_frame, self.base, self.learning_rate)
        motion_mask = np.uint8(cv2.absdiff(self.base, np.float32(self.prepped_frame)))
        return motion_mask

    def fill_history(self, frame):
        self.__prepare_frame(frame)
        self.__prepare_base()
        if self.frame_count < self.init_history_count:
            cv2.accumulateWeighted(self.prepped_frame, self.base, 0.5)
            self.frame_count += 1
        else:
            self.history_done = True
