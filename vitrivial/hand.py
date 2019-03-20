import constants
from geometry import Geometry
from algo_class import AlgoClass
from vit_math import Point
from vit_math import Curve
from vit_math import Vector
from finger import Finger


class Hand(AlgoClass):
    """
    The wrist and its middle point is the axis of reference from
    which the range of motion of the finger tips is analyzed and hence
    the fingers tracked

     list of 6 fingers: each define by 3 points [end_defect1, tip_middle, end_defect2]
     - 5 normal finger: each of which is standing or not
     - 1 the wrist (finger): at index 0

     Chivalry of hand helps make equivalence
    """

    WRIST_DELTA_Y = -1
    PREVIOUS_PROMPT = None
    TABLE = ''

    PROMPT = 0  # open
    FIST = 1    # close
    OTHER = 2   # partial

    def __init__(self, img, g, shape):
        #  local import due to circular dependencies
        from silhouette import Silhouette

        self.image = img
        self.onion_geometry = g

        #TODO
        # work on OPENED, CLOSED, partial to correct finger!
        # refine Thumb, Wrist make them work together, no duplicate code
        #   Robust Algo
        self.shape = shape
        #print self.onion_geometry[constants.GEO_BBOX].__str__()
        if Hand.PREVIOUS_PROMPT is None:
            print "First prompt"
            Hand.set_wrist_delta_y(self.onion_geometry[constants.GEO_BBOX])

        self.thumb_left, self.thumb_point = Hand.find_thumb(self.onion_geometry)
        self.wrist_pt1, self.wrist_pt2 = self.find_wrist(self.onion_geometry[constants.GEO_HULL])

        #  produce two Curve objects. GEO_POLY not enough points?
        self.in_defects, self.out_defects = \
            Silhouette.get_defect_pts(self.onion_geometry[constants.GEO_CONTOUR], self.shape) #.curve)

#       self.in_defects.draw_points(self.image, constants.COLOR_GREEN, size=constants.BIG_CIRCLE_SIZE)

        # make our main CURVE object for the fingers, self.in_defects is CHANGED to have
        # near points of the curve be exactly the same
        # TODO: add points in ref if two in_defects in a row
        self.onion_geometry[constants.GEO_POLY].create_poly_curve(self.in_defects, self.wrist_pt1,
                                                                  self.wrist_pt2, self.thumb_point)

        #print "first", self.onion_geometry[constants.GEO_POLY].poly_curve
        # reorientation of POLY and self.in_defects
        #self.onion_geometry[constants.GEO_POLY].poly_curve = self.align_points_wrt_wrist()
        #print "second", self.onion_geometry[constants.GEO_POLY].poly_curve

        self.remove_extra_points()
        self.fingers = Finger.create_fingers(self.onion_geometry[constants.GEO_POLY].poly_curve)

        self.print_angles_report()
        #
        #


    def draw(self, image):

        def draw_thumb(poly):
            line = Curve([poly.center, self.thumb_point])
            line.draw(image, constants.COLOR_GREEN, close=False, circle=True)

        def draw_extra(our_poly):
            self.in_defects.draw_points(image, constants.COLOR_PURPLE,
                                        size=constants.SMALL_CIRCLE_SIZE, label=True)
                                        #size=constants.SMALL_CIRCLE_SIZE)

            #self.out_defects.draw_points(image, constants.COLOR_YELLOW,
            #                             size=constants.TINY_CIRCLE_SIZE)
            #our_poly.draw_points(image, constants.COLOR_WHITE, label=True)
            our_poly.draw_points(image, constants.COLOR_WHITE, label=True, offset=-20)
            #our_poly.draw_points(image, constants.COLOR_WHITE)

        if constants.HAND_DRAW[Finger.MAJOR]:
            draw_extra(self.onion_geometry[constants.GEO_POLY].poly_curve)

        if constants.HAND_DRAW[Finger.WRIST] and self.fingers is not None:
            self.fingers[Finger.WRIST].draw(image, constants.COLOR_YELLOW)

        if constants.HAND_DRAW[Finger.THUMB]:
            draw_thumb(self.onion_geometry[constants.GEO_POLY])

        if constants.HAND_DRAW[Finger.INDEX] and self.fingers is not None:
            Finger.draw_all(image, self.fingers)



    # TODO: if two defects in row add a midpoint
    def remove_extra_points(self):
        """
        :return:
        """

        def in_between(def1, def2):
            if def2 - def1 == 2:
                return def1 + 1

            # to widen the range -> most exterior point wanted
            # due to orientation, seems to be the first one for thumb, index, major
            elif digit_num < Finger.MAJOR:
                return def1 + 1
            else:
                return def2 - 1

#defect here!

        ref = self.onion_geometry[constants.GEO_POLY].poly_curve

        defects_copy = Curve(self.in_defects)
        print "curve\n", ref

        if len(ref) >= Finger.PTS_LEN:
            # copy the wrist known to be three points
            new_curve = Curve(ref[:Finger.PTS_LEN])
            #print "defects\n", defects, "\nnew_curve\n", new_curve
            idx = Finger.PTS_LEN
            #print "next points", defects_copy
            first_idx = ref.index(defects_copy[0])
            defects_copy.remove(0)
            new_curve.append([ref[first_idx]])
            digit_num = Finger.THUMB
            while first_idx != -1 and len(defects_copy) > 0:
                print "next points", defects_copy
                next_idx = ref.index(defects_copy[0])
                print "pattern index", first_idx, next_idx
                if next_idx != -1:
                    tip = in_between(first_idx, next_idx)
                    print "pattern points ", ref[first_idx+1], ref[next_idx]
                    new_curve.append([ref[tip], ref[next_idx]]) #insert tip and second defect
                    defects_copy.remove(0)
                    digit_num += 1
                first_idx = next_idx
            self.onion_geometry[constants.GEO_POLY].poly_curve = new_curve



    # def align_points_wrt_wrist(self):
    #     """
    #     Align the poly with respect to wrist and add a midpoint if necessary
    #     Align similarly the defect points, so the two curves are inline
    #     post: poly_curve starts at farther wrist point from thumb,
    #        then thumb, index, major, ring and pinky points
    #     :return:
    #     """
    #     ref = self.onion_geometry[constants.GEO_POLY].poly_curve
    #
    #     # find in our poly Curve the indices of the wrist
    #     # known index should not return -1
    #     poly_index1 = ref.index(self.wrist_pt1)
    #     poly_index2 = ref.index(self.wrist_pt2)
    #     opposite_to_thumb = self.thumb_point.is_first_farther(ref[poly_index1], ref[poly_index2])
    #     #print "opposite", opposite_to_thumb
    #
    #     direction = 1
    #     if opposite_to_thumb:
    #         # going CW towards thumb
    #         direction = -1
    #         ref.orient(poly_index1, direction=direction)
    #     else:
    #         ref.orient(poly_index2, direction=direction)
    #
    #     # wrist: second point is end of the wrist, supplement it to be three points
    #     if ref[1] == self.wrist_pt1 or ref[1] == self.wrist_pt2:
    #         ref.add_midpoint(1)
    #
    #     # in_defects work: align it with curve first defect--beyond WRIST (zero finger)
    #     if len(ref) > Finger.PTS_LEN:
    #         _, first_defect = ref.index_first_in_common(self.in_defects, Finger.PTS_LEN)
    #         if first_defect != -1:
    #             # same orientation than poly WORKS
    #             self.in_defects.orient(first_defect, direction=direction)
    #         # else:
    #         #     print "trouble"
    #
    #     return ref

    def find_wrist(self, hull_geo):
        """
        Given as geo the convex_hull, in relation to its center
                         -----------
        there are more points above center (open palm...) than below
        1. Find the start and end indices defining the wrist,
           which is an almost horizontal line (deltaY < 5, deltaX > 50)
           + correct for being the longest line (if three points)

           one point... correction not fool proof
        :param self:
        :param hull_geo:
        :return: Point, Point   (NONE if not found)
        """

        #curve_pts = Curve.convert_np_array2curve(hull_geo.curve)
        curve_pts = Curve(hull_geo.curve)
        wrist_hull_index1, wrist_hull_index2 = Curve.indices_of_lowest_horizontal(
            curve_pts, hull_geo.center, Hand.WRIST_DELTA_Y)

        # does this work? CK
        if Hand.PREVIOUS_PROMPT is None and wrist_hull_index1 != -1:
            Hand.PREVIOUS_PROMPT = self

        return curve_pts[wrist_hull_index1], curve_pts[wrist_hull_index2]

    @staticmethod
    def set_wrist_delta_y(bbox):
        """
        """
        #  20% height of the bbox... should be set by PROMPT and not retouch
        if Hand.WRIST_DELTA_Y == -1:
            Hand.WRIST_DELTA_Y = bbox.get_height() / 20.0
            #print "delta Y", Hand.WRIST_DELTA_Y

    #Chris' style
    @staticmethod
    def find_thumb(geo):
        """
        Return if the thumb is on the left and its Point coordinates
        :return: bool, Point
        """
        def is_thumb_to_the_left():
            diff = geo[constants.GEO_BBOX].center.x - geo[constants.GEO_HULL].center.x
            #  center of mass (hull) to the left of the bbox center -> thumb to the right
            return diff <= 0

        extremes = Geometry.find_extremes(geo[constants.GEO_HULL].curve)
        thumb_left = is_thumb_to_the_left()
        if thumb_left:
            return thumb_left, extremes[Geometry.EX_LEFT]
        else:
            return thumb_left, extremes[Geometry.EX_RIGHT]

    def print_angles_report(self):
        """

        :return:
        """
        #defect_pts = Finger.get_defect_pts(self.fingers)
        finger_tips = Finger.get_finger_tips(self.fingers)

        axis = Vector(self.fingers[Finger.WRIST].palm_pt2, self.fingers[Finger.WRIST].tip)
        print self.get_angles_table(finger_tips, self.fingers[Finger.WRIST].tip, axis)

        print Hand.TABLE

    @staticmethod
    def get_angles_table(variable_pts, anchor_origin, anchor_axis):
        """

        :param variable_pts:
        :param anchor_origin:
        :param anchor_axis: Vector
        :return: str
        """

        angles = []
        to_string_lines = ["", "", ""]

        for index in range(len(variable_pts)):
            to_tip = Vector(variable_pts[index], anchor_origin)
            angle = Vector.angle_bw_two_vectors(anchor_axis, to_tip)

            angles.append(angle)

        for idx in range(len(angles)):
            to_string_lines[0] += "%03d  " % angles[idx]
            #to_string_lines[1] += "%02d    " % idx
            to_string_lines[1] += "%s    " % Finger.NAMES[idx]
            to_string_lines[2] += "-----"

        to_string_lines[2] += '\n'
        return "\n".join(to_string_lines)

    # Ask Chris how he did FRONT and BACK
    # Does it work for both right and left hand




