from numpy import *
import numpy as np
np.seterr(divide='raise')


class VectorUtils:
    @staticmethod
    def find_unit_vector(vector):
        """
            Returns the unit vector of the vector.  
        """
        unit_vector = vector / np.linalg.norm(vector)
            
        if np.isnan(unit_vector).any():
            raise ZeroDivisionError
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
        
        try:
            da = a2-a1
            db = b2-b1
            dp = a1-b1
            dap = VectorUtils.perpare_line(da)
            denom = dot( dap, db)
            num = dot( dap, dp )
            intersection = (num / denom.astype(float))*db + b1
            return intersection
        except Exception as e:
            return None
    
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
        if (line_x_min <= point[0] <= line_x_max) and (line_y_min <= point[1] <= line_y_max):
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
    def are_poits_in_sight(point_01, point_02, blocks):
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