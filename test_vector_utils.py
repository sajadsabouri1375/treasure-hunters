import unittest
from vector_utils import VectorUtils
import numpy as np


class TestVectorUtils(unittest.TestCase):

    def test_find_unit_vector(self):
        vector = np.array([1,1]).reshape(1, -1)
        unit_vector = VectorUtils.find_unit_vector(vector)
        self.assertEqual(round(np.sqrt(2)/2, 5), round(unit_vector[0,0], 5))
        self.assertEqual(round(np.sqrt(2)/2, 5), round(unit_vector[0,1], 5))

    def test_find_angle_between_two_vectors(self):
        vector_1 = np.ones((1,2))
        vector_2 = np.ones((1,2)) * -1
        angle = VectorUtils.find_angle_between_two_vectors(vector_1, vector_2)
        self.assertEqual(np.round(np.pi, 5), np.round(angle, 5))
        
if __name__ == '__main__':
    unittest.main()