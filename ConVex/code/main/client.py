from application import Application
import os.path
import sys

''' Think of this as a main
'''
if len(sys.argv) == 1:  # live demo
    app = Application()
elif len(sys.argv) == 2:  # video demo
    if os.path.isfile(sys.argv[1]): 
        app = Application(sys.argv[1])
    else:
        print "File not exist"
        sys.exit(0)
else:
    print "Too Many Arguments"
    sys.exit(0)

while app.is_running():
    gesture_num = app.analyze_for_gestures()
