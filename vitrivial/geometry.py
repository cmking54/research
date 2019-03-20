import cv2
import constants
import numpy as np
from vit_math import Point
from vit_math import Curve
from finger import Finger


class Geometry:

    EX_BOTTOM = 0
    EX_RIGHT = 1
    EX_TOP = 2
    EX_LEFT = 3
    # convenient to consider BOXES as curve
    # is it efficient? or we are wasting resources

    #  POLY approx: start at the highest point it seems
    # (known from observation, not from documentation)

    def __init__(self, curve, t, center=None, area=None):
        self.curve = curve
        # TODO: check it is a Curve throughout;
        # GOAL: create_fingers version list of Point for 3 * 6
        self.poly_curve = None
        self.g_type = t
        self.belong_to_prompt = False

        self.pts_to_add = None

        self.perimeter = Geometry.init_perimeter(self.curve, self.g_type)
        if center is None:
            self.center = Geometry.compute_center_of_mass(self.curve)
        else:
            self.center = center

        if area is None:
            self.area = cv2.contourArea(self.curve)
        else: # could be done for tilted box as well
            self.area = area

    def draw(self, img):
        if constants.GEO_DRAW[self.g_type]:
            if self.g_type == constants.GEO_POLY and self.poly_curve is not None:
                self.poly_curve.draw(img, constants.COLOR_WHITE, close=True, circle=True)
                #pass
            else:
                cv2.drawContours(img, [self.curve], -1, constants.GEO_COLORS[self.g_type],
                                 constants.PEN_THICKNESS)

            if self.pts_to_add is not None:
                self.pts_to_add.draw_points(img, constants.COLOR_GREEN)

    def get_height(self):
        _, _, _, height = cv2.boundingRect(self.curve)
        return height

    def __str__(self):
        astring = "Type " + constants.GEO_NAMES[self.g_type] + \
                  " Length " + str(len(self.curve)) + "\n"
        astring += "\t\tCenter " + str(self.center) + "\n"
        astring += "\t\tArea " + str(self.area) + "\n"
        astring += "\t\tPerimeter " + str(self.perimeter) + "\n"
        astring += "\t\tPrompt " + str(self.belong_to_prompt) + "\n\n"
        return astring

    @staticmethod
    def append_bounding_boxes(geo):
        """
        Supplement the contour, poly and hull computed initially (using create_geometries)
         with rigid geometries: tilted and axis-aligned bboxes)
        :param geo: Geometry list (POLY, CONTOUR, HULL)
        :return:
        """
        curve = geo[constants.GEO_POLY].curve
        #  be careful order
        geo.append(Geometry.create_tilted_box(curve))
        geo.append(Geometry.create_bounding_box(curve))
        return geo

    @staticmethod
    def create_tilted_box(curve):
        """
        Create the constants.GEO_TILTED_BOX geometry
        which is the minimum (rotated) rectangular area containing the curve
        GEO_TILTED_BOX is tighter than the GEO_BBOX created below
        :param curve: list of coordinates (tuple?)
        :return: Geometry object that is the tilted rectangle containing the curve
        """
        tilted_rect = cv2.minAreaRect(curve)
        # print type(tilted_rect), tilted_rect.__str__()  # to figure out the BBOX (down)
        # calculate coordinates of the minimum area rectangle
        # and normalize coordinates to integers
        tilted_box = np.int0(cv2.boxPoints(tilted_rect))
        return Geometry(tilted_box, constants.GEO_TILTED_BBOX, Point(tilted_rect[0]))

    @staticmethod
    def create_bounding_box(curve):
        """
        Create the constants.GEO_BBOX geometry
        which is the axis-aligned rectangular area containing the curve
        :param curve: list of coordinates to be contained
        :return: Geometry object that is the bounding rectangle of the curve
        """
        rect_x, rect_y, rect_w, rect_h = cv2.boundingRect(curve)
        #  Difference bw Rect using top-left corner and Box using the center
        # http://docs.opencv.org/2.4/modules/core/doc/old_basic_structures.html?
        #    ... highlight=cvbox2d#CvBox2D
        center = (rect_x + rect_w / 2.0, rect_y + rect_h / 2.0)
        # calculate coordinates for the bounding box
        box = cv2.boxPoints((center, (rect_w, rect_h), 0))
        # normalize coordinates to integers
        box = np.int0(box)
        return Geometry(box, constants.GEO_BBOX, Point(center), rect_w * rect_h)


    @staticmethod
    def init_perimeter(shape, t):
        # calculates a contour perimeter or a poly curve length
        # => fine for all (I think)  --may not be most efficient
        return cv2.arcLength(shape, True)

    @staticmethod
    def compute_center_of_mass(shape):
        m = cv2.moments(shape)
        cx = int(m['m10']/m['m00'])
        cy = int(m['m01']/m['m00'])
        return Point(cx, cy)

    @staticmethod
    # assumed g1 is the larger one
    def compute_areas_ratio(g1, g2):
        diff = g1.area - g2.area
        return diff * 100 / g2.area

    @staticmethod
    def align(curve, defects,  start_pt, next_pt, extreme_pt):
        # known index should not return -1
        poly_index1 = curve.index(start_pt)
        poly_index2 = curve.index(next_pt)
        opposite_to_thumb = extreme_pt.is_first_farther(curve[poly_index1], curve[poly_index2])
        #print "opposite", opposite_to_thumb

        direction = 1
        if opposite_to_thumb:
            # going CW towards thumb
            direction = -1
            curve.orient(poly_index1, direction=direction)
        else:
            curve.orient(poly_index2, direction=direction)

        # no point bw start_pt and next_pt: make sure wrist has three points
        if curve[1] == start_pt or curve[1] == next_pt:
            curve.add_midpoint(1)

        if len(curve) > Finger.PTS_LEN:
            _, first_defect = curve.index_first_in_common(defects, Finger.PTS_LEN)
            if first_defect != -1:
                # same orientation than poly WORKS
                defects.orient(first_defect, direction=direction)


    def create_poly_curve(self, defect_pts, start_pt, next_pt, extreme_pt):

        if self.g_type == constants.GEO_POLY:
            approx = Curve(self.curve)
            #print "length before", len(approx)
            # TODO: very small d for fist
            # TODO: FIX BUG
            self.pts_to_add = Curve.filter_different_pts(approx, defect_pts)

            # copy to display
            pts_to_add = Curve(self.pts_to_add)
            approx.insert_pts(pts_to_add)

            # orient curve wrt param points (wrist and thumb)
            #self.poly_curve = \
            Geometry.align(approx, defect_pts, start_pt, next_pt, extreme_pt)
            self.poly_curve = approxukanT1/2t00


            #print "length after", len(self.poly_curve)

    #  is it needed??



    @staticmethod
    def find_extremes(c):
        #c = max(cnts, key=cv2.contourArea)
        ext_left = tuple(c[c[:, :, 0].argmin()][0])
        ext_right = tuple(c[c[:, :, 0].argmax()][0])
        ext_top = tuple(c[c[:, :, 1].argmin()][0])
        ext_bot = tuple(c[c[:, :, 1].argmax()][0])
        return [Point(ext_bot), Point(ext_right), Point(ext_top), Point(ext_left)]

    # @staticmethod
    # def draw_extremes(image, extremes, size=5, color=None):
    #     pass
    #
    # #cv2.drawContours(image, [c], -1, (0, 255, 255), 2)
    # cv2.circle(image, extLeft, 8, (0, 0, 255), -1)
    # cv2.circle(image, extRight, 8, (0, 255, 0), -1)
    # cv2.circle(image, extTop, 8, (255, 0, 0), -1)
    # cv2.circle(image, extBot, 8, (255, 255, 0), -1)
    #
    # if color is not None:
    #     cv2.circle(image, extLeft, 4, color, -1)
    #     cv2.circle(image, extRight, 4, color, -1)
    #     cv2.circle(image, extTop, 4, color, -1)
    #     cv2.circle(image, extBot, 4, color, -1)

    # @staticmethod
    # def convert_array_py2np(py_array):
    #     np_array = np.array([[[None, None]]])
    #     # place = 1
    #     for item in py_array:
    #         inner_1 = np.array([[item]])
    #         # inner_2 = np.array([inner_1])
    #         # print inner_2
    #         # print 'gdf', item
    #         # print np_array.shape, inner_1.shape
    #         np_array = np.append(np_array, inner_1, axis=0)
    #         # place += 1
    #     # print 'dfsf', np_array
    #     #print 'cast', np_array[1:,]
    #     #print
    #     return np_array[1:, ]