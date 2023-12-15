from numpy import *
import numpy as np
# np.seterr(divide='raise')
np.seterr(all='raise')


class VectorUtils:
    @staticmethod
    def find_unit_vector(vector):
        """
            Returns the unit vector of the vector.  
        """
        
        if vector is None:
            return vector
        
        try:
            unit_vector = vector / np.linalg.norm(vector)
        except:
            return None
        
        return unit_vector
    
    @staticmethod
    def find_angle_between_two_vectors(vector_1, vector_2):
        """ 
            Returns the angle in radians between vectors 'v1' and 'v2'
        """
        
        try:
            unit_vector_1 = VectorUtils.find_unit_vector(vector_1)
            unit_vector_2 = VectorUtils.find_unit_vector(vector_2)
            return np.arccos(np.clip(np.dot(unit_vector_1.ravel(), unit_vector_2.ravel()), -1.0, 1.0))
        
        except ZeroDivisionError:
            return 0

        except AttributeError:
            return 0
        
    @staticmethod
    def find_vector_angle(vector):
        return VectorUtils.find_angle_between_two_vectors(vector, np.array([1,0]).reshape(1,-1))
    
    @staticmethod
    def find_angle_vector(angle):
        return VectorUtils.find_unit_vector(np.array([np.cos(angle), np.sin(angle)]).reshape(1, -1))
    
    @staticmethod
    def perpare_line(a) :
        b = empty_like(a)
        b[0] = -a[1]
        b[1] = a[0]
        return b

    def find_segment_intersect(a1, a2, b1, b2) :
        
        # da = a2-a1
        # db = b2-b1
        # dp = a1-b1
        # dap = VectorUtils.perpare_line(da)
        # denom = dot(dap, db)
        # num = dot(dap, dp )
        # intersection = (num / denom.astype(float))*db + b1
    
        try:
            m1 = (a2[1] - a1[1]) / (a2[0] - a1[0])
        except:
            m1 = np.inf
        
        try:
            m2 = (b2[1] - b1[1]) / (b2[0] - b1[0])
        except:
            m2 = np.inf
        
        if m1 == np.inf:
            intercept1 = np.inf
        else:
            intercept1 = a1[1] - m1 * a1[0]
            
        if m2 == np.inf:
            intercept2 = np.inf
        else:
            intercept2 = b1[1] - m2 * b1[0]
        
        if m1 != np.inf and m2 != np.inf:
            
            if m1 == m2:
                return None
            
            else:
                x_intersection = (intercept2 - intercept1) / (m1 - m2)
                y_intersection = m1 * x_intersection + intercept1
            
        elif m1 == np.inf and m2 != np.inf:
            x_intersection = a1[0]
            y_intersection = m2 * x_intersection + intercept2
        
        elif m1 != np.inf and m2 == np.inf:
            x_intersection = b1[0]
            y_intersection = m1 * x_intersection + intercept1
        
        elif m1 == np.inf and m2 == np.inf:
            return None
        
        intersection = np.array(
            [
                x_intersection,
                y_intersection
            ]
        )

        return intersection
    
    @staticmethod
    def find_lines_intersection(line_01, line_02):
        # These may need to ravel
        start_01 = line_01[0].ravel()
        end_01 = line_01[1].ravel()
        start_02 = line_02[0].ravel()
        end_02 = line_02[1].ravel()
        
        return VectorUtils.find_segment_intersect(start_01, end_01, start_02, end_02)
    
    @staticmethod
    def is_point_on_part_line(line, point):
        line_point_01 = line[0].ravel()
        line_point_02 = line[1].ravel()
        point = point.ravel()
        line_x_min = min(line_point_01[0], line_point_02[0])
        line_x_max = max(line_point_01[0], line_point_02[0])
        line_y_min = min(line_point_01[1], line_point_02[1])
        line_y_max = max(line_point_01[1], line_point_02[1])
        
        
        if ((point[0] - line_x_min) >= -0.0000001) and ((line_x_max - point[0]) >= -0.0000001) and ((point[1] - line_y_min) >= -0.0000001) and ((line_y_max - point[1]) >= -0.0000001):
            return True

        return False
               
    @staticmethod
    def find_part_lines_intersection(line_01, line_02):
        intersection = VectorUtils.find_lines_intersection(line_01, line_02)
        
        if intersection is None:
            return None
        
        if VectorUtils.is_point_on_part_line(line_01, intersection) and VectorUtils.is_point_on_part_line(line_02, intersection):
            return intersection
        
        return None
    
    @staticmethod
    def find_distance_between_two_points(point_01, point_02):
        return np.linalg.norm(point_01-point_02)

    @staticmethod
    def are_points_in_sight(point_01, point_02, blocks):
        reaching_line = [
            point_01,
            point_02
        ]
        
        return all(
            [
                VectorUtils.find_part_lines_intersection(
                    reaching_line,
                    block
                ) is None
                for block in blocks
            ]
        )