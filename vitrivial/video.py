import cv2

from skin import Skin
from motion import Motion
from hand import Hand
from tools import Tools
from silhouette import Silhouette
from algo_class import AlgoClass

import constants


class Video(AlgoClass):
    """
    Reads frames from a video source and broadcast them to motion and skin

    Instance Variables:
        web_cam: bool - True when web camera is the source and is still on
                        False when video file is the source
        capture:       VideoCapture object - use to read frames
        has_frame:     bool - a frame exists       (necessary?)
        current_frame: image  - current video frame
        count_frame:   int  - total number of frames read from video source

    """

    def __init__(self, source):
        """
        Create a video instance from the given source
        :param source: either Device ID or video file name
        """
        AlgoClass.__init__(self)

        self.web_cam, self.capture = self.set_capture(source)
        self.TOTAL_FRAMES, self.NUM_FRAMES_SKIPPED = self.set_read()

        # all should be called img
        self.before_process = None

        # updated by read(), make sure a frame exists
        self.has_frame, self.current_frame = False, None
        self.read()
        #  use to skip frame
        self.count_frame = 1

        self.motion, self.motion_region = self.set_motion_tracker(), None
        self.skin, self.skin_regions = Skin(), None

        self.masked_frame = None
        self.hand_img = None

        self.hand = None

    def update(self):
        """
        Video control center. If there is a new non-skipped frame with
        sufficient changes based on main areas of concern
             - on motion (including background sub) and
             - skin color
        the existing hand is process for gesture recognition
        :return: bool
        """
        # TODO: rank among multiple hands
        if self.has_more_frames() and self.is_retrieved() and self.motion.detected():

            print "frame", self.count_frame

            self.masked_frame = self.create_masked_frame()
            hand_silhouette = self.find_hand_silhouette()
            if hand_silhouette is not None:
                self.process_hand(hand_silhouette)
                return True

            return False

    def create_masked_frame(self):
        """
        Create and return a masked version of the current frame
        The mask rejects non-skin colors and static parts by filtering for skin
        and motion regions
        :return: image
        """
        self.motion_region = self.motion.get_motion_region()
        self.skin_regions = self.skin.get_active_regions(self.current_frame)

        # main area of concern
        return cv2.bitwise_and(self.skin_regions, self.skin_regions,
                               mask=self.motion_region)

    def find_hand_silhouette(self, frame=None):
        """
        Return Silhouette of the hand by processing the geometries of all the contours
        :param frame: image
        :return: Silhouette
        """
        if frame is None:
            frame = self.masked_frame

        contours = Silhouette.get_contours(frame, constants.CONTOURS_MIN_AREA)
        # onion geometries for all large contours (likely face and hand)
        silhouettes = Silhouette.create_geometries(frame, contours)

        if len(silhouettes) > 0:
            #for idx in range(len(sils)):
            #sils[idx].draw_all()

            return Silhouette.select_hand_like(silhouettes)

        return None

    def process_hand(self, hand_silhouette):
        """
        Process the hand silhouette to identify the thumb and fingers
        :param hand_silhouette: Silhouette
        :return:
        """
        hand_silhouette.log_all()
        self.hand = Hand(self.current_frame, hand_silhouette.onion_geometry,
                         hand_silhouette.shape_like)

        #  drawn after the Hand constructor call to track the refined poly_curve
        hand_silhouette.draw_all()
        self.hand.draw(self.current_frame)

    def read(self):
        """
        Update current frame with next read and some initial image processing
        :return: None
        """
        self.has_frame, self.current_frame = self.capture.read()
        self.before_process = self.current_frame.copy()
        self.current_frame = Tools.pre_process_image(self.current_frame)

    def is_running(self):
        """
        Return True if video source has more frames and user has not issued a quit command
        :return: bool
        """

        if self.has_more_frames() and not self.video_key_interrupt():
            return True
        else:
            self.capture.release()
            cv2.destroyAllWindows()
            return False

    def is_retrieved(self):
        """
        One frame out of NUM_FRAMES_SKIPPED is to be read
        For example out with FPS 30 and 3 FRAMES_USED_PER_SEC
                1 is read, meaning grabbed and retrieved (latter is a slow op)
                9 are skipped, VideoCapture.grab() applied to advance video
        :return: bool
        """
        self.count_frame += 1
        if (self.count_frame % self.NUM_FRAMES_SKIPPED) == 0:
            self.read()
            self.motion.update_frame(self.current_frame)
            return True
        else:
            self.has_frame = self.capture.grab()
            return False

    def has_more_frames(self):
        """
        Return True if the video source has more frames
        :return: bool
        """
        return self.web_cam or self.count_frame < self.TOTAL_FRAMES

    #
    #  constructor helpers

    def set_capture(self, source):
        """
        :param source: int/str ( live camera index/video file name)
        :return: VideoCapture
        """
        web_cam = False

        if source == constants.DEFAULT_DEVICE:
            self.log_text("Webcam " + source + " in use")
            web_cam = True

        capture = cv2.VideoCapture(source)

        if not capture.isOpened():
            self.log_text("Failed to open video source. Exiting...")
            exit()

        self.log_text(source)
        return web_cam, capture

    def set_read(self):
        """
        Set video statistics
        Return total number of frames in video source and
               frames to skip in between two reads
        :return: int, int
        """
        total_frames = self.capture.get(cv2.CAP_PROP_FRAME_COUNT)
        num_frames_skipped = int(self.capture.get(cv2.CAP_PROP_FPS)
                                      / constants.FRAMES_USED_PER_SEC)
        self.log_text("total frames %d" % total_frames)
        self.log_text("used frames %d" % constants.FRAMES_USED_PER_SEC)
        self.log_text("skip %d" % num_frames_skipped)
        return total_frames, num_frames_skipped

    def set_motion_tracker(self):
        """
        :return: Motion object
        """
        width, height = self.get_frame_size()
        return Motion(height, width, self.current_frame)

    def get_frame_size(self):
        """
        :return: int, int
        """
        return self.capture.get(cv2.CAP_PROP_FRAME_WIDTH), \
               self.capture.get(cv2.CAP_PROP_FRAME_HEIGHT)

    @staticmethod
    def video_key_interrupt():
        """
        Delay for keyboard interrupt callbacks.
        Return True if the predefined quit key was pressed
        :return: bool
        """
        """
        Note:
        & 0xff needed for 64-bit machine: see following link
        http://docs.opencv.org/3.0-beta/doc/py_tutorials/py_gui/py_image_display/
           ...py_image_display.html
        """
        k = cv2.waitKey(constants.VIDEO_KEY_EVENT_DELAY) & 0xff
        return k == ord(constants.PROGRAM_QUIT_KEY.lower())






