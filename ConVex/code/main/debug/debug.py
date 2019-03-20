import cv2
import numpy as np
class Debug:

    def __init__(self):
        self.stages = {} # dict of stage name :: str to drafting stage :: [img]
        self.ref = 'debug.txt'
        f = open(self.ref,'w') # clear
        f.close()
    def showStage(self, stage_name):
        if stage_name in self.stages:
            cv2.imshow(stage_name,np.hstack(self.stages[stage_name]))
        #else:
        #    self.sprint('Stage Not Found ' + stage_name)

    #def showAllStages(self): # may be unmanagable
    #    return
    def saveSnapshot(self, stage_name, img, i=0): # save to canvas
        if stage_name not in self.stages:
            f = open(self.ref,'a')
            f.write(stage_name+"\n") # save to text doc
            f.close()
            self.stages[stage_name] = [img]
        else:
            if i < len(self.stages[stage_name]):
                self.stages[stage_name][i] = img
            elif i == len(self.stages[stage_name]):
                self.stages[stage_name] += [img]
    
    #def updateSnapshot(self, stage_name, i):
    #    if stage_name in self.stages and i < len(self.stages[stage_name]):
    #        return self.stages[stage_name][i]
    def sprint(self, s):
	    print 'Debug says: ' + s
