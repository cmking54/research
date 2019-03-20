from motion import MotionDetector
from video import Video
from frame_analysis import Frame
from hand_processing import Hand


class Application:
    def __init__(self, source=0):
        self.motion_detector = MotionDetector()
        self.video = Video(source, self.motion_detector)
        self.frame = Frame()
        self.hand = Hand()

    def is_running(self):
        return self.video.is_running()

    def analyze_for_gestures(self):
        if self.video.has_frame_changed():
            zones = self.frame.get_crucial_zones_of_frame(self.motion_detector, self.video.get_frame())
            if len(zones) > 0:
                # is_hand = self.hand.get_hand(zones)
                return -1  # return self.gesture.match(self.hand) if is_hand else -1
            else:
                return -1  # error may be needed?
        return -1
