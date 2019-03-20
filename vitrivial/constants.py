import imutils

"""
Program constants

    UNDELEGATED: Have not been delegated yet
        CV3: If current version is cv3
        DEFAULT_DEVICE: Video capture device ID eg. 0 for webcam or str for a video file
        FRAMES_USED_PER_SEC: Number of frames used in a second, used to ignore overflow over redundant data
        PROGRAM_QUIT_KEY: Key to be pressed to exit program
        VIDEO_KEY_EVENT_DELAY: Number of milliseconds to wait for keyboard interrupts
        -VIDEO_NUM_OF_FRAMES_SKIPPED: Number of frames to skip before analysing a frame
        -BACKGROUND: Whether OpenCV's background subtraction is used 
        THRESHOLD_DIFFERENCE_VALUE: Epsilon of Approx Polygon 
        THRESHOLD_COLOR: Color to be placed if above a threshold
        CONTOURS_MIN_AREA: Threshold for smallest contour allowed to process
        MASK_BORDER: How much to ignore the peripheral of the mask
        COLOR_[Color]: BGR representation of Color, used for debugging
        PEN_THICKNESS: Default thickness of drawn debugging
        [X]_ROUND_KERNEL: Dimension for sculpting tool, X = size
    SKIN: Constants for finding range of skin color in YCrCb
        MIN_SKIN_COLOR: Low bound on skin color range
        MAX_SKIN_COLOR: High bound on skin color range
"""

#http://www.pyimagesearch.com/2015/08/10/checking-your-opencv-version-using-python/
CV3 = imutils.is_cv3()

DEFAULT_DEVICE = 0
FRAMES_USED_PER_SEC = 3

PROGRAM_QUIT_KEY = 'q'

VIDEO_KEY_EVENT_DELAY = 20
#VIDEO_NUM_OF_FRAMES_SKIPPED = 30  # TO DO: consider smooth output and analyze performance

#BACKGROUND = True


THRESHOLD_DIFFERENCE_VALUE = 10  # 127 mid luminosity (usual)
                      # 10 threshold in difference (special)
THRESHOLD_COLOR = 255  # color white if above mid luminosity

CONTOURS_MIN_AREA = 5000

MASK_BORDER = 15

#BGR
COLOR_BLUE = (255, 0, 0)
COLOR_RED = (0, 0, 255)
COLOR_GREEN = (0, 255, 0)
COLOR_YELLOW = (0, 255, 255)
COLOR_PURPLE = (255, 0, 255)
COLOR_WHITE = (255, 255, 255)

PEN_THICKNESS = 2

#SKIN: Constants for finding range of skin color in YCrCb
# min and max YCrCb
# Elodie hard coded value found:
# https://dsp.stackexchange.com/questions/2565/opencv-detectin-skin-colour-invariant-with-illumination-changes%20#imageYCrCb
# Chai and Ngan Face segmentation using skin colour map 1999
MIN_SKIN_COLOR = [0, 133, 77]
MAX_SKIN_COLOR = [255, 173, 127]

#stupid orange pouf (and colgate shirt) in elodie_in
#MIN_SKIN_COLOR = [0, 143, 77]
#MAX_SKIN_COLOR = [255, 173, 127]


#MIN_SKIN_COLOR = [0, 130, 77]      # for tino (particular pictures, not back_tino.avi)
#MAX_SKIN_COLOR = [255, 173, 132]


SMALL_KERNEL_SIZE = (5, 5)
MID_KERNEL_SIZE = (10, 10)
BIG_KERNEL_SIZE = (25, 25)


# Silhouette has an array of 5 geometries
GEO_POLY = 0
GEO_CONTOUR = 1
GEO_HULL = 2
GEO_TILTED_BBOX = 3  #of the POLY
GEO_BBOX = 4         #of the POLY

GEO_COLORS = [COLOR_BLUE, COLOR_YELLOW, COLOR_RED, COLOR_GREEN, COLOR_PURPLE]
GEO_NAMES = ["handle_init_input", "contour", "hull", "tilted box", "bounding box"]
GEO_DRAW = [True, False, True, False, False]

HAND_NAMES = ["wrist", "thumb", "fingers", "extra"]
HAND_DRAW = [True, False, True, True]

GEO_AREA_RATIO_CLOSE = 15
GEO_AREA_RATIO_PROMPT_MIN = 30
#GEO_AREA_RATIO_PROMPT_MAX = 45   #Elodie
GEO_AREA_RATIO_PROMPT_MAX = 70

#GEO_CENTERS_AREA_PROMPT_GREATER = 400  # used in proportion of Hull area   Elodie
GEO_CENTERS_AREA_PROMPT_GREATER = 4000  # used in proportion of Hull area
GEO_CENTERS_AREA_PROMPT_SMALLER = 100  # used in proportion of Hull area

# see vit_math
NEAR_DIST = 5

# DRAW
TINY_CIRCLE_SIZE = 2
SMALL_CIRCLE_SIZE = 4
BIG_CIRCLE_SIZE = 6

#SKIN   HSV value: Junk
#MIN_SKIN_COLOR = [0, 48, 80]  #  Slider analyze Summer 2016    Works for elodie and chris; not Tino
#MIN_SKIN_COLOR = [0, 48, 0]  #  Not using the Value
#http://answers.opencv.org/question/3300/skin-detection/
#MAX_SKIN_COLOR = [20, 255, 255]  #  Slider analyze Summer 2016
