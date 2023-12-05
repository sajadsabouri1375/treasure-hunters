import numpy as np


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