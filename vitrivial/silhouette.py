import cv2
import constants
from hand import Hand
from geometry import Geometry
from algo_class import AlgoClass
from vit_math import Point
from vit_math import Curve


class Silhouette(AlgoClass):
    """
       Object grouping the features of a contour
       + Class methods = utils functions for contour computations
    """

    areas = []

    # log images for easy access during visual debugging
    log_all_geometries = None

    # log_all_approx = None
    # log_all_bboxes = None



    def __init__(self, img, geo):  # img, c):
        """

        :param img: masked image revealing all the regions that are silhouette candidates
        :param geo: list of the first three Geometry objects [POLY, CONTOUR, HULL] (complex ones)
                Stored in increasing order of areas
                 - POLY: a lower handle_init_input-lines approximation (not tight enough)
                 - CONTOUR: curve joining all the continuous points--along the boundary--
                 having the same color/intensity
                 - HULL: convex hull points
                onion_geometry supplements geo param by adding the tilted and bounding boxes
                ORDER IS ESSENTIAL in the onion_geometry
        """
        AlgoClass.__init__(self)

        self.masked_img = img
        self.onion_geometry = Geometry.append_bounding_boxes(geo)
        self.shape_like = self.geo_area_ratio_similarity()
        Silhouette.log_all_geometries = self.masked_img

    def draw_all(self, img=None):
        if img is None:
            img = self.masked_img

        for idx in range(len(self.onion_geometry)):
            self.onion_geometry[idx].draw(img)

    def log_all(self):
        for idx in range(len(self.onion_geometry)):
            result = str(self.onion_geometry[idx])
            self.log_text(result)

    @staticmethod
    # consider generalization to specific sized contours, i.e. in range
    #  0 to max for STAGE1 hands; body increasing as closer (proportion of the image)
    def get_contours(masked_img, min_size=constants.CONTOURS_MIN_AREA):
        """
        :param masked_img:
        :param min_size:
        :return:
        """
        img_gray = cv2.cvtColor(masked_img, cv2.COLOR_BGR2GRAY)
        contours = Silhouette.cv_find_contours(img_gray)
        large_contours = []

        for c in contours:
            area = cv2.contourArea(c)
            if area > min_size:
                large_contours += [c]

        return large_contours

    @staticmethod
    def create_geometries(img, contours):
        """
        :return:
        """

        silhouettes = []

        for curve in contours:
            g_contour = Geometry(curve, constants.GEO_CONTOUR)

            #  TO DO: investigate the 0.01 precision of the contour approx
            #          (set out of luck right now)
            #  much more pts (alternative to defects?)
            # epsilon = 0.001 * cv2.arcLength(curve, True)
            epsilon = 0.01 * cv2.arcLength(curve, True)
            poly = cv2.approxPolyDP(curve, epsilon, closed=True)
            g_poly = Geometry(poly, constants.GEO_POLY)

            hull = cv2.convexHull(poly)
            g_hull = Geometry(hull, constants.GEO_HULL)

            silhouettes += [Silhouette(img, [g_poly, g_contour, g_hull])]

        return silhouettes

    @staticmethod
    def select_hand_like(silhs):
        """

        :param silhs:
        :return:
        """
        if Hand.PREVIOUS_PROMPT is not None:
            return Silhouette.find_closest_to_previous(
                silhs, Hand.PREVIOUS_PROMPT.onion_geometry[constants.GEO_BBOX])
        else:
            return Silhouette.find_among_others(silhs)

    @staticmethod
    def find_closest_to_previous(silhs, geo):
        """

        :param silhs:
        :param geo:
        :return:
        """

        # comparison point
        previous_hand_center = geo.center
        # assuming first is closest
        closest = 0
        min_dist = Point.get_square_distance(previous_hand_center,
                                             silhs[closest].onion_geometry[constants.GEO_BBOX].center)
        for idx in range(1, len(silhs)):
            next_center = silhs[idx].onion_geometry[constants.GEO_BBOX].center

            new_dist = Point.get_square_distance(previous_hand_center, next_center)
            if new_dist < min_dist:
                closest = idx

        return silhs[closest]

    @staticmethod
    #  assuming when there is at least one HAND and something else (such as a face)
    #  and PROMPT has not been found
    def find_among_others(silhs):
        """

        :param silhs:
        :return: a silhouette object
        """

        for a_silh in silhs:

            if len(silhs) > 1 and Hand.PREVIOUS_PROMPT is None:
                if a_silh.shape_like == Hand.PROMPT:
                    a_silh.onion_geometry[constants.GEO_POLY].belong_to_prompt = True
                    if Silhouette.are_geo_centers_distinct(a_silh.onion_geometry):
                        return a_silh
                        # should perimeters also be compared

        return None

    # def set_similarity(self):
    #
    #     if Silhouette.geo_area_ratio_similarity(self.onion_geometry):
    #         return Silhouette.PROMPT
    #     else:
    #         return Silhouette.OTHER

    def geo_area_ratio_similarity(self):
        """
        hull and poly ratio area is considered as a signature of
           - prompt hand (and opened hand)
           - fist (close hand) / or face initially

        :param onion:
        :return:
        """
        onion = self.onion_geometry
        ratio = Geometry.compute_areas_ratio(onion[constants.GEO_HULL],
                                             onion[constants.GEO_POLY])

        # print "area ratio", ratio

        if ratio < constants.GEO_AREA_RATIO_CLOSE:  # such as the face when differentiating
            # at the beginning (no PROMPT found)
            return Hand.FIST  # False
        elif constants.GEO_AREA_RATIO_PROMPT_MAX > ratio > constants.GEO_AREA_RATIO_PROMPT_MIN:
            return Hand.PROMPT  # True
        return Hand.OTHER  # False

    @staticmethod
    def are_geo_centers_distinct(onion):
        """
        the centers with one off form a triangle (not true for Chris' hand)
        :param onion:
        :return:
        """
        area = Curve.triangle_area([onion[constants.GEO_HULL].center,
                                    onion[constants.GEO_POLY].center,
                                    onion[constants.GEO_BBOX].center])
        # print "area", area
        min_prop = onion[constants.GEO_HULL].area / constants.GEO_CENTERS_AREA_PROMPT_GREATER
        max_prop = onion[constants.GEO_HULL].area / constants.GEO_CENTERS_AREA_PROMPT_SMALLER

        # print "min", min_prop, "max", max_prop
        if max_prop > area > min_prop:
            # print area
            return True
        return False

    @staticmethod
    def find_defect_pts(curve):
        """
        in = are far of the curve
                in bw fingers defect points;
        out = are close to the curve (usually HULL)
                wrist and finger tips
        :param curve (contour)
        :return: Curve, Curve
        """
        def format_defect_info(defect):
            f_s, f_e, f_f, fixpt_depth = defect
            # convexityDefects 4th element integer, 'fixpt_depth' fixed-point approximation
            # (with 8 fractional bits) of the distance bw farthest contour point and the hull.
            #    - to get floating-point value of depth --> fixpt_depth/256.0
            return Point(curve[f_s][0]), Point(curve[f_e][0]), Point(curve[f_f][0]), \
                   fixpt_depth / 256.0

        #  hull_indices (not the earlier hull):
        #         returnPoints is False so that indices (not coord) are returned
        hull_indices = cv2.convexHull(curve, clockwise=False, returnPoints=False)
        defects = cv2.convexityDefects(curve, hull_indices)
        inside_defect_pts = []
        outside_defect_pts = []
        for i in range(defects.shape[0]):
            start, end, far, depth = format_defect_info(defects[i, 0])
            # print "depth", depth
            if depth > 2:
                inside_defect_pts += [far]
            else:
                outside_defect_pts += [far]

        return Curve(inside_defect_pts), Curve(outside_defect_pts)

    @staticmethod
    def get_defect_pts(geo, shape): #curve):
        """
        Process contour to find both type of defects.
        Filter the in_defects
        :param geo:
        :param shape:
        :return:
        """
        curve = geo.curve
        in_defects, out_defects = Silhouette.find_defect_pts(curve)

        if shape == Hand.PROMPT:
            Silhouette.remove_false_in_defects(in_defects, geo.center)

        return in_defects, out_defects

    @staticmethod
    def remove_false_in_defects(defects, center):
        """
        Open hand may have BAD in_defect that are far at extremity
            - farther than other inner -> THUMB extreme
            - near by the HULL
        :param defects: Curve -> modified
        :param center:
        :return:
        """

        print "defect", len(defects)

        while len(defects) > 6:
            loc = defects.farthest_point(center)
            print "remove a defect", loc
            if loc != -1:
                defects.remove(loc)

        print "defect after", len(defects)

    @staticmethod
    def cv_find_contours(img_gray):
        """
        USE instead of cv2.findContours as it resolves return conflicts of CV2 and CV3
        http://www.pyimagesearch.com/2015/08/10/checking-your-opencv-version-using-python/

        :param img_gray: gray (single channel) source image
        :return: a list of all the contours in the image
        Each individual contour is a Numpy array of (x,y) coordinates of boundary points
        """
        # check if using OpenCV 3
        if constants.CV3:
            (_, contours, _) = cv2.findContours(img_gray.copy(), cv2.RETR_EXTERNAL,
                                                cv2.CHAIN_APPROX_SIMPLE)
        else:
            (contours, _) = cv2.findContours(img_gray.copy(), cv2.RETR_TREE,
                                             cv2.CHAIN_APPROX_SIMPLE)

        return contours
