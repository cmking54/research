from video import Video
from silhouette import Silhouette
from vlogging import VisualRecord
import logging
import constants


class Application:
    """
    Manages the running of the application

    Instance variables
        capture: Video object to read and process images from video source
        logger: VisualRecord object used for visual debugging
        fh: A file handler for the visual logger / debugger
    """

    def __init__(self, source=constants.DEFAULT_DEVICE):
        """
        Constructor, sets up video and logging
        :param source: variable representing the video source
        int -> live camera; str -> video file
        """

        self.capture = Video(source)

        if source != constants.DEFAULT_DEVICE:
            log_filename = source.split("/")[1]
        else:
            log_filename = "live_video"

        self.logger = self.init_log(log_filename)

    @staticmethod
    def init_log(filename):
        logger = logging.getLogger("visual_logging_example")
        fh = logging.FileHandler("logs/" + filename + ".html", mode="w")

        logger.setLevel(logging.DEBUG)
        logger.addHandler(fh)

        return logger

    def is_running(self):
        """
        Client-side to whether there are more frames to process
        :return: if video is still retrieving frames
        """
        return self.capture.is_running()

    def update(self):
        """
        Client-side to advance processing, is logged accordingly
        :return: void
        """
        if self.capture.update():
            self.log_all()

    def log_all(self):
        self.write_log("Initial", self.capture.before_process)
        self.write_log("Pre Process", self.capture.current_frame)
        #self.write_log("Difference", self.capture.motion.img_diff)
        ##self.write_log("Gray", self.capture.motion.current_gray_frame)
        #self.write_log("Background mask", self.capture.background_mask)

        #"""Motion logs"""
        #self.write_log("Motion Mask", self.capture.motion.motion_region)
        self.write_log("All Geometries", Silhouette.log_all_geometries)
        # self.write_log("Motion Contour Approximations", Silhouette.log_all_approx)
        #self.write_log("Motion Boxes", self.capture.motion.motion_boxes)

        #"""Skin logs"""
        # self.write_log("YCrCb Image", self.capture.skin.ycrcb_frame)
        # self.write_log("Skin Mask", self.capture.skin.skin_mask)
        # self.write_log("Skin Region", self.capture.skin.skin_region)
        # self.write_log("Skin n Motion Region", self.capture.skin.skin_motion_region)

        # self.write_log("All Contours", Silhouette.log_all_approx)
        # self.write_log("All Contour Approximations", Silhouette.log_all_approx)
        # self.write_log("All Bounding Boxes", Silhouette.log_all_bboxes)

        # self.write_log("Skin contours", self.capture.skin_frame)
        # self.write_log("Hand image", self.capture.hand_img)

    def write_log(self, title, image):
        self.logger.debug(VisualRecord(
            (title + " = %d" % self.capture.count_frame), image, fmt="png"))




