from os import path
import sys

from application import Application
from t_logging import TextLogger
import constants


def setup_from_cmd():
    """
    Gets arguments from command line
    :return: application: implementation of algorithm
    """
    # live demo
    if len(sys.argv) == 1:
        application = Application()
        #  TO CHECK
        print "Using web-cam, device ", constants.OPENED_VIDEO_DEVICE, "needs to be connected"
    # video demo
    elif len(sys.argv) == 2:
        if path.isfile(sys.argv[1]):
            application = Application(sys.argv[1])
            print "Given video", sys.argv[1]
        else:
            print "File not exist"
            sys.exit(0)
    else:
        print "Too Many Arguments"
        sys.exit(0)
    return application

"""
Average use case
"""
app = setup_from_cmd()
count = 0
while app.is_running():
    app.update()

TextLogger.dump_text_by_origin()
