import cv2
import imutils
from errors import AppError
from logger import Logger


class Video:
    current_frame = None

    def __init__(self, source, motion_detector):
        self.logger = Logger('Vid_logger', './video/')
        self.video_source = cv2.VideoCapture(source)
        self.current_frame = \
            self.last_processed_frame = None
        self.MIN_FRAME_DIFF = 140000
        self.num_of_frames = 0
        self.TOTAL_FRAMES = self.video_source.get(cv2.CAP_PROP_FRAME_COUNT)
        self.USABLE_FRAMES_PER_SECOND = 3
        self.NUM_FRAMES_SKIPPED = int(self.video_source.get(cv2.CAP_PROP_FPS)
                                      / self.USABLE_FRAMES_PER_SECOND)
        self.__setup(motion_detector)

    def is_running(self, time_delay_between_frames=1, quit_key='q'):
        if self.num_of_frames < self.TOTAL_FRAMES and cv2.waitKey(time_delay_between_frames) & 0xff != ord(quit_key.lower()):
            # print self.num_of_frames
            # and cv2.waitKey(time_delay_between_frames) & 0xff != ord(quit_key.lower()):
            return True
        else:
            exit()
            return False

    @staticmethod
    def exit():
        cv2.destroyAllWindows()

    def get_frame(self):
        return self.current_frame.copy()

    def __setup(self, motion_detector):
        """Preps Camera and Motion Detector"""
        while not motion_detector.is_history_done():
            self.__grab_image()
            self.__read_image()
            self.__fill_hist(motion_detector)
        self.last_processed_frame = self.current_frame

    def __grab_image(self):
        """Advances Video Source"""
        found = self.video_source.grab()
        self.num_of_frames += 1
        if not found:
            raise AppError('Ran Out Of Frames')  # FIXME: fix error style

    def __read_image(self):
        """Retrieves a image for current source"""
        found, frame = self.video_source.retrieve()
        if not found:
            raise AppError('Video Source not found')  # FIXME: fix error style
        self.current_frame = imutils.resize(frame, width=600)  # TODO: log me

    def __fill_hist(self, motion_detector):  # is this in the right scope?
        # TODO: have motion handle color
        motion_detector.fill_history(self.get_frame()) # cv2.cvtColor(Video.current_frame, cv2.COLOR_BGR2HSV))

    def has_frame_changed(self):
        for _ in range(self.NUM_FRAMES_SKIPPED):
            self.__grab_image()
        self.__read_image()
        if self.__change_occurred():
            self.logger.log('Used frames', self.current_frame)
            self.last_processed_frame = self.current_frame
            return True
        else:
            return False

    def __change_occurred(self):
        # some blurring/cleaning needed
        frame_difference = cv2.absdiff(cv2.cvtColor(self.current_frame, cv2.COLOR_BGR2GRAY),
                                       cv2.cvtColor(self.last_processed_frame.copy(), cv2.COLOR_BGR2GRAY))
        return cv2.countNonZero(frame_difference) >= self.MIN_FRAME_DIFF
