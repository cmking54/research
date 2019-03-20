import math
import cv2
import constants


# signed angle between two vector
#http://johnblackburne.blogspot.com/2012/01/angle-between-two-vectors.html
#http://johnblackburne.blogspot.com/2012/05/angle-between-two-3d-vectors.html
#http://johnblackburne.blogspot.co.uk/2012/02/perp-dot-product.html

class Vector(object):

    def __init__(self, p1, p2=None):
        if p2 is None:
            self.x = p1.x
            self.y = p1.y
        else:
            self.x = p2.x - p1.x
            self.y = p2.y - p1.y


    def __str__(self):
        return "vec:", self.x, self.y

    def length(self):
        return math.sqrt(self.x * self.x + self.y * self.y)

    def extend(self, scalar):
        self.x = self.x * scalar
        self.y = self.y * scalar

    @staticmethod
    def get_angle_between(seg1, seg2):
        num = Vector.dot_product(seg1, seg2)
        dem = seg1.length() * seg2.length()

        left_of_eq = float(num)/dem
        return math.degrees(math.acos(left_of_eq))
    #    num = Point.dot_product(unique)
    #         dem = line_seg1.get_length() * line_seg2.get_length()
    #         left_of_eq = float(num)/dem
    #         return math.acos(left_of_eq)

    @staticmethod
    def angle_bw_two_vectors(v1, v2):
        dot_p = v1.dot(v2)
        perp_dot = Vector.perp_dot(v1, v2)
        #print "perp_dot/dot_p", perp_dot, "/", dot_p
        return math.degrees(math.atan2(perp_dot, dot_p))


    def dot(self, v2):
        """

        :return: float
        """
        return self.x * v2.x + self.y * v2.y

    def perp(self):
        """

        :return: Vector
        """
        return Vector(-self.y, self.x)

    @staticmethod
    def perp_dot(v1, v2):
        """
        :param v1: Vector
        :param v2: Vector
        :return: float
        """
        #perp_v1 = v1.perp()
        #return perp_v1.dot(v2)
        #  inline version
        return v1.x * v2.y - v1.y * v2.x

    @staticmethod
    def dot_product(v1, v2):
        """

         :param v1: Point representing a vec
         :param v2: Point representing a vec
         :return: float, a scalar
        """
        return v1.x * v2.x + v1.y * v2.y
        # new_v1 = Vector(v1)
        # new_v1.extend(1.0/v1.length())
        # new_v2 = Vector(v2)
        # new_v2.extend(1.0/v2.length())
        # return new_v1.x * new_v2.x + new_v1.y * new_v2.y #) / (v1_length * v2_length)



class Point(object):
    X = 0
    Y = 1

    def __init__(self, *args):
        data = self.handle_init_input(args)
#       data = Point.handle_init_input(args)
        self.x = data[Point.X]
        self.y = data[Point.Y]

    def handle_init_input(self, args):
        if len(args) == 2:
            return args
        elif len(args) == 1:
            if not isinstance(args[0], self.__class__) and len(args[0]) == 1:
                return args[0][0]
        return args[0]

#  Ask Chris: instead of above... am I missing something?
    # @staticmethod
    # def handle_init_input(args):
    #     if len(args) == 2:
    #         return args
    #     elif len(args) == 1:
    #         if not isinstance(args[0], Point.__class__) and len(args[0]) == 1:
    #             return args[0][0]
    #     return args[0]

    def __str__(self):
        return "(%d, %d)" % self.get_tuple()

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.x == other.x and self.y == other.y
        return NotImplemented

    def __ne__(self, other):
        if isinstance(other, self.__class__):
            return not self.__eq__(other)
        return NotImplemented

    def __getitem__(self, item):
        if isinstance(item, int):
            if item == Point.X:
                return self.x
            elif item == Point.Y:
                return self.y
            else:
                return NotImplemented
        return NotImplemented

    def get_tuple(self):
        return self.x, self.y

    def draw(self, img, color, size=constants.TINY_CIRCLE_SIZE):
        cv2.circle(img, (self.x, self.y), size, color, -1)

    def square_distance(self, other):
        return math.hypot(self.x-other.x, self.y-other.y)

    def is_first_farther(self, pt1, pt2):
        dist1 = self.square_distance(pt1)
        dist2 = self.square_distance(pt2)
        return dist1 > dist2

    @staticmethod
    def get_midpoint(pt1, pt2):
        return Point((pt1.x+pt2.x)/2, (pt1.y+pt2.y)/2)

    def near(self, pt, min_dist=constants.NEAR_DIST):
        if self == pt:
            return True

        if Point.distance(self, pt) < min_dist:
            return True
        return False




    @staticmethod
    def get_square_distance(a, b):
        if not isinstance(a, Point.__class__):
            a = Point(a)
        if not isinstance(b, Point.__class__):
            b = Point(b)

        return a.square_distance(b)

    @staticmethod
    def distance(a, b):
        return math.sqrt(Point.square_distance(a, b))

    @staticmethod
    def dot(p1, p2):
        """

         :param p1: Point representing a vec
         :param p2: Point representing a vec
         :return: float, a scalar
        """
        return p1.x * p2.x + p1.y * p2.y


    # #  TO ERASE: soon (triangle still call it)
    # @staticmethod
    # def create_vit_curve(point_array):
    #     ret_pts = []
    #
    #     for point in point_array:
    #         if not isinstance(point, Point.__class__):
    #             ret_pts += [Point(point)]
    #         else:
    #             ret_pts += [point]
    #
    #     return ret_pts


class Curve(object):

    def __init__(self, points):
        self.points = Curve.handle_init_input(points)

    #  in case the item are not points
    @staticmethod
    def handle_init_input(args):
        ret_pts = []

        for point in args:
            if not isinstance(point, Point.__class__):
                ret_pts += [Point(point)]
            else:
                ret_pts += [point]

        return list(ret_pts)

    # def __getitem__(self, item):
    #     if isinstance(item, int):
    #         return self.points[item]
    #     return NotImplemented

 #   def __getitem__(self, item): return self._list[item]
    def __delitem__(self, index):
        if isinstance(index, int) or isinstance(index, slice):
            del self.points[index]
        else:
           raise TypeError('Curve.__delitem__ index('+str(index)+') must '
                                                                  'be int/slice')



    def __setitem__(self, index, value):
        if isinstance(index, int) or isinstance(index, slice):
            self.points[index] = Point(value)
        else:
            raise TypeError('Curve.__setitem__ index('+str(index)+') must '
                                                                  'be int/slice')




    def __getitem__(self, index):
        if isinstance(index, int) or isinstance(index, slice):
            return self.points[index]
        else:
            raise TypeError('Curve.__getitem__ index('+str(index)+') must '
                                                                  'be int/slice')

    # def __contains__(self, item):
    #     return item in self.points


    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.points == other.points
        return NotImplemented


    def __len__(self):
        return len(self.points)

    def __str__(self):
        res = ""
        for idx in xrange(len(self)):
            res += str(idx) + ": " + str(self.points[idx]) + "\n"
        return res

    def __iter__(self):
        return iter(self.points)
    #
    # def get_points(self):
    #     return self.points
    def append(self, pts):
        for pt in pts:
            self.points += [pt]

    def insert(self, idx, pt):
        self.points.insert(idx, pt)

    #TODO: trouble if called and pt is not there
    def index(self, pt):
        #print "array\n", self

        if pt not in self.points:
            return -1

        return self.points.index(pt)

    def remove(self, idx):
        if isinstance(idx, int):
            del self.points[idx]

    def is_near(self, pt, min_dist=constants.NEAR_DIST):
        """

        :param pt:
        :param min_dist:
        :return: bool, int
        """
        #  False if self array of points neither include pt
        #            nor pt is close to any
        # alist = [1, 2, 3, 4]
        # if alist.__contains__(5):
        #     idx = [1,2,3,4].index(5)

        idx = -1
        if self.points.__contains__(pt):
            idx = self.points.index(pt)
            #print "EXACT", idx
            return True, idx
        #else:
        #    print "doesn't contain", str(pt)
        #    print "in\n", str(self)

        #for apt in self.points:
        for idx in range(len(self.points)):
            # smaller than 5 bw points = close by: is that right?
            #  use in defect in points.. in bw fingers
            #  see bug in log elodie1_in_out_defect_points_oriented_poly.html
            # (Frame 170: 12 and 14 points)
            dist = Point.distance(self.points[idx], pt)
            #print "dist", dist, self.points[idx], pt
            if dist < min_dist:
                #print "near", idx
                return True, idx

        return False, -1

    def orient(self, start, direction):
        """
        In place reorder of the array 0 is start
        :param start:
        :param direction:
        :return:
        """
        reorder_array = []
        loc = start
        for idx in xrange(len(self.points)):
            reorder_array.append(self.points[loc % len(self.points)])
            loc += direction
            #reorder_array.append(self.points[(start+direction*idx) % len(self.points)])
        self.points = reorder_array

    def index_first_in_common(self, defect_curve, start=0):
        """
        Use passing defect points
        :param defect_curve:
        :param start:
        :return: int, int (index in self and index of defect-- -1 for not found in the latter
        """

        loc = -1
        i = 0
        while i < len(self.points):
            pt = self.points[(i+start) % len(self.points)]
            found = pt in defect_curve
            if found:
                loc = defect_curve.index(pt)
                print loc
                return i + start, loc
            i += 1

        return i + start - 1, loc
        #     #print "curve", curve[(start+i) % len(curve)]
        #     found, loc = defects.is_near(curve[(start+i) % len(curve)])   # next defect
        #     print found, start+i
        #     if found:
        #         return start+i
        #     i += 1
        #
        # #print "no next defect"
        # return loc

    def draw(self, img, color, close=True, circle=False):
        for idx in xrange(len(self.points)-1):
            Curve.draw_line(img, color, self.points[idx], self.points[idx+1], circle)

        if close:
            Curve.draw_line(img, color,
                            self.points[len(self.points)-1],
                            self.points[0], circle)

        if circle:
            self.draw_points(img, color)

    def draw_points(self, img, color, size=constants.TINY_CIRCLE_SIZE, label=False, offset=0):

        for idx in xrange(len(self.points)):
            self.points[idx].draw(img, color, size)
            if label:
                ori = self.points[idx]
                cv2.putText(img, str(idx), (ori.x+offset, ori.y),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1, cv2.LINE_AA)

    def add_midpoint(self, idx):
        if 0 < idx < len(self.points):  # zero not inclusive
            self.insert(idx, Point.get_midpoint(self.points[idx - 1],
                                                self.points[idx]))
        else:
            print "mid-point problem"


    def insert_pts(self, close_by):
        """
        Insert the close_by points within the closest line segment found in self curve
        :param close_by: Curve
        :return: Curve
        """
        print "HOW many", len(close_by), "\n", close_by
        print "curve\n", self

        #until there is no more points to insert
        while len(close_by) > 0:
            pt = close_by[0]
            idx = self.closest_line(pt)
            # insert before the +1 index
            if idx != -1:
                print "Insert at", idx
                self.insert(idx+1, pt)
            close_by.remove(0)

    def farthest_point(self, center):
        """
        USE with PROMPT in_defect curve len(self) > 6
            remove farther away point from center of POLY
        :param center:
        :return:
        """
        loc = -1
        max_dist = -1
        for idx in xrange(len(self.points)):
            dist = center.square_distance(self.points[idx])
            if dist > max_dist:
                max_dist = dist
                loc = idx
        return loc

    def closest_line(self, pt):
        loc = -1
        min_dist = 1000000
        #print "closest"
        for idx in range(len(self.points)-1):

            dist = Curve.segment_square_distance(self.points[idx],
                                                 self.points[idx+1], pt)

            #print "intermediate", idx, dist, min_dist, loc
            if 0 <= dist < min_dist:
                loc = idx
                min_dist = dist

        #print "distance", min_dist, "location", loc
        return loc

    @staticmethod
    def triangle_area(alist):
        """

        :param alist:
        :return:
        """
        if not isinstance(alist, Curve.__class__):
            alist = Curve(alist)

        if len(alist) != 3:
            raise Exception()
        a, b, c = alist[0], alist[1], alist[2]
        return abs(a.x * b.y - a.y * b.x + a.y * c.x - a.x * c.y + b.x * c.y - c.x * b.y) / 2

    # consider adding min_dist
    @staticmethod
    def filter_different_pts(pts, other_pts):
        """
        Two curves that may have same or near points
        Return a curve made of the other_pts that are unique

        Does a second thing: other_pts change from near to exactly the same
        :param pts: Curve
        :param other_pts: Curve
        :return: Curve
        """
        unique = []
        #for pt in other_pts:
        for idx in xrange(len(other_pts)):
            pt = other_pts[idx]
            found, loc = pts.is_near(pt)
            if not found:
                unique += [pt]
            else:
                if idx == 0 or (idx > 1 and other_pts[idx-1] != pts[loc]):
                    other_pts[idx] = pts[loc]


        return Curve(unique)

    # from
    # http://www.randygaul.net/2014/07/23/distance-point-to-line-segment/
    # not best naming... with line instead of vec...
    @staticmethod
    def segment_square_distance(pt_a, pt_b, out_pt):
        """

        :param pt_a: end Point of line segment
        :param pt_b: end Point of line segment
        :param out_pt: Point that is projected to (ab)
        :return: float positive for square orthogonal distance in [ab]
                       -1 for outside [ab]
        """
        print "line", pt_a, pt_b
        print "point", out_pt

        line = Vector(pt_a, pt_b)
        line_pa = Vector(out_pt, pt_a)

        scalar = Vector.dot_product(line, line_pa)

        print "scalar", scalar, Vector.dot_product(line, line)
        if scalar > 0.0:
            return -1 # closest point is a

        line_pb = Vector(pt_b, out_pt)
        scalar2 = Vector.dot_product(line_pb, line)

        #print "scalar2", scalar2
        if scalar2 > 0.0:
            return -1 # closest point is a

        unit_dot = scalar / (Vector.dot_product(line, line) * 1.0) #essential to be FLOAT
        print unit_dot
        line.extend(unit_dot)

        print line.__str__()

        projx = line_pa.x - line.x
        projy = line_pa.y - line.y

        proj = Vector(Point(projx, projy))
        print "DISTANCE", math.sqrt(Vector.dot_product(proj, proj))
        return math.sqrt(Vector.dot_product(proj, proj))
        #proj = Vector(line, line_pa)
        #print "DISTANCE ", proj#Vector.dot_product(proj, proj)
        #return proj.length() #Vector.dot_product(proj, proj)

    # @staticmethod
    # def convert_np_array2curve(np_array):
    #     py_array = []
    #     for item in np_array:
    #         py_array += [item[0]]
    #     return Curve(py_array)

    @staticmethod
    def indices_of_lowest_horizontal(curve_pts, center, delta_y):
        """
        
        :param curve_pts: 
        :param center: 
        :param delta_y: 
        :return: int, int   indices in py_pts of the lowest horizontal
                            -1, -1 no line found
        """

        # list of points below the centroid
        below_centroid_indices = []
        #print "idx"
        for idx in range(len(curve_pts)):
            if curve_pts[idx].y > center.y:  # y_coord is below y_centroid
                below_centroid_indices += [idx]

        print "result", len(below_centroid_indices)

        # Assumptions: work for upright hand
        # does it work for front or facing hand, right or left (without knowing thumb location)
        if len(below_centroid_indices) >= 2:

            #  assume it is the first point
            extreme_indices = [below_centroid_indices[0]]
            similar_y = curve_pts[extreme_indices[0]].y

            for idx in range(1, len(below_centroid_indices)):
                t_idx = below_centroid_indices[idx]
                new_point = curve_pts[t_idx]
                new_y = new_point.y

                # first point in the filtered list, add the next one if closed by
                if abs(similar_y-new_y) < delta_y:
                    extreme_indices.append(t_idx)
                    similar_y = min(similar_y, new_y)
                #    print "find closeby point", t_idx

                # Otherwise points not close vertically,
                #    reset the current point is below the saved extreme
                else:
                    if new_y > similar_y:
                        print "reset with", t_idx, new_y
                        extreme_indices = [t_idx]
                        similar_y = new_y


            # Correction for wrist is only one point.
            # From observation take the last point of curve (special case starting at wrist end)
            dist = abs(curve_pts[extreme_indices[0]].y - curve_pts[extreme_indices[len(extreme_indices)-1]].y)
            if len(extreme_indices) == 1 and dist < delta_y:
                extreme_indices.append((extreme_indices[0]+1) % len(curve_pts))

            #print "length", len(extreme_indices)
            #print "delta Y at wrist", dist, extreme_indices[0], extreme_indices[len(extreme_indices)-1]

            # Found case:
            # Is it general to take the list first and last as assumed sequential horizontal pts
            return extreme_indices[0], extreme_indices[len(extreme_indices)-1]

        # Trouble case
        return -1, -1

    @staticmethod
    def draw_line(img, color, pt1, pt2, circle=False):
        pt1 = pt1.get_tuple()
        pt2 = pt2.get_tuple()

        cv2.line(img, pt1, pt2, color, 2)
        if circle:
            cv2.circle(img, pt1, 5, color, -1)
            cv2.circle(img, pt2, 5, color, -1)



