import cv2
import math
# import sys


def distance(a, b):
    """a -> tuple, b -> tuple, returns distance -> float"""
    x1, y1 = a
    x2, y2 = b
    return math.sqrt(math.pow(x1 - x2, 2) + math.pow(y1 - y2, 2))


class Zone:
    def __init__(self, zone_info, debug_frame):
        self.debug_frame = debug_frame
        self.__init_data(zone_info)
        self.__align_data()
        self.__get_fingers()

    def __init_data(self, zone_info):
        # self.maybeHands = []
        self.rect, self.contour = zone_info
        self.moments = cv2.moments(self.contour)
        self.center_of_gravity = (int(self.moments["m10"] / self.moments["m00"]),
                                  int(self.moments["m01"] / self.moments["m00"]))
        # cv2.circle(frame_copy, (cX, cY), 7, (0, 0, 255), -1)
        # cv2.line(frame_copy,(rect[0],cY),(rect[0]+rect[2],cY),(0,0,255),1)
        # cv2.line(frame_copy,(cX,rect[1]),(cX,rect[1]+rect[3]),(0,0,255),1)
        #   cv2.line(frame_copy,s,e,(0,0,255),3)
        self.hull_points = cv2.convexHull(self.contour, returnPoints=False)
        self.defect_points = cv2.convexityDefects(self.contour, self.hull_points)
        # cv2.drawContours(frame_copy, con, -1, (122,122,0), 3)

    def __align_data(self):
        sum_of_distances = 0
        count_of_distances = 0
        saved_far = ()
        self.triangles = []

        for i in range(self.defect_points.shape[0]):
            start, end, far, depth = Zone.__format_defect_info(self.defect_points[i, 0],
                                                               self.contour)
            sum_of_distances += distance(far, start)
            if i != 0:  # skipping random bug in contour
                self.triangles += [[far, end]]
                if len(self.triangles) > 1:
                    self.triangles[len(self.triangles)-2] += [far]
                else:
                    saved_far = far
                count_of_distances += 1
            # cv2.circle(frame_copy,f,7,[0,0,0],-1)
            # cv2.putText(frame_copy,str(i),f, cv2.FONT_HERSHEY_SIMPLEX, 1,[0,255,0],2,cv2.LINE_AA)
        self.average_of_distances = sum_of_distances / count_of_distances
        if len(self.triangles) > 0:
            self.triangles[len(self.triangles)-1] += [saved_far]

    def __get_fingers(self):
        self.fingers = []
        for triangle in self.triangles:
            side_1, apex, side_2 = triangle
            side_1_distance = distance(side_1, apex)
            side_2_distance = distance(side_2, apex)
            # FIXME: how much of average to be used?
            if side_1_distance >= self.average_of_distances * 0.7 and side_2_distance >= self.average_of_distances:
                self.fingers += [triangle]
        """for i in range(len(fingers)):
            a, b, c = fingers[i]
            cv2.putText(frame_copy,str(i),b, cv2.FONT_HERSHEY_SIMPLEX, 1,[0,255,0],2,cv2.LINE_AA)
            cv2.circle(frame_copy,a,7,[0,255,255],-1)
            cv2.circle(frame_copy,b,7,[0,255,0],-1)
            cv2.line(frame_copy,a,b,(55,0,255),3) # red
            cv2.line(frame_copy,c,b,(255,0,255),3) # pink
        """
        # app.Debug.saveSnapshot('MaybeHands',frame_copy,1)

    def determine_hand(self):
        for finger in self.fingers:
            a, b, c = finger
            d = ((a[0]+c[0])/2, (a[1]+c[1])/2)
            """a_b = distance(a, b)
            a_c = distance(a, c)
            b_c = distance(b, c)"""
            area_of_triangle = distance(a, c) * distance(b, d) * 0.5
            if area_of_triangle > 600:  # testing: make constant above later
                cv2.line(debug_frame, a, c, (255, 0, 55), 3)  # blue
                # d = ((a[0]+c[0])/2, (a[1]+c[1])/2)
                cv2.line(debug_frame, d, b, (55, 0, 55), 3)  # purple
                # cv2.putText(debug_frame,str(i),b, cv2.FONT_HERSHEY_SIMPLEX, 1,[0,255,0],2,cv2.LINE_AA)
            # cv2.line(frame_copy,a,b,(55,0,255),3) # red
            # cv2.line(frame_copy,c,b,(255,0,255),3) # pink

    def is_better_than(self, other_zone):
        """comparsion of hands to one another; preliminary test: how many reasonable fingers?"""
        if len(self.fingers) > 5:
            return False
        if other_zone is None:
            return True
        return len(self.fingers) > len(other_zone.fingers)


    @staticmethod
    def __format_defect_info(defect, contour):
        start, end, far, depth = defect
        return tuple(contour[start][0]), tuple(contour[end][0]), tuple(contour[far][0]), depth


class Hand:
    def __init__(self):
        self.best_hand = None

    def get_hand(self, zones, debug_frame):
        self.__setup_zones(zones, debug_frame)
        self.__find_best_hand()
        return False  # maybe not a bool return value

    def __setup_zones(self, zones_info, debug_frame):
        self.zones = []
        for zone_info in zones_info:
            self.zones += [Zone(zone_info, debug_frame)]

    def __find_best_hand(self):
        for zone in self.zones:
            if zone.is_better_than(self.best_hand):
                self.best_hand = zone
